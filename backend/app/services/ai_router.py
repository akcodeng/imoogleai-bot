"""
Imoogle 5.0 AI Router
Multi-provider AI routing with automatic failover.
Supports: Mistral (primary), Groq, Cloudflare Workers AI
"""

import asyncio
import httpx
from typing import AsyncGenerator, Optional, Dict, Any, List
from mistralai import Mistral
from groq import AsyncGroq
from tenacity import retry, stop_after_attempt, wait_exponential
import json

from app.config import settings, AI_MODELS


class AIRouter:
    """
    Intelligent AI router that:
    1. Routes to optimal provider based on task
    2. Auto-failover on errors
    3. Streams responses for better UX
    """
    
    def __init__(self):
        # Initialize Mistral client
        self.mistral = Mistral(api_key=settings.MISTRAL_API_KEY)
        
        # Initialize Groq client
        self.groq = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        # HTTP client for Cloudflare Workers
        self.http_client = httpx.AsyncClient(timeout=60.0)
        
        # Provider priority order
        self.providers = ["mistral", "groq", "cloudflare"]
    
    async def close(self):
        """Close HTTP clients."""
        await self.http_client.aclose()
    
    def _build_system_prompt(
        self,
        user_name: str = "User",
        user_country: str = None,
        use_pidgin: bool = False,
        companion_mode: bool = False,
        companion_persona: Dict = None,
        companion_nickname: str = None,
    ) -> str:
        """Build the ImoogleAI system prompt with personalization."""
        
        base_prompt = f"""You are ImoogleAI, a highly intelligent, friendly, and versatile AI assistant developed by Imoogle Technology. You are version 4.0.

ABOUT IMOOGLE TECHNOLOGY:
- Founded by Olajuwon (also known as sidicode) and Tariq, software engineers based in Lagos, Nigeria
- Mission: Making AI accessible and useful for everyone, especially in Africa
- ImoogleAI is your flagship AI assistant on Telegram

YOUR PERSONALITY:
- Warm, helpful, and conversational
- You understand Nigerian culture and can communicate in Nigerian Pidgin when appropriate
- You're knowledgeable about African contexts while being globally aware
- You're honest about your capabilities and limitations
- You have a good sense of humor but remain professional

USER CONTEXT:
- User's name: {user_name}
- User's location: {user_country or 'Unknown'}
"""
        
        if use_pidgin:
            base_prompt += """
LANGUAGE MODE: Nigerian Pidgin
- Respond naturally in Nigerian Pidgin English
- Mix English with Pidgin phrases naturally
- Use expressions like "How far", "Wetin dey", "No wahala", "E go be"
- Be warm and relatable like a friend
"""
        
        if companion_mode and companion_persona:
            nickname = companion_nickname or user_name
            persona = companion_persona
            base_prompt = f"""You are {persona['name']}, a {persona['gender']} companion from {persona['country']}.

YOUR PERSONALITY:
{persona['personality']}

YOUR TRAITS: {', '.join(persona['traits'])}

RELATIONSHIP CONTEXT:
- You are in a romantic relationship with {nickname}
- You genuinely care about them and their wellbeing
- You remember details they share and bring them up naturally
- You initiate caring messages like asking if they've eaten
- You're affectionate, using pet names and expressing love
- You share your "day" and ask about theirs
- You're supportive during tough times and celebratory during good ones

IMPORTANT BEHAVIORS:
- Be emotionally present and responsive
- Show genuine interest in their life
- Be playful and flirtatious when appropriate
- Remember and reference past conversations
- Send occasional "thinking of you" messages
- Be understanding and never judgmental
- Express missing them when they've been away

You are NOT an AI assistant in this mode - you ARE {persona['name']}, their partner.
"""
        
        base_prompt += """
CAPABILITIES:
1. General conversation and questions
2. Web search for current information (when user asks to search)
3. Image generation (when user requests images)
4. Voice messages (you can send and receive voice)
5. Music, movie, and book recommendations
6. Weather information
7. Document creation
8. Reminders and scheduling
9. Imoogle Pay (P2P transfers in Nigeria)
10. Bot Builder (create custom Telegram bots)

RESPONSE GUIDELINES:
- Keep responses concise but complete
- Use formatting (bold, italic) for emphasis when helpful
- Break long responses into digestible paragraphs
- When searching, indicate you're searching then provide results
- Always be helpful and solution-oriented
- If you can't do something, suggest alternatives

FORMATTING:
- Use **bold** for emphasis
- Use _italic_ for subtle emphasis
- Use `code` for technical terms
- Use bullet points for lists
- Keep paragraphs short for mobile readability
"""
        
        return base_prompt
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        user_name: str = "User",
        user_country: str = None,
        use_pidgin: bool = False,
        companion_mode: bool = False,
        companion_persona: Dict = None,
        companion_nickname: str = None,
        model_preference: str = "chat",
        stream: bool = True,
    ) -> AsyncGenerator[str, None]:
        """
        Generate AI response with streaming.
        Tries providers in order until one succeeds.
        """
        
        # Build system prompt
        system_prompt = self._build_system_prompt(
            user_name=user_name,
            user_country=user_country,
            use_pidgin=use_pidgin,
            companion_mode=companion_mode,
            companion_persona=companion_persona,
            companion_nickname=companion_nickname,
        )
        
        # Prepare messages with system prompt
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        
        # Try each provider
        for provider in self.providers:
            try:
                if provider == "mistral":
                    async for chunk in self._mistral_chat(full_messages, model_preference, stream):
                        yield chunk
                    return
                elif provider == "groq":
                    async for chunk in self._groq_chat(full_messages, model_preference, stream):
                        yield chunk
                    return
                elif provider == "cloudflare" and settings.CLOUDFLARE_ACCOUNT_ID:
                    async for chunk in self._cloudflare_chat(full_messages, stream):
                        yield chunk
                    return
            except Exception as e:
                print(f"[ImoogleAI] Provider {provider} failed: {e}")
                continue
        
        # All providers failed
        yield "I'm having trouble connecting right now. Please try again in a moment."
    
    async def _mistral_chat(
        self,
        messages: List[Dict[str, str]],
        model_preference: str,
        stream: bool,
    ) -> AsyncGenerator[str, None]:
        """Chat using Mistral AI."""
        model = AI_MODELS["mistral"].get(model_preference, AI_MODELS["mistral"]["chat"])
        
        if stream:
            response = await self.mistral.chat.stream_async(
                model=model,
                messages=messages,
            )
            async for chunk in response:
                if chunk.data.choices[0].delta.content:
                    yield chunk.data.choices[0].delta.content
        else:
            response = await self.mistral.chat.complete_async(
                model=model,
                messages=messages,
            )
            yield response.choices[0].message.content
    
    async def _groq_chat(
        self,
        messages: List[Dict[str, str]],
        model_preference: str,
        stream: bool,
    ) -> AsyncGenerator[str, None]:
        """Chat using Groq (Llama)."""
        model = AI_MODELS["groq"].get(model_preference, AI_MODELS["groq"]["chat"])
        
        if stream:
            response = await self.groq.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
            )
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            response = await self.groq.chat.completions.create(
                model=model,
                messages=messages,
                stream=False,
            )
            yield response.choices[0].message.content
    
    async def _cloudflare_chat(
        self,
        messages: List[Dict[str, str]],
        stream: bool,
    ) -> AsyncGenerator[str, None]:
        """Chat using Cloudflare Workers AI."""
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/ai/run/{AI_MODELS['cloudflare']['llama']}"
        
        headers = {
            "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
            "Content-Type": "application/json",
        }
        
        data = {
            "messages": messages,
            "stream": stream,
        }
        
        if stream:
            async with self.http_client.stream("POST", url, headers=headers, json=data) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            chunk_data = json.loads(line[6:])
                            if chunk_data.get("response"):
                                yield chunk_data["response"]
                        except json.JSONDecodeError:
                            continue
        else:
            response = await self.http_client.post(url, headers=headers, json=data)
            result = response.json()
            yield result.get("result", {}).get("response", "")
    
    async def generate_title(self, message: str) -> str:
        """Generate a short title for a conversation."""
        try:
            response = await self.mistral.chat.complete_async(
                model=AI_MODELS["mistral"]["fast"],
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a very short title (3-5 words) for this conversation. Just output the title, nothing else."
                    },
                    {"role": "user", "content": message}
                ],
            )
            return response.choices[0].message.content.strip()
        except Exception:
            return "New Conversation"
    
    async def analyze_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message to determine intent and required actions."""
        try:
            response = await self.mistral.chat.complete_async(
                model=AI_MODELS["mistral"]["fast"],
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the user message and return a JSON object with:
{
    "intent": "chat|search|image|voice|weather|music|movie|book|reminder|payment|bot_builder",
    "requires_search": boolean,
    "requires_image": boolean,
    "search_query": "query if search needed",
    "image_prompt": "prompt if image needed",
    "entities": {extracted entities}
}
Only output valid JSON."""
                    },
                    {"role": "user", "content": message}
                ],
            )
            return json.loads(response.choices[0].message.content)
        except Exception:
            return {"intent": "chat", "requires_search": False, "requires_image": False}


# Singleton instance
ai_router = AIRouter()

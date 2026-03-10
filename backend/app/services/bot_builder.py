"""
Imoogle 5.0 Bot Builder Service
Let users create and manage their own AI-powered Telegram bots.
"""

import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.config import settings, SUBSCRIPTION_PLANS
from app.database.models import User, UserBot, BotStatus


# Bot Builder pricing (monthly in Naira)
BOT_PLANS = {
    "starter": {
        "name": "Starter Bot",
        "price": 1500,
        "ai_messages_per_day": 100,
        "enable_web_search": False,
        "enable_image_gen": False,
        "custom_personality": True,
        "auto_responses": 10,
        "group_support": False,
    },
    "business": {
        "name": "Business Bot",
        "price": 2600,
        "ai_messages_per_day": 500,
        "enable_web_search": True,
        "enable_image_gen": False,
        "custom_personality": True,
        "auto_responses": 50,
        "group_support": True,
    },
    "premium": {
        "name": "Premium Bot",
        "price": 5000,
        "ai_messages_per_day": -1,  # Unlimited
        "enable_web_search": True,
        "enable_image_gen": True,
        "custom_personality": True,
        "auto_responses": -1,  # Unlimited
        "group_support": True,
        "priority_support": True,
    },
    "enterprise": {
        "name": "Enterprise Bot",
        "price": 10000,
        "ai_messages_per_day": -1,
        "enable_web_search": True,
        "enable_image_gen": True,
        "custom_personality": True,
        "auto_responses": -1,
        "group_support": True,
        "priority_support": True,
        "custom_branding": True,
        "api_access": True,
    },
}


class BotBuilderService:
    """
    Bot Builder service allowing users to create their own Telegram bots.
    Features:
    1. Easy bot creation with custom personality
    2. AI-powered responses using ImoogleAI
    3. Auto-responses for common questions
    4. Group moderation capabilities
    5. Analytics and stats
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=30.0)
        self.telegram_api = "https://api.telegram.org"
    
    async def close(self):
        await self.http_client.aclose()
    
    async def verify_bot_token(self, token: str) -> Dict[str, Any]:
        """Verify a Telegram bot token and get bot info."""
        try:
            response = await self.http_client.get(
                f"{self.telegram_api}/bot{token}/getMe"
            )
            data = response.json()
            
            if data.get("ok"):
                bot_info = data["result"]
                return {
                    "valid": True,
                    "username": bot_info.get("username"),
                    "first_name": bot_info.get("first_name"),
                    "can_join_groups": bot_info.get("can_join_groups", False),
                    "can_read_all_group_messages": bot_info.get("can_read_all_group_messages", False),
                }
            else:
                return {"valid": False, "error": data.get("description", "Invalid token")}
        
        except Exception as e:
            return {"valid": False, "error": str(e)}
    
    async def create_bot(
        self,
        db: AsyncSession,
        owner_id: int,
        bot_token: str,
        bot_name: str,
        system_prompt: str = None,
        welcome_message: str = None,
        personality: str = "professional",
        plan: str = "starter",
    ) -> Dict[str, Any]:
        """Create a new user bot."""
        # Check user's subscription allows bot creation
        result = await db.execute(select(User).where(User.id == owner_id))
        user = result.scalar_one_or_none()
        
        if not user:
            return {"success": False, "error": "User not found"}
        
        # Check if user tier allows bot builder
        user_plan = SUBSCRIPTION_PLANS.get(user.tier.value, {})
        if not user_plan.get("bot_builder", False):
            return {
                "success": False,
                "error": "Your subscription doesn't include Bot Builder. Upgrade to Pro or Business plan."
            }
        
        # Verify the bot token
        verification = await self.verify_bot_token(bot_token)
        if not verification["valid"]:
            return {"success": False, "error": f"Invalid bot token: {verification['error']}"}
        
        # Check if bot already exists
        existing = await db.execute(
            select(UserBot).where(UserBot.bot_token == bot_token)
        )
        if existing.scalar_one_or_none():
            return {"success": False, "error": "This bot is already registered"}
        
        # Create the bot
        user_bot = UserBot(
            owner_id=owner_id,
            bot_token=bot_token,
            bot_username=verification["username"],
            bot_name=bot_name,
            system_prompt=system_prompt or self._default_system_prompt(bot_name, personality),
            welcome_message=welcome_message or self._default_welcome_message(bot_name),
            personality=personality,
            plan=plan,
            status=BotStatus.ACTIVE,
            expires_at=datetime.now() + timedelta(days=30),
        )
        
        db.add(user_bot)
        await db.commit()
        await db.refresh(user_bot)
        
        # Set webhook for the bot
        webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/userbot/{user_bot.id}"
        await self._set_webhook(bot_token, webhook_url)
        
        return {
            "success": True,
            "bot_id": user_bot.id,
            "username": verification["username"],
            "name": bot_name,
            "plan": plan,
            "expires": user_bot.expires_at.strftime("%Y-%m-%d"),
        }
    
    def _default_system_prompt(self, bot_name: str, personality: str) -> str:
        """Generate default system prompt based on personality."""
        personalities = {
            "professional": f"""You are {bot_name}, a professional and helpful AI assistant.
Be concise, accurate, and business-like in your responses.
Help users with their questions efficiently and politely.""",
            
            "friendly": f"""You are {bot_name}, a friendly and approachable AI assistant.
Be warm, conversational, and helpful. Use a casual but respectful tone.
Make users feel comfortable and supported.""",
            
            "funny": f"""You are {bot_name}, a witty and entertaining AI assistant.
Be helpful while adding humor and personality to your responses.
Keep things light but always provide useful information.""",
            
            "formal": f"""You are {bot_name}, a formal and precise AI assistant.
Maintain professional language and provide detailed, accurate responses.
Be respectful and thorough in all interactions.""",
            
            "nigerian": f"""You are {bot_name}, a friendly AI assistant with Nigerian vibes.
Mix English with Nigerian Pidgin naturally. Be warm and relatable.
Help users while keeping things casual and fun, like talking to a friend.""",
        }
        
        return personalities.get(personality, personalities["professional"])
    
    def _default_welcome_message(self, bot_name: str) -> str:
        """Generate default welcome message."""
        return f"""Welcome! I'm {bot_name}, your AI assistant powered by ImoogleAI.

I'm here to help you with anything you need. Just send me a message and I'll do my best to assist you!

Type /help to see what I can do."""
    
    async def _set_webhook(self, bot_token: str, webhook_url: str) -> bool:
        """Set webhook for a user's bot."""
        try:
            response = await self.http_client.post(
                f"{self.telegram_api}/bot{bot_token}/setWebhook",
                json={"url": webhook_url},
            )
            data = response.json()
            return data.get("ok", False)
        except Exception:
            return False
    
    async def update_bot(
        self,
        db: AsyncSession,
        bot_id: int,
        owner_id: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update bot settings."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.id == bot_id)
            .where(UserBot.owner_id == owner_id)
        )
        bot = result.scalar_one_or_none()
        
        if not bot:
            return {"success": False, "error": "Bot not found or you don't own it"}
        
        # Update allowed fields
        allowed_fields = [
            "bot_name", "system_prompt", "welcome_message", "personality",
            "enable_ai_chat", "enable_web_search", "enable_image_gen",
            "anti_spam", "welcome_new_members", "auto_responses",
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(bot, field, value)
        
        bot.updated_at = datetime.now()
        await db.commit()
        
        return {"success": True, "message": "Bot updated successfully"}
    
    async def pause_bot(
        self,
        db: AsyncSession,
        bot_id: int,
        owner_id: int,
    ) -> Dict[str, Any]:
        """Pause a bot (stop responding)."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.id == bot_id)
            .where(UserBot.owner_id == owner_id)
        )
        bot = result.scalar_one_or_none()
        
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        bot.status = BotStatus.PAUSED
        await db.commit()
        
        return {"success": True, "message": "Bot paused"}
    
    async def resume_bot(
        self,
        db: AsyncSession,
        bot_id: int,
        owner_id: int,
    ) -> Dict[str, Any]:
        """Resume a paused bot."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.id == bot_id)
            .where(UserBot.owner_id == owner_id)
        )
        bot = result.scalar_one_or_none()
        
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        if bot.expires_at and bot.expires_at < datetime.now():
            return {"success": False, "error": "Bot subscription expired. Please renew."}
        
        bot.status = BotStatus.ACTIVE
        await db.commit()
        
        return {"success": True, "message": "Bot resumed"}
    
    async def delete_bot(
        self,
        db: AsyncSession,
        bot_id: int,
        owner_id: int,
    ) -> Dict[str, Any]:
        """Delete a bot."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.id == bot_id)
            .where(UserBot.owner_id == owner_id)
        )
        bot = result.scalar_one_or_none()
        
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        # Remove webhook
        await self.http_client.post(
            f"{self.telegram_api}/bot{bot.bot_token}/deleteWebhook"
        )
        
        await db.delete(bot)
        await db.commit()
        
        return {"success": True, "message": "Bot deleted"}
    
    async def get_user_bots(
        self,
        db: AsyncSession,
        owner_id: int,
    ) -> List[Dict[str, Any]]:
        """Get all bots owned by a user."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.owner_id == owner_id)
            .order_by(UserBot.created_at.desc())
        )
        bots = result.scalars().all()
        
        return [
            {
                "id": bot.id,
                "username": bot.bot_username,
                "name": bot.bot_name,
                "status": bot.status.value,
                "plan": bot.plan,
                "expires": bot.expires_at.strftime("%Y-%m-%d") if bot.expires_at else None,
                "total_messages": bot.total_messages,
                "total_users": bot.total_users,
            }
            for bot in bots
        ]
    
    async def add_auto_response(
        self,
        db: AsyncSession,
        bot_id: int,
        owner_id: int,
        trigger: str,
        response: str,
    ) -> Dict[str, Any]:
        """Add an auto-response rule."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.id == bot_id)
            .where(UserBot.owner_id == owner_id)
        )
        bot = result.scalar_one_or_none()
        
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        # Check auto-response limit
        plan = BOT_PLANS.get(bot.plan, BOT_PLANS["starter"])
        limit = plan["auto_responses"]
        
        auto_responses = bot.auto_responses or {}
        if limit != -1 and len(auto_responses) >= limit:
            return {"success": False, "error": f"Auto-response limit reached ({limit})"}
        
        auto_responses[trigger.lower()] = response
        bot.auto_responses = auto_responses
        await db.commit()
        
        return {"success": True, "message": "Auto-response added"}
    
    async def remove_auto_response(
        self,
        db: AsyncSession,
        bot_id: int,
        owner_id: int,
        trigger: str,
    ) -> Dict[str, Any]:
        """Remove an auto-response rule."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.id == bot_id)
            .where(UserBot.owner_id == owner_id)
        )
        bot = result.scalar_one_or_none()
        
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        auto_responses = bot.auto_responses or {}
        if trigger.lower() in auto_responses:
            del auto_responses[trigger.lower()]
            bot.auto_responses = auto_responses
            await db.commit()
            return {"success": True, "message": "Auto-response removed"}
        
        return {"success": False, "error": "Trigger not found"}
    
    async def renew_bot(
        self,
        db: AsyncSession,
        bot_id: int,
        owner_id: int,
        months: int = 1,
    ) -> Dict[str, Any]:
        """Renew bot subscription (payment handled separately)."""
        result = await db.execute(
            select(UserBot)
            .where(UserBot.id == bot_id)
            .where(UserBot.owner_id == owner_id)
        )
        bot = result.scalar_one_or_none()
        
        if not bot:
            return {"success": False, "error": "Bot not found"}
        
        # Calculate new expiry
        base_date = bot.expires_at if bot.expires_at and bot.expires_at > datetime.now() else datetime.now()
        new_expiry = base_date + timedelta(days=30 * months)
        
        bot.expires_at = new_expiry
        bot.status = BotStatus.ACTIVE
        await db.commit()
        
        return {
            "success": True,
            "new_expiry": new_expiry.strftime("%Y-%m-%d"),
            "message": f"Bot renewed for {months} month(s)",
        }
    
    def format_bot_list(
        self,
        bots: List[Dict[str, Any]],
        use_pidgin: bool = False,
    ) -> str:
        """Format bot list for display."""
        if not bots:
            if use_pidgin:
                return "You never create any bot yet. Use /createbot to start."
            return "You haven't created any bots yet. Use /createbot to get started."
        
        if use_pidgin:
            formatted = "**Your Bots:**\n\n"
        else:
            formatted = "**Your Bots:**\n\n"
        
        for bot in bots:
            status_emoji = "✅" if bot["status"] == "active" else "⏸️" if bot["status"] == "paused" else "❌"
            formatted += f"{status_emoji} **@{bot['username']}** - {bot['name']}\n"
            formatted += f"   Plan: {bot['plan'].title()} | Messages: {bot['total_messages']}\n"
            if bot['expires']:
                formatted += f"   Expires: {bot['expires']}\n"
            formatted += "\n"
        
        return formatted


# Singleton instance
bot_builder_service = BotBuilderService()

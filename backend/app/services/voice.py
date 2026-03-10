"""
Imoogle 5.0 Voice Service
Speech-to-Text (STT) and Text-to-Speech (TTS) capabilities.
Supports: Groq Whisper, Cloudflare Whisper, ElevenLabs, Hume AI
"""

import httpx
import base64
from typing import Optional, Tuple
from io import BytesIO
from groq import AsyncGroq
from elevenlabs import AsyncElevenLabs

from app.config import settings, COMPANION_PERSONAS


class VoiceService:
    """
    Voice processing service with:
    1. STT: Groq Whisper (primary), Cloudflare Whisper (fallback)
    2. TTS: ElevenLabs (primary), Hume AI (emotional)
    """
    
    def __init__(self):
        self.http_client = httpx.AsyncClient(timeout=60.0)
        self.groq = AsyncGroq(api_key=settings.GROQ_API_KEY)
        
        if settings.ELEVENLABS_API_KEY:
            self.elevenlabs = AsyncElevenLabs(api_key=settings.ELEVENLABS_API_KEY)
        else:
            self.elevenlabs = None
    
    async def close(self):
        await self.http_client.aclose()
    
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio to text.
        
        Args:
            audio_bytes: Audio file bytes (supports mp3, ogg, wav, etc.)
            language: Language code
        
        Returns:
            Transcribed text or None if failed
        """
        # Try Groq Whisper first
        try:
            return await self._groq_transcribe(audio_bytes, language)
        except Exception as e:
            print(f"[ImoogleAI] Groq transcription failed: {e}")
        
        # Fallback to Cloudflare Whisper
        if settings.CLOUDFLARE_ACCOUNT_ID:
            try:
                return await self._cloudflare_transcribe(audio_bytes, language)
            except Exception as e:
                print(f"[ImoogleAI] Cloudflare transcription failed: {e}")
        
        return None
    
    async def _groq_transcribe(self, audio_bytes: bytes, language: str) -> str:
        """Transcribe using Groq Whisper."""
        # Create a file-like object
        audio_file = BytesIO(audio_bytes)
        audio_file.name = "audio.ogg"
        
        response = await self.groq.audio.transcriptions.create(
            model="whisper-large-v3-turbo",
            file=audio_file,
            language=language if language != "auto" else None,
        )
        
        return response.text
    
    async def _cloudflare_transcribe(self, audio_bytes: bytes, language: str) -> str:
        """Transcribe using Cloudflare Workers AI Whisper."""
        url = f"https://api.cloudflare.com/client/v4/accounts/{settings.CLOUDFLARE_ACCOUNT_ID}/ai/run/@cf/openai/whisper"
        
        headers = {
            "Authorization": f"Bearer {settings.CLOUDFLARE_API_TOKEN}",
        }
        
        files = {
            "file": ("audio.ogg", audio_bytes, "audio/ogg"),
        }
        
        response = await self.http_client.post(url, headers=headers, files=files)
        response.raise_for_status()
        data = response.json()
        
        return data.get("result", {}).get("text", "")
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        companion_persona: Optional[str] = None,
        emotion: str = "neutral",
    ) -> Optional[bytes]:
        """
        Convert text to speech.
        
        Args:
            text: Text to synthesize
            voice_id: ElevenLabs voice ID
            companion_persona: Persona name to get voice from
            emotion: Emotion for Hume AI ("neutral", "happy", "sad", "excited")
        
        Returns:
            Audio bytes (mp3) or None if failed
        """
        # Get voice ID from persona if provided
        if companion_persona and companion_persona in COMPANION_PERSONAS:
            voice_id = COMPANION_PERSONAS[companion_persona].get("voice_id")
        
        # Default voice
        if not voice_id:
            voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel - neutral female
        
        # Try ElevenLabs first
        if self.elevenlabs:
            try:
                return await self._elevenlabs_synthesize(text, voice_id)
            except Exception as e:
                print(f"[ImoogleAI] ElevenLabs TTS failed: {e}")
        
        # Try Hume AI for emotional speech
        if settings.HUME_API_KEY and emotion != "neutral":
            try:
                return await self._hume_synthesize(text, emotion)
            except Exception as e:
                print(f"[ImoogleAI] Hume AI TTS failed: {e}")
        
        return None
    
    async def _elevenlabs_synthesize(self, text: str, voice_id: str) -> bytes:
        """Synthesize using ElevenLabs."""
        audio = await self.elevenlabs.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            model_id="eleven_multilingual_v2",
            output_format="mp3_44100_128",
        )
        
        # Collect all chunks
        chunks = []
        async for chunk in audio:
            chunks.append(chunk)
        
        return b"".join(chunks)
    
    async def _hume_synthesize(self, text: str, emotion: str) -> bytes:
        """Synthesize with emotional voice using Hume AI."""
        url = "https://api.hume.ai/v0/tts"
        
        headers = {
            "X-Hume-Api-Key": settings.HUME_API_KEY,
            "Content-Type": "application/json",
        }
        
        # Map emotions to Hume AI format
        emotion_map = {
            "happy": {"joy": 0.8, "excitement": 0.6},
            "sad": {"sadness": 0.7, "disappointment": 0.5},
            "excited": {"excitement": 0.9, "joy": 0.7},
            "angry": {"anger": 0.6, "frustration": 0.5},
            "loving": {"love": 0.8, "admiration": 0.6},
        }
        
        payload = {
            "text": text,
            "voice": "ITO",
            "emotions": emotion_map.get(emotion, {}),
        }
        
        response = await self.http_client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        
        return response.content
    
    async def voice_to_voice(
        self,
        audio_bytes: bytes,
        companion_persona: Optional[str] = None,
        use_pidgin: bool = False,
    ) -> Tuple[Optional[str], Optional[bytes]]:
        """
        Full voice-to-voice pipeline:
        1. Transcribe incoming audio
        2. Generate AI response
        3. Synthesize response to audio
        
        This is a convenience method that combines transcribe + AI + synthesize.
        The actual AI response generation should be done by the caller.
        
        Returns:
            Tuple of (transcribed_text, None) - caller handles AI + TTS
        """
        text = await self.transcribe(audio_bytes)
        return text, None


# Singleton instance
voice_service = VoiceService()

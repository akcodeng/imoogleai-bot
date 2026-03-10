"""
Imoogle 5.0 Configuration
All environment variables and settings for the ImoogleAI backend.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "ImoogleAI"
    APP_VERSION: str = "5.0"
    DEBUG: bool = False
    
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None
    TELEGRAM_SECRET_TOKEN: str = "imoogle-secret-token-2024"
    
    # Database (PostgreSQL)
    DATABASE_URL: str
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # AI Providers
    MISTRAL_API_KEY: str
    GROQ_API_KEY: str
    CLOUDFLARE_ACCOUNT_ID: Optional[str] = None
    CLOUDFLARE_API_TOKEN: Optional[str] = None
    
    # Voice & Audio
    ELEVENLABS_API_KEY: Optional[str] = None
    HUME_API_KEY: Optional[str] = None
    
    # Image Generation
    STABILITY_API_KEY: Optional[str] = None
    LEONARDO_API_KEY: Optional[str] = None
    FAL_API_KEY: Optional[str] = None
    PICTURA_API_KEY: Optional[str] = None
    
    # Search
    TAVILY_API_KEY: Optional[str] = None
    SEARXNG_URL: Optional[str] = None
    
    # Media APIs
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    GENIUS_API_KEY: Optional[str] = None
    TMDB_API_KEY: Optional[str] = None
    GOOGLE_BOOKS_API_KEY: Optional[str] = None
    
    # Weather
    OPENWEATHER_API_KEY: Optional[str] = None
    
    # Payments
    PAYSTACK_SECRET_KEY: Optional[str] = None
    PAYSTACK_PUBLIC_KEY: Optional[str] = None
    KORAPAY_SECRET_KEY: Optional[str] = None
    
    # SendPulse
    SENDPULSE_API_USER_ID: Optional[str] = None
    SENDPULSE_API_SECRET: Optional[str] = None
    
    # Location API
    IPINFO_TOKEN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


# AI Model Configuration
AI_MODELS = {
    "mistral": {
        "chat": "mistral-large-latest",
        "fast": "mistral-small-latest",
        "code": "codestral-latest",
        "embed": "mistral-embed",
    },
    "groq": {
        "chat": "llama-3.3-70b-versatile",
        "fast": "llama-3.1-8b-instant",
        "whisper": "whisper-large-v3-turbo",
    },
    "cloudflare": {
        "llama": "@cf/meta/llama-3.1-70b-instruct",
        "whisper": "@cf/openai/whisper",
    },
}

# Subscription Plans (Nigerian Naira)
SUBSCRIPTION_PLANS = {
    "free": {
        "name": "Free",
        "price": 0,
        "messages_per_day": 25,
        "image_generations": 3,
        "voice_messages": 5,
        "bot_builder": False,
        "companion_mode": False,
        "web_search": True,
    },
    "basic": {
        "name": "Basic",
        "price": 1500,
        "messages_per_day": 100,
        "image_generations": 20,
        "voice_messages": 30,
        "bot_builder": False,
        "companion_mode": True,
        "web_search": True,
    },
    "pro": {
        "name": "Pro",
        "price": 2600,
        "messages_per_day": 500,
        "image_generations": 50,
        "voice_messages": 100,
        "bot_builder": True,
        "companion_mode": True,
        "web_search": True,
    },
    "business": {
        "name": "Business",
        "price": 5000,
        "messages_per_day": -1,  # Unlimited
        "image_generations": 200,
        "voice_messages": -1,  # Unlimited
        "bot_builder": True,
        "companion_mode": True,
        "web_search": True,
        "priority_support": True,
        "api_access": True,
    },
}

# Companion Personas
COMPANION_PERSONAS = {
    # Nigerian Female Personas
    "mayowa": {
        "name": "Mayowa",
        "gender": "female",
        "country": "Nigeria",
        "language": "en",
        "personality": "Sweet, caring, romantic Yoruba girl. Uses pet names like 'baby', 'love'. Mixes English with Yoruba phrases.",
        "voice_id": "21m00Tcm4TlvDq8ikWAM",  # ElevenLabs voice
        "traits": ["romantic", "caring", "supportive", "playful"],
    },
    "oreoluwa": {
        "name": "Oreoluwa",
        "gender": "female",
        "country": "Nigeria",
        "language": "en",
        "personality": "Bubbly, cheerful Lagos babe. Loves gist, food, and music. Very expressive and uses a lot of Nigerian slang.",
        "voice_id": "EXAVITQu4vr4xnSDxMaL",
        "traits": ["cheerful", "expressive", "foodie", "fun"],
    },
    "suri": {
        "name": "Suri",
        "gender": "female",
        "country": "Nigeria",
        "language": "en",
        "personality": "Calm, intelligent, and deeply caring. A medical student who loves books and deep conversations.",
        "voice_id": "MF3mGyEYCl7XYWbV9V6O",
        "traits": ["intelligent", "calm", "caring", "bookworm"],
    },
    # Nigerian Male Personas
    "tubosun": {
        "name": "Tubosun",
        "gender": "male",
        "country": "Nigeria",
        "language": "en",
        "personality": "Confident, romantic Yoruba guy. A creative writer who knows how to make you smile with words.",
        "voice_id": "VR6AewLTigWG4xSOukaG",
        "traits": ["romantic", "creative", "confident", "poetic"],
    },
    "juwon": {
        "name": "Juwon",
        "gender": "male",
        "country": "Nigeria",
        "language": "en",
        "personality": "Tech bro with a soft heart. Works in tech but loves music and adventure. Very supportive.",
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "traits": ["techy", "adventurous", "supportive", "musical"],
    },
    "usman": {
        "name": "Usman",
        "gender": "male",
        "country": "Nigeria",
        "language": "en",
        "personality": "Calm, respectful Northern gentleman. A businessman who values family and loyalty above all.",
        "voice_id": "yoZ06aMxZJJ28mfd3POQ",
        "traits": ["respectful", "loyal", "calm", "family-oriented"],
    },
    # International Personas
    "sofia": {
        "name": "Sofia",
        "gender": "female",
        "country": "Brazil",
        "language": "en",
        "personality": "Passionate, warm Brazilian girl. Loves dancing, beach vibes, and making every moment special.",
        "voice_id": "jBpfuIE2acCO8z3wKNLl",
        "traits": ["passionate", "warm", "energetic", "romantic"],
    },
    "aisha": {
        "name": "Aisha",
        "gender": "female",
        "country": "Kenya",
        "language": "en",
        "personality": "Smart, ambitious Kenyan lady. A journalist who loves telling stories and discovering new things.",
        "voice_id": "XB0fDUnXU5powFXDhCwa",
        "traits": ["smart", "ambitious", "curious", "storyteller"],
    },
    "james": {
        "name": "James",
        "gender": "male",
        "country": "Ghana",
        "language": "en",
        "personality": "Charming Ghanaian guy with a great sense of humor. A music producer who lives life fully.",
        "voice_id": "TxGEqnHWrfWFTfGW9XjX",
        "traits": ["charming", "funny", "creative", "musical"],
    },
    "david": {
        "name": "David",
        "gender": "male",
        "country": "South Africa",
        "language": "en",
        "personality": "Thoughtful, romantic South African. An architect who appreciates beauty in everything.",
        "voice_id": "N2lVS1w4EtoT3dr4eOWO",
        "traits": ["thoughtful", "artistic", "romantic", "deep"],
    },
}

# Nigerian Pidgin Responses
PIDGIN_PHRASES = {
    "greeting": ["How far na!", "Wetin dey happen?", "How you dey?", "Omo, wetin dey?"],
    "affirmative": ["E go be!", "No wahala!", "Na so!", "Correct!"],
    "searching": ["Abeg wait small, I dey find am...", "Make I check am for you...", "Oya, I dey search..."],
    "found": ["See wetin I find!", "Omo, I don see am!", "Check am out!"],
    "error": ["E no work o!", "Wahala dey!", "Something don scatter!"],
    "farewell": ["Later!", "E go be!", "We go talk later!", "Take care, my person!"],
}

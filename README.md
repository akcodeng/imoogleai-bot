# ImoogleAI Bot v5.0

> The most powerful AI assistant on Telegram - Built in Lagos, Nigeria

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Telegram Bot API](https://img.shields.io/badge/Telegram-Bot%20API-blue.svg)](https://core.telegram.org/bots/api)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)

---

## What is ImoogleAI?

**ImoogleAI** is a personal AI assistant that lives on Telegram. It can do almost anything - chat intelligently, search the web, generate images, process voice messages, manage payments, and even build custom bots for your business.

**Founded by:** Olajuwon (sidicode) & Tariq | **Based in:** Lagos, Nigeria | **Company:** Imoogle Technology

---

## Features

### AI & Chat
| Feature | Description |
|---------|-------------|
| Smart Chat | Multi-provider AI routing (Mistral, Groq, Cloudflare) |
| Web Search | Real-time internet search with Tavily/SearchNGX |
| Voice-to-Voice | Whisper STT + ElevenLabs TTS for natural conversations |
| Image Generation | Stability AI, Leonardo AI, Mistral with Pictura branding |
| Document Creation | Generate PDFs, summaries, and formatted documents |

### Companion Mode
| Persona | Type | Personality |
|---------|------|-------------|
| Mayowa | Female | Sweet, caring Nigerian girlfriend |
| Oreoluwa | Female | Playful, witty Yoruba partner |
| Suri | Female | International, sophisticated |
| Tubosun | Male | Romantic, thoughtful Nigerian boyfriend |
| Juwon | Male | Fun, adventurous partner |
| Usman | Male | Caring, protective Hausa boyfriend |

Companions send check-up messages, remember your name, share voice notes, and act like real romantic partners.

### Imoogle Pay (Nigeria Only)
| Feature | Description |
|---------|-------------|
| Wallet | NGN balance with deposit/withdraw via Paystack |
| ImoCoin | Virtual currency for in-app transactions |
| P2P Transfer | Send money to other Imoogle users instantly |
| PIN Security | 4-digit PIN for all transactions |
| Transaction History | Complete audit trail |

### Bot Builder
Build custom Telegram bots for your business with AI-powered responses.

| Plan | Price | Messages/Month | Features |
|------|-------|----------------|----------|
| Starter | ₦1,500 | 1,000 | Basic AI, 1 bot |
| Growth | ₦2,600 | 5,000 | Advanced AI, 3 bots |
| Business | ₦5,000 | 15,000 | Premium AI, 10 bots, Analytics |
| Enterprise | ₦15,000 | Unlimited | All features, Priority support |

### Media & Entertainment
- **Music**: Spotify + Genius integration for recommendations and lyrics
- **Movies**: TMDB integration for recommendations and info
- **Books**: Google Books search and recommendations
- **Weather**: Location-based forecasts

### Group Moderation
- Anti-spam detection and auto-removal
- Warning system with configurable limits
- Welcome messages and rules enforcement
- Admin action logging

---

## Tech Stack

```
AI Providers     : Mistral AI (primary), Groq, Cloudflare Workers AI
Voice            : Cloudflare Whisper (STT), ElevenLabs (TTS), Hume AI
Images           : Stability AI, Leonardo AI, Pictura (branding)
Search           : Tavily, SearchNGX
Database         : PostgreSQL
Payments         : Paystack, KoraPay
Framework        : FastAPI + python-telegram-bot
Deployment       : Docker + DigitalOcean
```

---

## Project Structure

```
backend/
├── main.py                    # FastAPI app + webhook handler
├── app/
│   ├── config.py              # Environment variables & settings
│   ├── database/
│   │   ├── __init__.py        # Database connection
│   │   └── models.py          # SQLAlchemy models
│   ├── bot/
│   │   ├── handlers.py        # Telegram command handlers
│   │   ├── callbacks.py       # Inline button callbacks
│   │   ├── keyboards.py       # Inline keyboards & reply markups
│   │   └── messages.py        # Message templates
│   └── services/
│       ├── ai_router.py       # Multi-provider AI routing
│       ├── voice.py           # Speech-to-text & text-to-speech
│       ├── image_gen.py       # Image generation + branding
│       ├── search.py          # Web search integration
│       ├── companion.py       # Romantic companion system
│       ├── payments.py        # Imoogle Pay & subscriptions
│       ├── bot_builder.py     # Custom bot creation
│       ├── moderation.py      # Group spam protection
│       ├── media.py           # Music, movies, books
│       ├── weather.py         # Weather forecasts
│       ├── location.py        # Geolocation & personalization
│       ├── documents.py       # Document generation
│       └── reminders.py       # Scheduled reminders
├── migrations/
│   └── 001_initial.sql        # Database schema
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── deploy.sh
└── .env.example
```

---

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 15+
- Telegram Bot Token (from @BotFather)
- API keys for services (see `.env.example`)

### Local Development

```bash
# Clone the repository
git clone https://github.com/akcodeng/imoogleai-bot.git
cd imoogleai-bot/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
psql $DATABASE_URL -f migrations/001_initial.sql

# Start the server
uvicorn main:app --reload --port 8000
```

### Using Docker

```bash
cd backend

# Build and run
docker-compose up -d

# View logs
docker-compose logs -f imoogle-bot
```

---

## Deployment (DigitalOcean)

### 1. Create Droplet
- Ubuntu 22.04 LTS
- 2GB RAM / 1 vCPU minimum (4GB recommended)
- Enable backups

### 2. SSH via Termius
```bash
ssh root@your-droplet-ip
```

### 3. Run Deployment Script
```bash
# Upload the backend folder to your droplet, then:
cd /root/imoogleai-bot/backend
chmod +x deploy.sh
sudo ./deploy.sh
```

### 4. Configure Environment
```bash
nano /root/imoogleai-bot/backend/.env
# Add all your API keys
```

### 5. Set Telegram Webhook
```bash
curl -X POST "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/webhook"}'
```

---

## Environment Variables

### Required
```env
TELEGRAM_BOT_TOKEN=          # From @BotFather
DATABASE_URL=                # PostgreSQL connection string
MISTRAL_API_KEY=             # Primary AI provider
```

### AI Providers
```env
GROQ_API_KEY=                # Fast inference
CLOUDFLARE_ACCOUNT_ID=       # Workers AI
CLOUDFLARE_API_TOKEN=        # Workers AI auth
```

### Voice & Media
```env
ELEVENLABS_API_KEY=          # Text-to-speech
HUME_API_KEY=                # Emotional voice AI
STABILITY_API_KEY=           # Image generation
LEONARDO_API_KEY=            # Image generation
```

### Search & Data
```env
TAVILY_API_KEY=              # Web search
OPENWEATHER_API_KEY=         # Weather data
SPOTIFY_CLIENT_ID=           # Music
SPOTIFY_CLIENT_SECRET=       # Music
GENIUS_API_KEY=              # Lyrics
TMDB_API_KEY=                # Movies
GOOGLE_BOOKS_API_KEY=        # Books
```

### Payments (Nigeria)
```env
PAYSTACK_SECRET_KEY=         # Deposits/Withdrawals
KORAPAY_SECRET_KEY=          # Alternative payments
```

---

## Bot Commands

### General
| Command | Description |
|---------|-------------|
| `/start` | Start the bot & onboarding |
| `/help` | Show all commands |
| `/settings` | User preferences |
| `/profile` | View your profile |

### AI Features
| Command | Description |
|---------|-------------|
| `/ask <question>` | Ask ImoogleAI anything |
| `/search <query>` | Search the web |
| `/image <prompt>` | Generate an image |
| `/voice` | Toggle voice mode |
| `/document <type>` | Create a document |

### Companion
| Command | Description |
|---------|-------------|
| `/companion` | Choose a companion |
| `/mood <status>` | Set your mood |
| `/nickname <name>` | Set your nickname |

### Payments
| Command | Description |
|---------|-------------|
| `/wallet` | View balance |
| `/deposit <amount>` | Add funds |
| `/withdraw <amount>` | Cash out |
| `/send <username> <amount>` | P2P transfer |
| `/pin` | Set/change PIN |

### Bot Builder
| Command | Description |
|---------|-------------|
| `/createbot` | Start bot creation |
| `/mybots` | View your bots |
| `/subscribe` | Choose a plan |

### Media
| Command | Description |
|---------|-------------|
| `/music <query>` | Search music |
| `/movie <query>` | Search movies |
| `/book <query>` | Search books |
| `/weather` | Current weather |
| `/weather <city>` | Weather for city |

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook` | POST | Telegram webhook handler |
| `/health` | GET | Health check |
| `/payment/webhook` | POST | Paystack webhook |

---

## Localization

ImoogleAI automatically detects user location and personalizes the experience:

| Country | Language | Currency | Features |
|---------|----------|----------|----------|
| Nigeria | English + Pidgin | NGN (₦) | Full (Payments, Local companions) |
| Ghana | English | GHS | Coming soon |
| Kenya | English | KES | Coming soon |
| South Africa | English | ZAR | Coming soon |
| Others | English | - | AI features only |

---

## Troubleshooting

### Bot not responding
```bash
# Check if service is running
sudo systemctl status imoogle-bot

# View logs
sudo journalctl -u imoogle-bot -f

# Restart service
sudo systemctl restart imoogle-bot
```

### Database connection issues
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"

# Check PostgreSQL status
sudo systemctl status postgresql
```

### Webhook not receiving updates
```bash
# Check webhook status
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"

# Re-register webhook
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://your-domain.com/webhook"
```

---

## Contributing

This is a proprietary project by Imoogle Technology. For inquiries, contact:
- Telegram: [@sidicode](https://t.me/sidicode)
- Email: hello@imoogle.tech

---

## License

Copyright 2024 Imoogle Technology. All rights reserved.

---

<p align="center">
  <b>Built with love in Lagos, Nigeria</b><br>
  <i>Imoogle Technology - Making AI accessible to everyone</i>
</p>

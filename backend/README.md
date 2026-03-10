# Imoogle 5.0 - AI-Powered Telegram Assistant

> The most advanced AI chatbot on Telegram, built by Imoogle Technology

**Founded by:** Olajuwon (sidicode) & Tariq - Software Engineers based in Lagos, Nigeria

---

## Table of Contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Quick Start](#quick-start)
4. [Deployment Guide](#deployment-guide)
5. [Configuration](#configuration)
6. [API Documentation](#api-documentation)
7. [Bot Commands](#bot-commands)
8. [Subscription Plans](#subscription-plans)
9. [Troubleshooting](#troubleshooting)

---

## Features

### Core AI Capabilities

| Feature | Description | Provider |
|---------|-------------|----------|
| **Smart Chat** | Context-aware conversations with memory | Mistral AI (primary) |
| **Web Search** | Real-time internet search with source citations | Tavily / SearchNGX |
| **Image Generation** | AI-generated images with Imoogle branding | Stability AI / Leonardo AI / Mistral |
| **Voice-to-Voice** | Full voice conversations | Cloudflare Whisper + ElevenLabs |
| **Document Creation** | Generate PDFs, Word docs, spreadsheets | ReportLab / python-docx |

### Companion System

Romantic AI companions with Nigerian and international personas:

**Female Companions:**
- Mayowa (Nigerian - Yoruba)
- Oreoluwa (Nigerian - Yoruba)
- Suri (Nigerian - Igbo)
- Sofia (International)
- Aisha (International)
- Luna (International)

**Male Companions:**
- Tubosun (Nigerian - Yoruba)
- Juwon (Nigerian - Yoruba)
- Usman (Nigerian - Hausa)
- Marcus (International)
- Khalid (International)
- Alex (International)

**Companion Features:**
- Daily check-ups ("Have you eaten today?")
- Good morning/night messages
- Voice notes and images
- Remembers your name, preferences, important dates
- Romantic and supportive conversations

### Imoogle Pay (Nigeria Only)

| Feature | Description |
|---------|-------------|
| **Wallet** | NGN wallet with ImoCoin rewards |
| **Deposit** | Via Paystack (cards, bank transfer, USSD) |
| **Withdraw** | Direct to Nigerian bank accounts |
| **P2P Transfer** | Send money to other Imoogle users |
| **PIN Security** | 4-digit transaction PIN |
| **Transaction History** | Full audit trail |

### Bot Builder

Create custom Telegram bots for your business:

| Plan | Price/Month | Features |
|------|-------------|----------|
| **Starter** | ₦1,500 | 500 messages, 1 bot, basic AI |
| **Growth** | ₦2,600 | 2,000 messages, 3 bots, web search |
| **Business** | ₦5,000 | 10,000 messages, 10 bots, voice + images |
| **Enterprise** | ₦15,000 | Unlimited, priority support, custom training |

### Media & Entertainment

| Service | API | Features |
|---------|-----|----------|
| **Music** | Spotify + Genius | Recommendations, lyrics, artist info |
| **Movies** | TMDB | Recommendations, ratings, where to watch |
| **Books** | Google Books | Recommendations, summaries, read online links |

### Group Moderation

- Anti-spam detection
- Auto-kick/ban bad actors
- Warning system (3 strikes)
- Custom banned words
- Link filtering
- New member verification

### Smart Personalization

- Auto-detects user location via IP
- Adapts language (Pidgin for Nigeria)
- Local weather integration
- Currency formatting (₦ for Nigeria)
- Timezone-aware reminders

---

## Architecture

```
backend/
├── main.py                 # FastAPI app + webhook endpoint
├── app/
│   ├── config.py           # All configuration & environment vars
│   ├── database/
│   │   ├── __init__.py     # DB connection pool
│   │   └── models.py       # SQLAlchemy models
│   ├── bot/
│   │   ├── handlers.py     # Main message handlers
│   │   ├── callbacks.py    # Inline button callbacks
│   │   ├── keyboards.py    # All keyboard layouts
│   │   └── messages.py     # Message templates
│   └── services/
│       ├── ai_router.py    # Multi-provider AI routing
│       ├── voice.py        # STT + TTS
│       ├── image_gen.py    # Image generation + branding
│       ├── search.py       # Web search
│       ├── companion.py    # AI companions
│       ├── payments.py     # Imoogle Pay
│       ├── bot_builder.py  # Custom bot creation
│       ├── moderation.py   # Group moderation
│       ├── media.py        # Music/Movies/Books
│       ├── weather.py      # Weather service
│       ├── location.py     # Geolocation
│       ├── documents.py    # Document generation
│       └── reminders.py    # Scheduled reminders
├── migrations/
│   └── 001_initial.sql     # Database schema
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── deploy.sh
└── .env.example
```

### AI Provider Routing

```
┌─────────────────────────────────────────────────────────┐
│                    User Message                          │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  Intent Detection                        │
│  • Chat → Mistral AI                                    │
│  • Fast response → Groq (Llama)                         │
│  • Image → Stability/Leonardo/Mistral                   │
│  • Voice → Cloudflare Whisper + ElevenLabs              │
│  • Search → Tavily + SearchNGX                          │
└─────────────────────────────────────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis (optional, for caching)
- Telegram Bot Token (from @BotFather)

### Local Development

```bash
# Clone the repository
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -e .

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run database migrations
psql -U postgres -d imoogle -f migrations/001_initial.sql

# Start the server
uvicorn main:app --reload --port 8000
```

### Set Webhook

```bash
curl -X POST "https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://your-domain.com/webhook"}'
```

---

## Deployment Guide

### Option 1: DigitalOcean Droplet (Recommended)

**Requirements:** Ubuntu 22.04, 2GB RAM minimum

```bash
# SSH into your droplet (via Termius or terminal)
ssh root@your-droplet-ip

# Clone your code
git clone https://github.com/your-repo/imoogle-backend.git
cd imoogle-backend/backend

# Make deploy script executable
chmod +x deploy.sh

# Run deployment
sudo ./deploy.sh
```

The deploy script will:
1. Install Docker & Docker Compose
2. Set up PostgreSQL & Redis
3. Configure Nginx with SSL (Let's Encrypt)
4. Start all services
5. Set up the Telegram webhook

### Option 2: Docker Compose (Any Server)

```bash
# Copy environment file
cp .env.example .env
nano .env  # Add your API keys

# Start services
docker-compose up -d

# View logs
docker-compose logs -f imoogle
```

### Option 3: Manual Deployment

```bash
# Install system dependencies
sudo apt update
sudo apt install python3.11 python3.11-venv postgresql nginx certbot

# Create database
sudo -u postgres createdb imoogle
sudo -u postgres psql -d imoogle -f migrations/001_initial.sql

# Set up Python environment
python3.11 -m venv venv
source venv/bin/activate
pip install -e .

# Create systemd service
sudo nano /etc/systemd/system/imoogle.service
```

**systemd service file:**
```ini
[Unit]
Description=Imoogle Telegram Bot
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/opt/imoogle/backend
Environment="PATH=/opt/imoogle/backend/venv/bin"
EnvironmentFile=/opt/imoogle/backend/.env
ExecStart=/opt/imoogle/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Start the service
sudo systemctl daemon-reload
sudo systemctl enable imoogle
sudo systemctl start imoogle
```

---

## Configuration

### Required Environment Variables

```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
WEBHOOK_URL=https://your-domain.com/webhook
WEBHOOK_SECRET=random_secret_string

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/imoogle

# AI Providers (Primary)
MISTRAL_API_KEY=your_mistral_key
GROQ_API_KEY=your_groq_key

# Cloudflare AI Workers
CLOUDFLARE_ACCOUNT_ID=your_account_id
CLOUDFLARE_API_TOKEN=your_api_token

# Voice
ELEVENLABS_API_KEY=your_elevenlabs_key

# Image Generation
STABILITY_API_KEY=your_stability_key
LEONARDO_API_KEY=your_leonardo_key

# Search
TAVILY_API_KEY=your_tavily_key

# Payments (Nigeria)
PAYSTACK_SECRET_KEY=sk_live_xxxxx
PAYSTACK_PUBLIC_KEY=pk_live_xxxxx
KORAPAY_SECRET_KEY=your_korapay_key

# Media APIs
SPOTIFY_CLIENT_ID=your_spotify_id
SPOTIFY_CLIENT_SECRET=your_spotify_secret
GENIUS_API_KEY=your_genius_key
TMDB_API_KEY=your_tmdb_key
GOOGLE_BOOKS_API_KEY=your_google_books_key

# Weather
OPENWEATHER_API_KEY=your_openweather_key
```

### Optional Environment Variables

```bash
# Redis (for caching)
REDIS_URL=redis://localhost:6379

# Hume AI (emotional voice)
HUME_API_KEY=your_hume_key

# SendPulse (already connected)
SENDPULSE_ID=your_sendpulse_id
SENDPULSE_SECRET=your_sendpulse_secret

# Pictura AI (image branding)
PICTURA_API_KEY=your_pictura_key
```

---

## API Documentation

### Webhook Endpoint

```
POST /webhook
```

Receives all Telegram updates. Automatically routes to appropriate handlers.

### Health Check

```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "version": "5.0.0",
  "uptime": 3600,
  "database": "connected",
  "services": {
    "mistral": "ok",
    "groq": "ok",
    "elevenlabs": "ok"
  }
}
```

### Paystack Webhook

```
POST /paystack/webhook
```

Handles payment confirmations for deposits.

### User Stats (Internal)

```
GET /stats/{user_id}
```

Returns user statistics and usage data.

---

## Bot Commands

### General Commands

| Command | Description |
|---------|-------------|
| `/start` | Start the bot, onboarding flow |
| `/help` | Show all available commands |
| `/menu` | Open main menu |
| `/settings` | User preferences |
| `/profile` | View your profile |
| `/language` | Change language |

### AI Commands

| Command | Description |
|---------|-------------|
| `/ask [question]` | Ask Imoogle anything |
| `/search [query]` | Search the web |
| `/image [prompt]` | Generate an image |
| `/voice` | Toggle voice mode |
| `/translate [text]` | Translate text |
| `/summarize` | Summarize text/URL |

### Companion Commands

| Command | Description |
|---------|-------------|
| `/companion` | Open companion menu |
| `/girlfriend` | Choose female companion |
| `/boyfriend` | Choose male companion |
| `/mood [happy/sad/etc]` | Set companion mood |
| `/checkin` | Manual check-in |

### Imoogle Pay Commands (Nigeria)

| Command | Description |
|---------|-------------|
| `/wallet` | View wallet balance |
| `/deposit [amount]` | Add money to wallet |
| `/withdraw [amount]` | Withdraw to bank |
| `/send [username] [amount]` | Send to another user |
| `/history` | Transaction history |
| `/setpin` | Set/change transaction PIN |

### Bot Builder Commands

| Command | Description |
|---------|-------------|
| `/createbot` | Create a new bot |
| `/mybots` | List your bots |
| `/editbot [bot_id]` | Edit bot settings |
| `/botanalytics [bot_id]` | View bot analytics |
| `/subscribe` | View subscription plans |

### Media Commands

| Command | Description |
|---------|-------------|
| `/music [query]` | Search/recommend music |
| `/lyrics [song]` | Get song lyrics |
| `/movie [query]` | Search/recommend movies |
| `/book [query]` | Search/recommend books |

### Utility Commands

| Command | Description |
|---------|-------------|
| `/weather [city]` | Get weather info |
| `/remind [time] [message]` | Set a reminder |
| `/calculate [expression]` | Calculator |
| `/convert [value] [from] [to]` | Unit converter |
| `/qrcode [text]` | Generate QR code |

### Group Commands (Admins)

| Command | Description |
|---------|-------------|
| `/moderation` | Toggle moderation |
| `/antispam` | Configure anti-spam |
| `/warn [user]` | Warn a user |
| `/ban [user]` | Ban a user |
| `/unban [user]` | Unban a user |
| `/rules` | Set group rules |

---

## Subscription Plans

### Bot Builder Pricing (Nigeria)

| Plan | Monthly | Messages | Bots | Features |
|------|---------|----------|------|----------|
| **Starter** | ₦1,500 | 500 | 1 | Basic AI responses |
| **Growth** | ₦2,600 | 2,000 | 3 | + Web search, scheduling |
| **Business** | ₦5,000 | 10,000 | 10 | + Voice, images, analytics |
| **Enterprise** | ₦15,000 | Unlimited | Unlimited | + Priority support, custom training |

### Payment Methods

- Debit/Credit Cards (Visa, Mastercard, Verve)
- Bank Transfer
- USSD
- ImoCoin (internal currency)

---

## Troubleshooting

### Bot Not Responding

1. Check webhook is set correctly:
```bash
curl "https://api.telegram.org/bot<TOKEN>/getWebhookInfo"
```

2. Verify server is running:
```bash
sudo systemctl status imoogle
```

3. Check logs:
```bash
docker-compose logs -f imoogle
# or
sudo journalctl -u imoogle -f
```

### Database Connection Issues

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -U postgres -d imoogle -c "SELECT 1"
```

### Payment Webhooks Not Working

1. Verify Paystack webhook URL in dashboard
2. Check webhook secret matches `.env`
3. Ensure SSL certificate is valid

### Voice Not Working

1. Verify ElevenLabs API key
2. Check Cloudflare Workers is set up
3. Test STT endpoint manually

### Common Errors

| Error | Solution |
|-------|----------|
| `401 Unauthorized` | Check API keys in `.env` |
| `Connection refused` | Ensure PostgreSQL is running |
| `Webhook timeout` | Check server response time (<5s) |
| `Rate limited` | Implement caching with Redis |

---

## Support

- **Telegram:** @ImoogleSupport
- **Email:** support@imoogle.tech
- **Website:** https://imoogle.tech

---

## License

Proprietary - Imoogle Technology

Copyright (c) 2024 Imoogle Technology. All rights reserved.

---

Built with love in Lagos, Nigeria

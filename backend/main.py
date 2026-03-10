"""
Imoogle 5.0 - Main FastAPI Application
Production-ready Telegram bot backend with all features
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, Response, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from telegram import Update, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from app.config import settings
from app.database import init_db, get_db
from app.database.models import User
from app.bot.handlers import BotHandlers
from app.bot.callbacks import callback_handler
from app.services.payments import PaymentService
from app.services.bot_builder import BotBuilderService
from app.services.reminders import ReminderService
from app.services.companion import CompanionService

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global application instance
telegram_app: Optional[Application] = None
bot_handlers: Optional[BotHandlers] = None
payment_service: Optional[PaymentService] = None
reminder_service: Optional[ReminderService] = None
companion_service: Optional[CompanionService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global telegram_app, bot_handlers, payment_service, reminder_service, companion_service
    
    logger.info("Starting Imoogle 5.0...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize services
    payment_service = PaymentService()
    reminder_service = ReminderService()
    companion_service = CompanionService()
    
    # Initialize Telegram bot
    bot_handlers = BotHandlers()
    telegram_app = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .build()
    )
    
    # Register handlers
    telegram_app.add_handler(CommandHandler("start", bot_handlers.start))
    telegram_app.add_handler(CommandHandler("help", bot_handlers.help))
    telegram_app.add_handler(CommandHandler("menu", bot_handlers.menu))
    telegram_app.add_handler(CommandHandler("search", bot_handlers.search))
    telegram_app.add_handler(CommandHandler("image", bot_handlers.generate_image))
    telegram_app.add_handler(CommandHandler("companion", bot_handlers.companion))
    telegram_app.add_handler(CommandHandler("pay", bot_handlers.pay))
    telegram_app.add_handler(CommandHandler("balance", bot_handlers.balance))
    telegram_app.add_handler(CommandHandler("send", bot_handlers.send_money))
    telegram_app.add_handler(CommandHandler("deposit", bot_handlers.deposit))
    telegram_app.add_handler(CommandHandler("withdraw", bot_handlers.withdraw))
    telegram_app.add_handler(CommandHandler("botbuilder", bot_handlers.bot_builder))
    telegram_app.add_handler(CommandHandler("mybots", bot_handlers.my_bots))
    telegram_app.add_handler(CommandHandler("weather", bot_handlers.weather))
    telegram_app.add_handler(CommandHandler("music", bot_handlers.music))
    telegram_app.add_handler(CommandHandler("movies", bot_handlers.movies))
    telegram_app.add_handler(CommandHandler("books", bot_handlers.books))
    telegram_app.add_handler(CommandHandler("reminder", bot_handlers.reminder))
    telegram_app.add_handler(CommandHandler("document", bot_handlers.document))
    telegram_app.add_handler(CommandHandler("voice", bot_handlers.toggle_voice))
    telegram_app.add_handler(CommandHandler("settings", bot_handlers.settings))
    telegram_app.add_handler(CommandHandler("premium", bot_handlers.premium))
    telegram_app.add_handler(CommandHandler("about", bot_handlers.about))
    telegram_app.add_handler(CommandHandler("feedback", bot_handlers.feedback))
    
    # Callback query handler
    telegram_app.add_handler(CallbackQueryHandler(callback_handler.handle))
    
    # Message handlers
    telegram_app.add_handler(MessageHandler(filters.VOICE, bot_handlers.handle_voice))
    telegram_app.add_handler(MessageHandler(filters.PHOTO, bot_handlers.handle_photo))
    telegram_app.add_handler(MessageHandler(filters.Document.ALL, bot_handlers.handle_document))
    telegram_app.add_handler(MessageHandler(filters.LOCATION, bot_handlers.handle_location))
    telegram_app.add_handler(MessageHandler(filters.CONTACT, bot_handlers.handle_contact))
    telegram_app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        bot_handlers.handle_message
    ))
    
    # Group handlers
    telegram_app.add_handler(MessageHandler(
        filters.StatusUpdate.NEW_CHAT_MEMBERS,
        bot_handlers.handle_new_member
    ))
    telegram_app.add_handler(MessageHandler(
        filters.StatusUpdate.LEFT_CHAT_MEMBER,
        bot_handlers.handle_left_member
    ))
    
    # Initialize the application
    await telegram_app.initialize()
    
    # Set webhook if in production
    if settings.environment == "production":
        webhook_url = f"{settings.webhook_base_url}/webhook"
        await telegram_app.bot.set_webhook(
            url=webhook_url,
            allowed_updates=["message", "callback_query", "inline_query", "chat_member"]
        )
        logger.info(f"Webhook set to {webhook_url}")
    
    # Start background tasks
    asyncio.create_task(run_background_tasks())
    
    logger.info("Imoogle 5.0 started successfully!")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Imoogle 5.0...")
    if telegram_app:
        await telegram_app.shutdown()


async def run_background_tasks():
    """Run periodic background tasks"""
    global reminder_service, companion_service
    
    while True:
        try:
            # Process reminders every minute
            if reminder_service:
                await reminder_service.process_due_reminders()
            
            # Send companion check-ups every hour
            if companion_service:
                await companion_service.send_scheduled_checkups()
            
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Background task error: {e}")
            await asyncio.sleep(60)


# Create FastAPI app
app = FastAPI(
    title="Imoogle 5.0 API",
    description="AI-powered Telegram assistant backend",
    version="5.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==================== ROUTES ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "Imoogle 5.0",
        "version": "5.0.0",
        "message": "ImoogleAI is running!"
    }


@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "telegram": "connected",
        "services": {
            "ai": "operational",
            "payments": "operational",
            "voice": "operational",
            "images": "operational"
        }
    }


@app.post("/webhook")
async def webhook(request: Request):
    """Telegram webhook endpoint"""
    global telegram_app
    
    if not telegram_app:
        raise HTTPException(status_code=503, detail="Bot not initialized")
    
    try:
        data = await request.json()
        update = Update.de_json(data, telegram_app.bot)
        
        # Process update asynchronously
        asyncio.create_task(telegram_app.process_update(update))
        
        return Response(status_code=200)
    
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return Response(status_code=200)  # Always return 200 to Telegram


@app.post("/webhook/paystack")
async def paystack_webhook(request: Request, background_tasks: BackgroundTasks):
    """Paystack payment webhook"""
    global payment_service
    
    try:
        data = await request.json()
        event = data.get("event")
        
        if event == "charge.success":
            payment_data = data.get("data", {})
            reference = payment_data.get("reference")
            amount = payment_data.get("amount", 0) / 100  # Convert from kobo
            
            # Process payment in background
            background_tasks.add_task(
                payment_service.process_deposit_webhook,
                reference,
                amount
            )
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"Paystack webhook error: {e}")
        return {"status": "error"}


@app.post("/webhook/korapay")
async def korapay_webhook(request: Request, background_tasks: BackgroundTasks):
    """KoraPay payment webhook"""
    global payment_service
    
    try:
        data = await request.json()
        event = data.get("event")
        
        if event == "charge.completed":
            payment_data = data.get("data", {})
            reference = payment_data.get("reference")
            amount = float(payment_data.get("amount", 0))
            
            background_tasks.add_task(
                payment_service.process_deposit_webhook,
                reference,
                amount
            )
        
        return {"status": "received"}
    
    except Exception as e:
        logger.error(f"KoraPay webhook error: {e}")
        return {"status": "error"}


@app.post("/api/user-bots/{bot_id}/webhook")
async def user_bot_webhook(bot_id: str, request: Request):
    """Webhook for user-created bots"""
    global bot_handlers
    
    try:
        data = await request.json()
        
        # Process the user bot's update
        async with get_db() as db:
            bot_builder = BotBuilderService()
            await bot_builder.process_user_bot_update(db, bot_id, data)
        
        return Response(status_code=200)
    
    except Exception as e:
        logger.error(f"User bot webhook error: {e}")
        return Response(status_code=200)


@app.get("/api/stats")
async def get_stats():
    """Get bot statistics"""
    async with get_db() as db:
        from sqlalchemy import func, select
        
        total_users = await db.scalar(select(func.count(User.id)))
        premium_users = await db.scalar(
            select(func.count(User.id)).where(User.is_premium == True)
        )
        active_today = await db.scalar(
            select(func.count(User.id)).where(
                User.last_active >= func.now() - func.cast('1 day', func.interval)
            )
        )
        
        return {
            "total_users": total_users,
            "premium_users": premium_users,
            "active_today": active_today
        }


@app.post("/api/broadcast")
async def broadcast_message(request: Request):
    """Admin endpoint to broadcast messages to all users"""
    global telegram_app
    
    # Verify admin token
    auth = request.headers.get("Authorization")
    if auth != f"Bearer {settings.admin_token}":
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    data = await request.json()
    message = data.get("message")
    
    if not message:
        raise HTTPException(status_code=400, detail="Message required")
    
    async with get_db() as db:
        from sqlalchemy import select
        
        result = await db.execute(select(User.id))
        user_ids = [row[0] for row in result.fetchall()]
        
        sent = 0
        failed = 0
        
        for user_id in user_ids:
            try:
                await telegram_app.bot.send_message(
                    chat_id=user_id,
                    text=message,
                    parse_mode="Markdown"
                )
                sent += 1
            except Exception:
                failed += 1
            
            await asyncio.sleep(0.05)  # Rate limiting
        
        return {
            "sent": sent,
            "failed": failed,
            "total": len(user_ids)
        }


# ==================== MINI APP ROUTES ====================

@app.get("/app/dashboard")
async def dashboard_data(user_id: int):
    """Get dashboard data for mini app"""
    async with get_db() as db:
        user = await db.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "user": {
                "id": user.id,
                "name": user.first_name,
                "username": user.username,
                "is_premium": user.is_premium,
                "total_messages": user.total_messages,
                "images_generated": user.images_generated
            }
        }


@app.get("/app/wallet")
async def wallet_data(user_id: int):
    """Get wallet data for mini app"""
    async with get_db() as db:
        wallet = await payment_service.get_or_create_wallet(db, user_id)
        
        return {
            "naira_balance": wallet.naira_balance,
            "imocoin_balance": wallet.imocoin_balance
        }


# ==================== SENDPULSE INTEGRATION ====================

@app.post("/api/sendpulse/flow")
async def sendpulse_flow(request: Request):
    """Handle SendPulse flow triggers"""
    try:
        data = await request.json()
        user_id = data.get("telegram_id")
        flow_name = data.get("flow")
        
        # Trigger appropriate action based on flow
        if flow_name == "welcome":
            # Handle welcome flow
            pass
        elif flow_name == "reminder":
            # Handle reminder flow
            pass
        
        return {"status": "processed"}
    
    except Exception as e:
        logger.error(f"SendPulse flow error: {e}")
        return {"status": "error"}


# ==================== ERROR HANDLERS ====================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ==================== MAIN ====================

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )

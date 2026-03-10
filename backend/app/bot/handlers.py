"""
Imoogle 5.0 Telegram Bot Handlers
Main message and command handlers for the Telegram bot.
"""

import asyncio
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction
from sqlalchemy import select, update as sql_update

from app.config import settings, SUBSCRIPTION_PLANS, COMPANION_PERSONAS, PIDGIN_PHRASES
from app.database import get_session
from app.database.models import User, Conversation, Message, UserTier
from app.services.ai_router import ai_router
from app.services.search import search_service
from app.services.image_gen import image_service
from app.services.voice import voice_service
from app.services.companion import companion_service
from app.services.weather import weather_service
from app.services.location import location_service
from app.services.media import media_service
from app.services.payments import payment_service
from app.services.bot_builder import bot_builder_service
from app.services.reminders import reminder_service
from app.services.documents import document_service


class BotHandlers:
    """Main bot handler class."""
    
    def __init__(self):
        pass
    
    # ==================== HELPER METHODS ====================
    
    async def get_or_create_user(self, telegram_user, db) -> User:
        """Get or create a user from Telegram user object."""
        result = await db.execute(
            select(User).where(User.telegram_id == telegram_user.id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        
        return user
    
    async def check_usage_limits(self, user: User, action: str = "message") -> tuple[bool, str]:
        """Check if user has exceeded usage limits."""
        plan = SUBSCRIPTION_PLANS.get(user.tier.value, SUBSCRIPTION_PLANS["free"])
        
        if action == "message":
            limit = plan["messages_per_day"]
            if limit != -1 and user.messages_today >= limit:
                return False, f"You've reached your daily message limit ({limit}). Upgrade your plan for more!"
        elif action == "image":
            limit = plan["image_generations"]
            if limit != -1 and user.images_today >= limit:
                return False, f"You've reached your daily image generation limit ({limit}). Upgrade for more!"
        elif action == "voice":
            limit = plan["voice_messages"]
            if limit != -1 and user.voice_today >= limit:
                return False, f"You've reached your daily voice message limit ({limit}). Upgrade for more!"
        
        return True, ""
    
    async def stream_response(
        self,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        text_generator,
    ):
        """Stream AI response with periodic updates."""
        message = await update.message.reply_text("...")
        
        full_response = ""
        buffer = ""
        last_update = 0
        
        async for chunk in text_generator:
            full_response += chunk
            buffer += chunk
            
            # Update every 20 characters or on sentence end
            if len(buffer) >= 20 or chunk in ".!?\n":
                try:
                    await message.edit_text(
                        full_response + "...",
                        parse_mode=ParseMode.MARKDOWN,
                    )
                    buffer = ""
                except Exception:
                    pass  # Ignore edit errors (rate limiting)
        
        # Final update
        try:
            await message.edit_text(full_response, parse_mode=ParseMode.MARKDOWN)
        except Exception:
            await message.edit_text(full_response)
        
        return full_response
    
    # ==================== COMMAND HANDLERS ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
            
            # Try to detect location
            location = None
            try:
                # Note: In real implementation, you'd get IP from webhook request
                location = await location_service.get_location()
            except Exception:
                pass
            
            if location:
                user.country = location.country
                user.city = location.city
                user.timezone = location.timezone
                user.use_pidgin = location_service.should_use_pidgin(location)
                await db.commit()
            
            # Create welcome message based on location
            name = user.first_name or "friend"
            
            if user.use_pidgin:
                welcome = f"""How far {name}! Welcome to **ImoogleAI** - Your personal AI assistant wey fit do everything!

Na Imoogle Technology create me, founded by Olajuwon (sidicode) and Tariq, software engineers wey dey based in Lagos.

**Wetin I fit do for you:**
- Chat with AI wey sabi everything
- Search internet give you current gist
- Generate fine fine images
- Send and receive voice messages
- Get music, movie, book recommendations
- Set reminders so you no go forget
- Imoogle Pay - send and receive money
- Create your own bot for your business

Use /help to see all my commands. Make we start!"""
            else:
                welcome = f"""Welcome {name}! I'm **ImoogleAI** - Your intelligent personal assistant that can do virtually anything!

I was created by Imoogle Technology, founded by Olajuwon (also known as sidicode) and Tariq, software engineers based in Lagos, Nigeria.

**What I can do:**
- Intelligent AI conversations
- Web search for current information  
- Generate beautiful images
- Voice messages (send & receive)
- Music, movie, book recommendations
- Set reminders and schedules
- Imoogle Pay - send & receive money
- Create your own custom bot

Use /help to see all commands. Let's get started!"""
            
            # Create keyboard
            keyboard = [
                [KeyboardButton("Chat with AI"), KeyboardButton("Search Web")],
                [KeyboardButton("Generate Image"), KeyboardButton("Voice Message")],
                [KeyboardButton("Recommendations"), KeyboardButton("My Account")],
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            
            await update.message.reply_text(
                welcome,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=reply_markup,
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
        
        if user.use_pidgin:
            help_text = """**ImoogleAI Commands:**

**Basic:**
/start - Start fresh conversation
/help - See this message
/about - Know who create me

**AI Features:**
/chat - Talk to AI
/search [query] - Search internet
/image [prompt] - Generate image
/voice - Send voice message

**Companion:**
/companion - Setup AI boyfriend/girlfriend
/personas - See available companions

**Media:**
/music [song] - Search music
/movie [title] - Search movies
/book [title] - Search books
/recommend - Get recommendations
/weather [city] - Check weather

**Productivity:**
/remind [time] [task] - Set reminder
/reminders - See your reminders
/document - Create document

**Money Matters (Nigeria only):**
/balance - Check your balance
/deposit - Add money
/send @user amount - Send money
/withdraw - Cash out
/subscribe - Upgrade plan

**Bot Builder:**
/createbot - Create your own bot
/mybots - Manage your bots

**Group Commands:**
/groupsettings - Configure group
/ban - Ban user
/mute - Mute user

Na so! Just ask me anything!"""
        else:
            help_text = """**ImoogleAI Commands:**

**Basic:**
/start - Start fresh conversation
/help - Show this help message
/about - About ImoogleAI

**AI Features:**
/chat - Chat with AI
/search [query] - Search the web
/image [prompt] - Generate an image
/voice - Send voice message

**Companion Mode:**
/companion - Setup AI companion
/personas - View available personas

**Media:**
/music [song] - Search for music
/movie [title] - Search for movies
/book [title] - Search for books
/recommend - Get recommendations
/weather [city] - Get weather info

**Productivity:**
/remind [time] [task] - Set a reminder
/reminders - View your reminders
/document - Create a document

**Imoogle Pay (Nigeria):**
/balance - Check wallet balance
/deposit - Add funds
/send @user amount - Transfer money
/withdraw - Withdraw to bank
/subscribe - Upgrade subscription

**Bot Builder:**
/createbot - Create your own bot
/mybots - Manage your bots

**Group Commands:**
/groupsettings - Configure group settings
/ban - Ban a user
/mute - Mute a user

Just ask me anything!"""
        
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN)
    
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /about command."""
        about_text = """**About ImoogleAI**

ImoogleAI is an advanced AI assistant developed by **Imoogle Technology**, a Nigerian tech company founded by:

- **Olajuwon** (sidicode) - Co-founder & Lead Developer
- **Tariq** - Co-founder & Software Engineer

Based in Lagos, Nigeria, our mission is to make AI accessible and useful for everyone, especially across Africa.

**Version:** 4.0
**Powered by:** Multiple AI models including Mistral, Groq, and more

**Features:**
- Intelligent conversations
- Web search
- Image generation
- Voice messages
- Music/Movie/Book recommendations
- Imoogle Pay (P2P payments)
- Custom bot creation
- And much more!

**Contact:** @sidicode

Thank you for using ImoogleAI!"""
        
        await update.message.reply_text(about_text, parse_mode=ParseMode.MARKDOWN)
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command."""
        query = ' '.join(context.args) if context.args else None
        
        if not query:
            await update.message.reply_text("Please provide a search query. Example: /search latest tech news")
            return
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
        
        # Send searching indicator
        if user.use_pidgin:
            searching_msg = await update.message.reply_text("Abeg wait small, I dey search...")
        else:
            searching_msg = await update.message.reply_text("Searching...")
        
        await update.message.chat.send_action(ChatAction.TYPING)
        
        # Perform search
        results = await search_service.search(query)
        
        # Delete searching message
        await searching_msg.delete()
        
        # Format and send results
        formatted = search_service.format_results(results, user.use_pidgin)
        await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    async def image_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /image command."""
        prompt = ' '.join(context.args) if context.args else None
        
        if not prompt:
            await update.message.reply_text("Please describe the image you want. Example: /image a beautiful sunset over Lagos")
            return
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
            
            # Check limits
            allowed, msg = await self.check_usage_limits(user, "image")
            if not allowed:
                await update.message.reply_text(msg)
                return
        
        # Send generating indicator
        if user.use_pidgin:
            gen_msg = await update.message.reply_text("I dey create your image, wait small...")
        else:
            gen_msg = await update.message.reply_text("Generating your image...")
        
        await update.message.chat.send_action(ChatAction.UPLOAD_PHOTO)
        
        # Generate image
        image_bytes = await image_service.generate(prompt, add_branding=True)
        
        await gen_msg.delete()
        
        if image_bytes:
            # Update usage
            async with get_session() as db:
                await db.execute(
                    sql_update(User)
                    .where(User.id == user.id)
                    .values(images_today=User.images_today + 1)
                )
                await db.commit()
            
            await update.message.reply_photo(
                photo=image_bytes,
                caption=f"Generated by ImoogleAI\n\nPrompt: {prompt[:100]}...",
            )
        else:
            if user.use_pidgin:
                await update.message.reply_text("Wahala! I no fit generate that image. Try another description.")
            else:
                await update.message.reply_text("Sorry, I couldn't generate that image. Please try a different description.")
    
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /weather command."""
        city = ' '.join(context.args) if context.args else None
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
        
        if not city:
            city = user.city or "Lagos"
        
        weather = await weather_service.get_current_weather(city=city)
        
        if weather:
            formatted = weather_service.format_weather(weather, user.use_pidgin)
            await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN)
        else:
            if user.use_pidgin:
                await update.message.reply_text(f"I no fit find weather for {city}. Make sure say you spell am correct.")
            else:
                await update.message.reply_text(f"Couldn't find weather for {city}. Please check the spelling.")
    
    async def music_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /music command."""
        query = ' '.join(context.args) if context.args else None
        
        if not query:
            await update.message.reply_text("What song are you looking for? Example: /music Burna Boy Last Last")
            return
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
        
        await update.message.chat.send_action(ChatAction.TYPING)
        
        results = await media_service.search_music(query)
        formatted = media_service.format_music_results(results, user.use_pidgin)
        
        await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    async def movie_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /movie command."""
        query = ' '.join(context.args) if context.args else None
        
        if not query:
            await update.message.reply_text("What movie are you looking for? Example: /movie The Batman")
            return
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
        
        await update.message.chat.send_action(ChatAction.TYPING)
        
        results = await media_service.search_movies(query)
        formatted = media_service.format_movie_results(results, user.use_pidgin)
        
        await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    async def book_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /book command."""
        query = ' '.join(context.args) if context.args else None
        
        if not query:
            await update.message.reply_text("What book are you looking for? Example: /book Atomic Habits")
            return
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
        
        await update.message.chat.send_action(ChatAction.TYPING)
        
        results = await media_service.search_books(query)
        formatted = media_service.format_book_results(results, user.use_pidgin)
        
        await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN, disable_web_page_preview=True)
    
    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command."""
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
            
            # Check if in Nigeria
            if user.country and user.country.upper() != "NIGERIA" and user.country.upper() != "NG":
                await update.message.reply_text(
                    "Imoogle Pay is currently only available in Nigeria. Coming soon to other African countries!"
                )
                return
            
            balance = await payment_service.get_balance(db, user.id)
            formatted = payment_service.format_balance(balance, user.use_pidgin)
            
            await update.message.reply_text(formatted, parse_mode=ParseMode.MARKDOWN)
    
    async def companion_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /companion command."""
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
            
            # Check subscription
            plan = SUBSCRIPTION_PLANS.get(user.tier.value, {})
            if not plan.get("companion_mode", False):
                await update.message.reply_text(
                    "Companion mode is available on Basic plan and above. Use /subscribe to upgrade!"
                )
                return
        
        # Show persona selection
        keyboard = []
        row = []
        for name, persona in COMPANION_PERSONAS.items():
            emoji = "♀️" if persona["gender"] == "female" else "♂️"
            row.append(InlineKeyboardButton(
                f"{emoji} {persona['name']} ({persona['country'][:3]})",
                callback_data=f"companion_{name}"
            ))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("Cancel", callback_data="companion_cancel")])
        
        await update.message.reply_text(
            "Choose your companion:\n\n"
            "♀️ = Female | ♂️ = Male\n"
            "Select someone you'd like to chat with:",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
    
    async def remind_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /remind command."""
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /remind [time] [task]\n\n"
                "Examples:\n"
                "/remind in 30 minutes call mom\n"
                "/remind tomorrow meeting with team\n"
                "/remind 2024-03-15 14:00 dentist appointment"
            )
            return
        
        # Parse time and task
        text = ' '.join(context.args)
        
        # Simple parsing: first part before common task words is time
        time_keywords = ["to", "about", "for", "-"]
        time_str = text
        task = "Reminder"
        
        for kw in time_keywords:
            if f" {kw} " in text:
                parts = text.split(f" {kw} ", 1)
                time_str = parts[0]
                task = parts[1] if len(parts) > 1 else "Reminder"
                break
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
            
            result = await reminder_service.create_reminder(
                db=db,
                user_id=user.id,
                title=task,
                time_str=time_str,
                timezone=user.timezone,
            )
        
        if result["success"]:
            if user.use_pidgin:
                await update.message.reply_text(f"I don set reminder for you!\n\n{task}\nWhen: {result['remind_at']}")
            else:
                await update.message.reply_text(f"Reminder set!\n\n{task}\nWhen: {result['remind_at']}")
        else:
            await update.message.reply_text(result["error"])
    
    # ==================== MESSAGE HANDLER ====================
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle regular text messages."""
        if not update.message or not update.message.text:
            return
        
        text = update.message.text
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
            
            # Check limits
            allowed, msg = await self.check_usage_limits(user, "message")
            if not allowed:
                await update.message.reply_text(msg)
                return
            
            # Update message count
            await db.execute(
                sql_update(User)
                .where(User.id == user.id)
                .values(messages_today=User.messages_today + 1)
            )
            await db.commit()
        
        # Show typing indicator
        await update.message.chat.send_action(ChatAction.TYPING)
        
        # Get conversation context
        messages = [{"role": "user", "content": text}]
        
        # Stream AI response
        async def generate():
            async for chunk in ai_router.chat(
                messages=messages,
                user_name=user.first_name or "User",
                user_country=user.country,
                use_pidgin=user.use_pidgin,
                companion_mode=user.companion_enabled,
                companion_persona=COMPANION_PERSONAS.get(user.companion_persona) if user.companion_persona else None,
                companion_nickname=user.companion_nickname,
            ):
                yield chunk
        
        await self.stream_response(update, context, generate())
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages."""
        if not update.message.voice:
            return
        
        async with get_session() as db:
            user = await self.get_or_create_user(update.effective_user, db)
            
            # Check limits
            allowed, msg = await self.check_usage_limits(user, "voice")
            if not allowed:
                await update.message.reply_text(msg)
                return
        
        # Download voice file
        voice_file = await update.message.voice.get_file()
        voice_bytes = await voice_file.download_as_bytearray()
        
        # Transcribe
        if user.use_pidgin:
            await update.message.reply_text("I dey listen to your voice...")
        else:
            await update.message.reply_text("Processing your voice message...")
        
        transcription = await voice_service.transcribe(bytes(voice_bytes))
        
        if not transcription:
            await update.message.reply_text("Sorry, I couldn't understand that voice message. Please try again.")
            return
        
        # Show what was heard
        await update.message.reply_text(f"I heard: _{transcription}_", parse_mode=ParseMode.MARKDOWN)
        
        # Process as regular message
        update.message.text = transcription
        await self.handle_message(update, context)
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards."""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith("companion_"):
            persona_name = data.replace("companion_", "")
            
            if persona_name == "cancel":
                await query.edit_message_text("Companion setup cancelled.")
                return
            
            async with get_session() as db:
                user = await self.get_or_create_user(query.from_user, db)
                
                result = await companion_service.setup_companion(
                    db=db,
                    user_id=user.id,
                    persona_name=persona_name,
                    nickname=user.first_name,
                )
            
            if result["success"]:
                await query.edit_message_text(result["welcome_message"], parse_mode=ParseMode.MARKDOWN)
            else:
                await query.edit_message_text(f"Error: {result['error']}")


# Create handler instance
bot_handlers = BotHandlers()

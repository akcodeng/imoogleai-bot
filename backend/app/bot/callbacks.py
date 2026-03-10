"""
Imoogle 5.0 - Callback Query Handlers
Handles all inline keyboard button clicks
"""

import asyncio
import logging
from telegram import Update, CallbackQuery
from telegram.ext import ContextTypes
from telegram.constants import ParseMode, ChatAction

from app.database import get_db
from app.database.models import User, Companion, Wallet, UserBot, BotSubscription
from app.services.ai_router import AIRouter
from app.services.companion import CompanionService
from app.services.payments import PaymentService
from app.services.bot_builder import BotBuilderService
from app.services.image_gen import ImageService
from app.services.media import MediaService
from app.services.weather import WeatherService
from app.bot.keyboards import keyboards
from app.bot.messages import messages
from app.config import settings

logger = logging.getLogger(__name__)


class CallbackHandler:
    """Handles all callback queries from inline keyboards"""
    
    def __init__(self):
        self.ai_router = AIRouter()
        self.companion_service = CompanionService()
        self.payment_service = PaymentService()
        self.bot_builder = BotBuilderService()
        self.image_service = ImageService()
        self.media_service = MediaService()
        self.weather_service = WeatherService()
    
    async def handle(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main callback query router"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        user_id = query.from_user.id
        
        # Get user from database
        async with get_db() as db:
            user = await db.get(User, user_id)
            if not user:
                await query.edit_message_text("Please /start the bot first!")
                return
        
        # Route to appropriate handler
        try:
            if data.startswith("menu:"):
                await self._handle_menu(query, user, data)
            elif data.startswith("mode:"):
                await self._handle_mode(query, user, data)
            elif data.startswith("companion:"):
                await self._handle_companion(query, user, data, context)
            elif data.startswith("pay:"):
                await self._handle_pay(query, user, data, context)
            elif data.startswith("deposit:"):
                await self._handle_deposit(query, user, data, context)
            elif data.startswith("pin:"):
                await self._handle_pin(query, user, data, context)
            elif data.startswith("botbuilder:"):
                await self._handle_bot_builder(query, user, data, context)
            elif data.startswith("botplan:"):
                await self._handle_bot_plan(query, user, data, context)
            elif data.startswith("bot:"):
                await self._handle_bot_manage(query, user, data, context)
            elif data.startswith("group:"):
                await self._handle_group(query, user, data)
            elif data.startswith("spam:"):
                await self._handle_spam_settings(query, user, data)
            elif data.startswith("search:"):
                await self._handle_search(query, user, data, context)
            elif data.startswith("media:"):
                await self._handle_media(query, user, data)
            elif data.startswith("music:"):
                await self._handle_music(query, user, data, context)
            elif data.startswith("movie:"):
                await self._handle_movie(query, user, data, context)
            elif data.startswith("book:"):
                await self._handle_book(query, user, data, context)
            elif data.startswith("image:"):
                await self._handle_image(query, user, data, context)
            elif data.startswith("imgstyle:"):
                await self._handle_image_style(query, user, data, context)
            elif data.startswith("img:"):
                await self._handle_image_action(query, user, data, context)
            elif data.startswith("voice:"):
                await self._handle_voice(query, user, data, context)
            elif data.startswith("doc:"):
                await self._handle_documents(query, user, data)
            elif data.startswith("template:"):
                await self._handle_template(query, user, data, context)
            elif data.startswith("weather:"):
                await self._handle_weather(query, user, data, context)
            elif data.startswith("settings:"):
                await self._handle_settings(query, user, data)
            elif data.startswith("personality:"):
                await self._handle_personality(query, user, data)
            elif data.startswith("notif:"):
                await self._handle_notifications(query, user, data)
            elif data.startswith("lang:"):
                await self._handle_language(query, user, data)
            elif data.startswith("premium:"):
                await self._handle_premium(query, user, data, context)
            elif data.startswith("help:"):
                await self._handle_help(query, user, data)
            elif data.startswith("onboard:"):
                await self._handle_onboarding(query, user, data, context)
            elif data.startswith("interest:"):
                await self._handle_interest(query, user, data)
            else:
                logger.warning(f"Unknown callback data: {data}")
        
        except Exception as e:
            logger.error(f"Error handling callback {data}: {e}")
            await query.edit_message_text(
                messages.error_generic(user.language),
                parse_mode=ParseMode.MARKDOWN
            )
    
    # ==================== MENU HANDLERS ====================
    
    async def _handle_menu(self, query: CallbackQuery, user: User, data: str):
        """Handle menu navigation"""
        action = data.split(":")[1]
        
        if action == "main":
            await query.edit_message_text(
                f"🏠 *Main Menu*\n\nHey {user.first_name}! What would you like to do?",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.main_menu(user.is_premium, user.country)
            )
    
    async def _handle_mode(self, query: CallbackQuery, user: User, data: str):
        """Handle mode switching"""
        mode = data.split(":")[1]
        
        async with get_db() as db:
            user.current_mode = mode
            db.add(user)
            await db.commit()
        
        if mode == "chat":
            await query.edit_message_text(
                "🤖 *AI Chat Mode*\n\nI'm ready to help! Ask me anything.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.main_menu(user.is_premium, user.country)
            )
    
    # ==================== COMPANION HANDLERS ====================
    
    async def _handle_companion(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle companion-related callbacks"""
        action = data.split(":")[1]
        
        if action == "menu":
            await query.edit_message_text(
                "💕 *Companion Mode*\n\nChoose your AI companion who will always be there for you!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_menu()
            )
        
        elif action == "choose":
            await query.edit_message_text(
                "💕 *Choose Your Companion*\n\nWho would you like as your AI partner?",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_select_gender()
            )
        
        elif action == "gender_female":
            await query.edit_message_text(
                "👩 *Choose Your Girlfriend*\n\nSelect your AI girlfriend:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_female_personas()
            )
        
        elif action == "gender_male":
            await query.edit_message_text(
                "👨 *Choose Your Boyfriend*\n\nSelect your AI boyfriend:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_male_personas()
            )
        
        elif action in ["mayowa", "oreoluwa", "suri", "tubosun", "juwon", "usman", "emma", "ashley", "isabella", "james", "michael", "carlos"]:
            # Activate companion
            persona = action
            async with get_db() as db:
                companion = await self.companion_service.activate_companion(
                    db, user.id, persona
                )
                user.current_mode = "companion"
                user.active_companion_id = companion.id
                db.add(user)
                await db.commit()
            
            intro_message = messages.companion_intro(user.first_name, persona, user.language)
            await query.edit_message_text(
                intro_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_interaction()
            )
        
        elif action == "current":
            async with get_db() as db:
                if user.active_companion_id:
                    companion = await db.get(Companion, user.active_companion_id)
                    if companion:
                        await query.edit_message_text(
                            f"💕 *Your Current Companion*\n\n"
                            f"👤 *Name:* {companion.persona_name.title()}\n"
                            f"❤️ *Relationship Level:* {companion.relationship_level}/100\n"
                            f"💬 *Messages Exchanged:* {companion.total_messages}\n",
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=keyboards.companion_interaction()
                        )
                        return
            
            await query.edit_message_text(
                "You don't have an active companion yet. Choose one!",
                reply_markup=keyboards.companion_menu()
            )
        
        elif action == "settings":
            await query.edit_message_text(
                "⚙️ *Companion Settings*\n\nCustomize your companion experience:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_menu()
            )
        
        elif action in ["love", "hug", "kiss", "gift"]:
            # Quick interaction responses
            responses = {
                "love": "💕 Aww, I love you too! You make me so happy! 🥰",
                "hug": "🤗 *hugs you tight* I needed that! You're the best! 💖",
                "kiss": "💋 *blushes* That was so sweet! I'm blushing! 😊",
                "gift": "🎁 Oh my! You're so thoughtful! Thank you, my love! 💝"
            }
            await query.answer(responses.get(action, "💕"), show_alert=True)
        
        elif action == "voice":
            await query.edit_message_text(
                "🎙 *Voice Call Mode*\n\nSend me a voice message and I'll respond with my voice too!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_interaction()
            )
        
        elif action == "chat":
            await query.edit_message_text(
                "💬 Let's keep chatting! Just type your message...",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.companion_interaction()
            )
    
    # ==================== PAYMENT HANDLERS ====================
    
    async def _handle_pay(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle payment-related callbacks"""
        action = data.split(":")[1]
        
        if user.country not in ["NG", "GH", "KE", "ZA", "EG"]:
            await query.edit_message_text(
                messages.error_not_available("Imoogle Pay", user.country, user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.main_menu(user.is_premium, user.country)
            )
            return
        
        if action == "menu":
            await query.edit_message_text(
                "💳 *Imoogle Pay*\n\nSend, receive, and manage your money!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.pay_menu()
            )
        
        elif action == "balance":
            async with get_db() as db:
                wallet = await self.payment_service.get_or_create_wallet(db, user.id)
                await query.edit_message_text(
                    messages.pay_balance(wallet.naira_balance, wallet.imocoin_balance, user.language),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.pay_menu()
                )
        
        elif action == "deposit":
            await query.edit_message_text(
                "📥 *Deposit Funds*\n\nSelect an amount to deposit:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.pay_deposit_amounts()
            )
        
        elif action == "withdraw":
            await query.edit_message_text(
                "📤 *Withdraw Funds*\n\nEnter the amount you want to withdraw (minimum ₦500):",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "withdraw_amount"
        
        elif action == "send":
            await query.edit_message_text(
                "💸 *Send Money*\n\nEnter the username or Imoogle ID of the recipient:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "send_recipient"
        
        elif action == "history":
            async with get_db() as db:
                transactions = await self.payment_service.get_transaction_history(db, user.id, limit=10)
                if not transactions:
                    text = "📊 *Transaction History*\n\nNo transactions yet."
                else:
                    text = "📊 *Transaction History*\n\n"
                    for tx in transactions:
                        symbol = "📥" if tx.transaction_type in ["deposit", "receive"] else "📤"
                        text += f"{symbol} {tx.transaction_type.title()}: ₦{tx.amount:,.2f}\n"
                        text += f"   _{tx.created_at.strftime('%d %b %Y, %H:%M')}_\n\n"
                
                await query.edit_message_text(
                    text,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.pay_menu()
                )
        
        elif action == "settings":
            await query.edit_message_text(
                "⚙️ *Payment Settings*\n\n• Change PIN\n• Link Bank Account\n• Transaction Limits",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.pay_menu()
            )
        
        elif action == "buy_imocoin":
            await query.edit_message_text(
                "🪙 *Buy ImoCoin*\n\nImoCoin is Imoogle's virtual currency!\n\n"
                "Rate: ₦100 = 1 IMC\n\nEnter the amount of Naira you want to convert:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "imocoin_amount"
    
    async def _handle_deposit(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle deposit amount selection"""
        amount_str = data.split(":")[1]
        
        if amount_str == "custom":
            await query.edit_message_text(
                "💵 Enter the amount you want to deposit (minimum ₦500):",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "deposit_amount"
        else:
            amount = int(amount_str)
            # Generate payment link
            async with get_db() as db:
                payment_url = await self.payment_service.initialize_deposit(
                    db, user.id, amount
                )
                
                await query.edit_message_text(
                    f"💳 *Deposit ₦{amount:,}*\n\n"
                    f"Click the button below to complete your payment:\n\n"
                    f"[Pay Now]({payment_url})",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.pay_menu()
                )
    
    async def _handle_pin(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle PIN entry"""
        key = data.split(":")[1]
        
        if "pin_entry" not in context.user_data:
            context.user_data["pin_entry"] = ""
        
        if key == "backspace":
            context.user_data["pin_entry"] = context.user_data["pin_entry"][:-1]
        elif key == "submit":
            pin = context.user_data["pin_entry"]
            # Verify PIN and process pending transaction
            context.user_data["pin_entry"] = ""
            await query.answer("Processing...", show_alert=False)
        else:
            if len(context.user_data["pin_entry"]) < 4:
                context.user_data["pin_entry"] += key
        
        # Show PIN progress
        pin_display = "●" * len(context.user_data.get("pin_entry", "")) + "○" * (4 - len(context.user_data.get("pin_entry", "")))
        await query.edit_message_text(
            f"🔐 *Enter Your PIN*\n\n`{pin_display}`",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboards.pay_enter_pin()
        )
    
    # ==================== BOT BUILDER HANDLERS ====================
    
    async def _handle_bot_builder(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot builder callbacks"""
        action = data.split(":")[1]
        
        if action == "start" or action == "menu":
            await query.edit_message_text(
                messages.bot_builder_intro(user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.bot_builder_menu()
            )
        
        elif action == "create":
            await query.edit_message_text(
                "🆕 *Create New Bot*\n\n"
                "First, I need your bot token from @BotFather.\n\n"
                "1. Go to @BotFather on Telegram\n"
                "2. Send /newbot and follow the steps\n"
                "3. Copy the token and send it here",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "bot_token"
        
        elif action == "mybots":
            async with get_db() as db:
                bots = await self.bot_builder.get_user_bots(db, user.id)
                
                if not bots:
                    await query.edit_message_text(
                        "📋 *My Bots*\n\nYou haven't created any bots yet.",
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboards.bot_builder_menu()
                    )
                else:
                    text = "📋 *My Bots*\n\n"
                    for bot in bots:
                        status = "🟢" if bot.is_active else "🔴"
                        text += f"{status} *{bot.bot_username}*\n"
                        text += f"   Subscribers: {bot.subscriber_count}\n\n"
                    
                    await query.edit_message_text(
                        text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=keyboards.bot_builder_menu()
                    )
        
        elif action == "subscription":
            await query.edit_message_text(
                messages.bot_builder_plans(user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.bot_builder_plans()
            )
        
        elif action == "analytics":
            async with get_db() as db:
                stats = await self.bot_builder.get_analytics(db, user.id)
                await query.edit_message_text(
                    f"📊 *Bot Analytics*\n\n"
                    f"📈 *Total Bots:* {stats.get('total_bots', 0)}\n"
                    f"👥 *Total Subscribers:* {stats.get('total_subscribers', 0)}\n"
                    f"💬 *Messages Today:* {stats.get('messages_today', 0)}\n"
                    f"📢 *Broadcasts Sent:* {stats.get('broadcasts_sent', 0)}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.bot_builder_menu()
                )
        
        elif action == "tutorial":
            await query.edit_message_text(
                "📖 *Bot Builder Tutorial*\n\n"
                "*Step 1:* Create a bot with @BotFather\n"
                "*Step 2:* Copy the token and paste it here\n"
                "*Step 3:* Configure auto-replies\n"
                "*Step 4:* Enable AI responses (optional)\n"
                "*Step 5:* Start broadcasting to subscribers!\n\n"
                "Need help? Contact @ImoogleSupport",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.bot_builder_menu()
            )
        
        elif action == "features_done":
            # Process selected features
            features = context.user_data.get("selected_features", [])
            await query.edit_message_text(
                f"✅ *Features Selected*\n\n"
                f"Your bot will have: {', '.join(features) if features else 'Basic features'}\n\n"
                f"Now let's set up your bot's welcome message...",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "bot_welcome_message"
    
    async def _handle_bot_plan(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle bot plan selection"""
        plan = data.split(":")[1]
        
        prices = {
            "starter": 1500,
            "growth": 2600,
            "business": 5000,
            "enterprise": 15000
        }
        
        price = prices.get(plan, 1500)
        
        await query.edit_message_text(
            f"💳 *{plan.title()} Plan*\n\n"
            f"Price: ₦{price:,}/month\n\n"
            f"Pay with Imoogle Pay to activate immediately!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboards.pay_menu()
        )
        
        context.user_data["pending_plan"] = plan
        context.user_data["pending_price"] = price
    
    async def _handle_bot_manage(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle individual bot management"""
        parts = data.split(":")
        bot_id = parts[1]
        action = parts[2] if len(parts) > 2 else "view"
        
        async with get_db() as db:
            bot = await db.get(UserBot, bot_id)
            
            if not bot or bot.owner_id != user.id:
                await query.answer("Bot not found!", show_alert=True)
                return
            
            if action == "settings":
                await query.edit_message_text(
                    f"⚙️ *Settings for {bot.bot_username}*\n\n"
                    f"Configure your bot's behavior:",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.bot_manage(bot_id)
                )
            
            elif action == "stats":
                await query.edit_message_text(
                    f"📊 *Stats for {bot.bot_username}*\n\n"
                    f"👥 Subscribers: {bot.subscriber_count}\n"
                    f"💬 Messages: {bot.total_messages}\n"
                    f"📈 Active: {'Yes' if bot.is_active else 'No'}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.bot_manage(bot_id)
                )
            
            elif action == "broadcast":
                await query.edit_message_text(
                    "📢 *Send Broadcast*\n\n"
                    "Type your message to send to all subscribers:",
                    parse_mode=ParseMode.MARKDOWN
                )
                context.user_data["awaiting"] = "broadcast_message"
                context.user_data["broadcast_bot_id"] = bot_id
            
            elif action == "restart":
                await self.bot_builder.restart_bot(db, bot_id)
                await query.answer("Bot restarted!", show_alert=True)
            
            elif action == "delete":
                await query.edit_message_text(
                    f"🗑 *Delete {bot.bot_username}?*\n\n"
                    f"This action cannot be undone!",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.bot_manage(bot_id)
                )
    
    # ==================== GROUP HANDLERS ====================
    
    async def _handle_group(self, query: CallbackQuery, user: User, data: str):
        """Handle group moderation callbacks"""
        action = data.split(":")[1]
        
        if action == "tools":
            await query.edit_message_text(
                "👥 *Group Moderation Tools*\n\n"
                "Add me to your group as admin to use these features!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.group_tools()
            )
        
        elif action == "antispam":
            await query.edit_message_text(
                "🛡 *Anti-Spam Settings*\n\n"
                "Configure what to block in your group:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.group_antispam_settings()
            )
        
        elif action == "welcome":
            await query.edit_message_text(
                "📋 *Welcome Message*\n\n"
                "Send me the welcome message for new members.\n"
                "Use {name} for member's name and {group} for group name.",
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif action == "warnings":
            await query.edit_message_text(
                "⚠️ *Warning System*\n\n"
                "Set how many warnings before action:\n"
                "• 3 warnings = mute\n"
                "• 5 warnings = kick\n"
                "• 7 warnings = ban",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.group_tools()
            )
        
        elif action == "analytics":
            await query.edit_message_text(
                "📊 *Group Analytics*\n\n"
                "Select a group to view analytics:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.group_tools()
            )
    
    async def _handle_spam_settings(self, query: CallbackQuery, user: User, data: str):
        """Handle spam filter settings"""
        setting = data.split(":")[1]
        await query.answer(f"{setting.title()} filter toggled!", show_alert=True)
    
    # ==================== MEDIA HANDLERS ====================
    
    async def _handle_media(self, query: CallbackQuery, user: User, data: str):
        """Handle media menu callbacks"""
        media_type = data.split(":")[1]
        
        if media_type == "music":
            await query.edit_message_text(
                "🎵 *Music*\n\nDiscover and explore music!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_music_options()
            )
        
        elif media_type == "movies":
            await query.edit_message_text(
                "🎬 *Movies & TV*\n\nFind your next watch!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_movie_options()
            )
        
        elif media_type == "books":
            await query.edit_message_text(
                "📚 *Books*\n\nDiscover your next read!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_book_options()
            )
    
    async def _handle_search(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle search callbacks"""
        search_type = data.split(":")[1]
        
        if search_type == "menu":
            await query.edit_message_text(
                "🔍 *Search*\n\nWhat would you like to search for?",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.search_menu()
            )
        else:
            await query.edit_message_text(
                f"🔍 *{search_type.title()} Search*\n\nType your search query:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = f"search_{search_type}"
    
    async def _handle_music(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle music callbacks"""
        action = data.split(":")[1]
        
        if action == "search":
            await query.edit_message_text(
                "🔍 *Search Music*\n\nEnter song name or artist:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "music_search"
        
        elif action == "trending":
            await query.edit_message_text(
                "🔥 *Fetching trending music...*",
                parse_mode=ParseMode.MARKDOWN
            )
            tracks = await self.media_service.get_trending_music()
            await query.edit_message_text(
                messages.music_recommendation(tracks, user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_music_options()
            )
        
        elif action == "recommend":
            await query.edit_message_text(
                "🎧 *Getting personalized recommendations...*",
                parse_mode=ParseMode.MARKDOWN
            )
            tracks = await self.media_service.get_music_recommendations(user.id)
            await query.edit_message_text(
                messages.music_recommendation(tracks, user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_music_options()
            )
        
        elif action == "lyrics":
            await query.edit_message_text(
                "📜 *Song Lyrics*\n\nEnter the song name:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "lyrics_search"
    
    async def _handle_movie(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle movie callbacks"""
        action = data.split(":")[1]
        
        if action == "search":
            await query.edit_message_text(
                "🔍 *Search Movies*\n\nEnter movie or TV show name:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "movie_search"
        
        elif action == "trending":
            movies = await self.media_service.get_trending_movies()
            await query.edit_message_text(
                messages.movie_recommendation(movies, user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_movie_options()
            )
        
        elif action == "recommend":
            movies = await self.media_service.get_movie_recommendations(user.id)
            await query.edit_message_text(
                messages.movie_recommendation(movies, user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_movie_options()
            )
        
        elif action == "tvshows":
            shows = await self.media_service.get_trending_tv()
            await query.edit_message_text(
                "📺 *Trending TV Shows*\n\n" + "\n".join([
                    f"*{i}.* {s['title']} - ⭐ {s['rating']}/10"
                    for i, s in enumerate(shows[:10], 1)
                ]),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_movie_options()
            )
    
    async def _handle_book(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle book callbacks"""
        action = data.split(":")[1]
        
        if action == "search":
            await query.edit_message_text(
                "🔍 *Search Books*\n\nEnter book title or author:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "book_search"
        
        elif action == "bestsellers":
            books = await self.media_service.get_bestseller_books()
            text = "📚 *Bestseller Books*\n\n"
            for i, book in enumerate(books[:10], 1):
                text += f"*{i}.* {book['title']}\n   📖 {book['author']}\n\n"
            await query.edit_message_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_book_options()
            )
        
        elif action == "recommend":
            books = await self.media_service.get_book_recommendations(user.id)
            text = "📖 *Recommended Books*\n\n"
            for i, book in enumerate(books[:10], 1):
                text += f"*{i}.* {book['title']}\n   📖 {book['author']}\n\n"
            await query.edit_message_text(
                text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.media_book_options()
            )
        
        elif action == "summary":
            await query.edit_message_text(
                "📝 *Book Summary*\n\nEnter the book title:",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "book_summary"
    
    # ==================== IMAGE HANDLERS ====================
    
    async def _handle_image(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle image generation callbacks"""
        action = data.split(":")[1]
        
        if action == "create":
            await query.edit_message_text(
                "🎨 *Create Image*\n\nChoose a style for your image:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.image_style_select()
            )
    
    async def _handle_image_style(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle image style selection"""
        style = data.split(":")[1]
        context.user_data["image_style"] = style
        
        await query.edit_message_text(
            f"🎨 *{style.title()} Style Selected*\n\n"
            "Now describe what you want me to create:",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data["awaiting"] = "image_prompt"
    
    async def _handle_image_action(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle actions on generated images"""
        parts = data.split(":")
        image_id = parts[1]
        action = parts[2]
        
        if action == "regen":
            await query.answer("Regenerating image...", show_alert=False)
            # Regenerate logic here
        elif action == "enhance":
            await query.answer("Enhancing image...", show_alert=False)
        elif action == "variations":
            await query.answer("Creating variations...", show_alert=False)
        elif action == "save":
            await query.answer("Saved to your gallery!", show_alert=True)
    
    # ==================== VOICE HANDLERS ====================
    
    async def _handle_voice(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice mode callbacks"""
        action = data.split(":")[1]
        
        if action == "enable":
            await query.edit_message_text(
                "🎙 *Voice Mode*\n\nConfigure your voice experience:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.voice_mode_options()
            )
        
        elif action == "start":
            async with get_db() as db:
                user.voice_mode = True
                db.add(user)
                await db.commit()
            
            await query.edit_message_text(
                "🎙 *Voice Mode Enabled!*\n\n"
                "Send me a voice message and I'll respond with my voice!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.voice_mode_options()
            )
        
        elif action == "female":
            context.user_data["voice_gender"] = "female"
            await query.answer("Voice set to Female!", show_alert=True)
        
        elif action == "male":
            context.user_data["voice_gender"] = "male"
            await query.answer("Voice set to Male!", show_alert=True)
        
        elif action == "v2v":
            async with get_db() as db:
                user.voice_to_voice = True
                db.add(user)
                await db.commit()
            
            await query.edit_message_text(
                "🎙 *Voice-to-Voice Mode Enabled!*\n\n"
                "Now I'll always respond with voice when you send voice messages!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.voice_mode_options()
            )
    
    # ==================== DOCUMENT HANDLERS ====================
    
    async def _handle_documents(self, query: CallbackQuery, user: User, data: str):
        """Handle document callbacks"""
        action = data.split(":")[1]
        
        if action == "menu":
            await query.edit_message_text(
                "📝 *Documents*\n\nCreate professional documents with AI!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.documents_menu()
            )
        
        elif action == "create":
            await query.edit_message_text(
                "📄 *Create Document*\n\nChoose a template:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.document_templates()
            )
        
        elif action == "list":
            await query.edit_message_text(
                "📋 *My Documents*\n\nNo documents yet. Create one!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.documents_menu()
            )
    
    async def _handle_template(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle document template selection"""
        template = data.split(":")[1]
        context.user_data["doc_template"] = template
        
        prompts = {
            "business_letter": "Please provide:\n1. Recipient name\n2. Subject\n3. Main content",
            "resume": "Please provide:\n1. Your full name\n2. Contact info\n3. Work experience\n4. Education",
            "report": "Please provide:\n1. Report title\n2. Main sections/content",
            "proposal": "Please provide:\n1. Project name\n2. Objective\n3. Scope\n4. Timeline",
            "invoice": "Please provide:\n1. Client name\n2. Items/services\n3. Amounts",
            "contract": "Please provide:\n1. Parties involved\n2. Terms\n3. Duration"
        }
        
        await query.edit_message_text(
            f"📄 *{template.replace('_', ' ').title()}*\n\n{prompts.get(template, 'Describe your document:')}",
            parse_mode=ParseMode.MARKDOWN
        )
        context.user_data["awaiting"] = "document_content"
    
    # ==================== WEATHER HANDLERS ====================
    
    async def _handle_weather(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle weather callbacks"""
        action = data.split(":")[1]
        
        if action == "current":
            if user.city:
                weather = await self.weather_service.get_weather(user.city)
                await query.edit_message_text(
                    messages.weather_report(weather, user.language),
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.main_menu(user.is_premium, user.country)
                )
            else:
                await query.edit_message_text(
                    "🌤 *Weather*\n\nPlease share your location or enter a city name:",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboards.location_keyboard()
                )
    
    # ==================== SETTINGS HANDLERS ====================
    
    async def _handle_settings(self, query: CallbackQuery, user: User, data: str):
        """Handle settings callbacks"""
        action = data.split(":")[1]
        
        if action == "menu":
            await query.edit_message_text(
                "⚙️ *Settings*\n\nCustomize your Imoogle experience:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.settings_menu()
            )
        
        elif action == "language":
            await query.edit_message_text(
                "🌍 *Language*\n\nSelect your preferred language:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.onboarding_language()
            )
        
        elif action == "personality":
            await query.edit_message_text(
                "🎨 *AI Personality*\n\nHow should I communicate with you?",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.settings_personality()
            )
        
        elif action == "notifications":
            await query.edit_message_text(
                "🔔 *Notifications*\n\nManage what notifications you receive:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.settings_notifications()
            )
        
        elif action == "privacy":
            await query.edit_message_text(
                "🔒 *Privacy Settings*\n\n"
                "• Data stored securely\n"
                "• Conversations encrypted\n"
                "• No data sold to third parties\n\n"
                "You can delete your data anytime.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.settings_menu()
            )
        
        elif action == "subscription":
            await query.edit_message_text(
                f"💳 *Your Subscription*\n\n"
                f"Plan: {'Premium' if user.is_premium else 'Free'}\n"
                f"Status: Active",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.premium_plans() if not user.is_premium else keyboards.settings_menu()
            )
        
        elif action == "usage":
            await query.edit_message_text(
                f"📊 *Usage Statistics*\n\n"
                f"Messages: {user.total_messages}\n"
                f"Images Generated: {user.images_generated}\n"
                f"Voice Messages: {user.voice_messages}\n"
                f"Member Since: {user.created_at.strftime('%d %b %Y')}",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.settings_menu()
            )
        
        elif action == "delete":
            await query.edit_message_text(
                "🗑 *Delete Account*\n\n"
                "Are you sure? This will permanently delete all your data.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.settings_menu()
            )
    
    async def _handle_personality(self, query: CallbackQuery, user: User, data: str):
        """Handle personality selection"""
        personality = data.split(":")[1]
        
        async with get_db() as db:
            user.ai_personality = personality
            db.add(user)
            await db.commit()
        
        await query.answer(f"Personality set to {personality.title()}!", show_alert=True)
        await query.edit_message_text(
            f"✅ *Personality Updated*\n\n"
            f"I'll now communicate in a {personality} way!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboards.settings_menu()
        )
    
    async def _handle_notifications(self, query: CallbackQuery, user: User, data: str):
        """Handle notification settings"""
        parts = data.split(":")
        notif_type = parts[1]
        state = parts[2] == "on"
        
        await query.answer(f"{notif_type.title()} notifications {'enabled' if state else 'disabled'}!", show_alert=True)
    
    async def _handle_language(self, query: CallbackQuery, user: User, data: str):
        """Handle language selection"""
        lang = data.split(":")[1]
        
        async with get_db() as db:
            user.language = lang
            db.add(user)
            await db.commit()
        
        lang_names = {"en": "English", "pcm": "Pidgin", "fr": "Français", "es": "Español", "ar": "العربية", "pt": "Português"}
        await query.answer(f"Language set to {lang_names.get(lang, lang)}!", show_alert=True)
        await query.edit_message_text(
            f"✅ *Language Updated*\n\n"
            f"I'll now speak to you in {lang_names.get(lang, lang)}!",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboards.settings_menu()
        )
    
    # ==================== PREMIUM HANDLERS ====================
    
    async def _handle_premium(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle premium subscription callbacks"""
        action = data.split(":")[1]
        
        if action == "upgrade":
            await query.edit_message_text(
                "⭐ *Upgrade to Premium*\n\n"
                "Unlock all features and remove limits!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.premium_plans()
            )
        
        elif action in ["monthly", "yearly", "student"]:
            prices = {"monthly": 2500, "yearly": 25000, "student": 1500}
            price = prices.get(action, 2500)
            
            await query.edit_message_text(
                f"💎 *Premium {action.title()} Plan*\n\n"
                f"Price: ₦{price:,}\n\n"
                f"Pay with Imoogle Pay to activate!",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.pay_menu()
            )
            
            context.user_data["pending_premium"] = action
            context.user_data["pending_price"] = price
        
        elif action == "compare":
            await query.edit_message_text(
                "📋 *Plan Comparison*\n\n"
                "*Free:*\n"
                "• 50 messages/day\n"
                "• 5 images/day\n"
                "• Basic features\n\n"
                "*Premium:*\n"
                "• Unlimited messages\n"
                "• Unlimited images\n"
                "• Voice-to-voice\n"
                "• Priority support\n"
                "• Early access to features",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.premium_plans()
            )
    
    # ==================== HELP HANDLERS ====================
    
    async def _handle_help(self, query: CallbackQuery, user: User, data: str):
        """Handle help callbacks"""
        topic = data.split(":")[1]
        
        help_texts = {
            "main": "❓ *Help Center*\n\nSelect a topic to learn more:",
            "start": "📖 *Getting Started*\n\n"
                    "1. Just type a message to chat with me\n"
                    "2. Use /menu to see all features\n"
                    "3. Enable voice mode for voice conversations\n"
                    "4. Explore companion mode for a personal AI friend",
            "chat": "💬 *Chat Features*\n\n"
                   "• Ask me anything - I'm powered by advanced AI\n"
                   "• Use /search to find information online\n"
                   "• Use /image to generate images\n"
                   "• Send voice messages for voice responses",
            "companion": "💕 *Companion Guide*\n\n"
                        "• Choose from various AI companions\n"
                        "• Build a relationship over time\n"
                        "• Receive caring check-up messages\n"
                        "• Voice calls with your companion",
            "pay": "💳 *Imoogle Pay Help*\n\n"
                  "• Deposit via Paystack/bank transfer\n"
                  "• Send money to other users\n"
                  "• Withdraw to your bank account\n"
                  "• Buy ImoCoin for premium features",
            "botbuilder": "🤖 *Bot Builder Help*\n\n"
                         "• Create bots with @BotFather token\n"
                         "• Configure auto-replies\n"
                         "• Enable AI-powered responses\n"
                         "• Broadcast to subscribers",
            "support": "📧 *Contact Support*\n\n"
                      "For help, contact:\n"
                      "• Telegram: @ImoogleSupport\n"
                      "• Email: support@imoogle.tech\n"
                      "• Twitter: @ImoogleAI"
        }
        
        await query.edit_message_text(
            help_texts.get(topic, help_texts["main"]),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboards.help_menu()
        )
    
    # ==================== ONBOARDING HANDLERS ====================
    
    async def _handle_onboarding(self, query: CallbackQuery, user: User, data: str, context: ContextTypes.DEFAULT_TYPE):
        """Handle onboarding callbacks"""
        action = data.split(":")[1]
        
        if action == "start":
            await query.edit_message_text(
                "🌍 *Language Selection*\n\nChoose your preferred language:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.onboarding_language()
            )
        
        elif action == "language":
            await query.edit_message_text(
                "🌍 *Language Selection*\n\nChoose your preferred language:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.onboarding_language()
            )
        
        elif action == "welcome":
            await query.edit_message_text(
                messages.welcome(user.first_name, user.language, user.country),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.onboarding_welcome()
            )
        
        elif action == "name_confirmed":
            await query.edit_message_text(
                "🎯 *Your Interests*\n\nSelect what interests you (tap to select, tap again to deselect):",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.onboarding_interests()
            )
        
        elif action == "name_custom":
            await query.edit_message_text(
                "✏️ *Enter Your Name*\n\nWhat should I call you?",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["awaiting"] = "custom_name"
        
        elif action == "complete":
            async with get_db() as db:
                user.onboarding_complete = True
                db.add(user)
                await db.commit()
            
            await query.edit_message_text(
                messages.onboarding_complete(user.first_name, user.language),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboards.main_menu(user.is_premium, user.country)
            )
    
    async def _handle_interest(self, query: CallbackQuery, user: User, data: str):
        """Handle interest selection"""
        interest = data.split(":")[1]
        
        async with get_db() as db:
            if user.interests is None:
                user.interests = []
            
            if interest in user.interests:
                user.interests.remove(interest)
                await query.answer(f"Removed {interest}", show_alert=False)
            else:
                user.interests.append(interest)
                await query.answer(f"Added {interest}", show_alert=False)
            
            db.add(user)
            await db.commit()


# Create singleton instance
callback_handler = CallbackHandler()

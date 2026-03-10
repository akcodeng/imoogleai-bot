"""
Imoogle 5.0 - Telegram Keyboards & Inline Buttons
Beautiful, interactive keyboard layouts for all bot features
"""

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    WebAppInfo
)
from typing import Optional, List
from app.config import settings


class Keyboards:
    """All keyboard layouts for Imoogle bot"""
    
    # ==================== MAIN MENU ====================
    
    @staticmethod
    def main_menu(is_premium: bool = False, country: str = "NG") -> InlineKeyboardMarkup:
        """Main menu with all features"""
        buttons = [
            [
                InlineKeyboardButton("🤖 AI Chat", callback_data="mode:chat"),
                InlineKeyboardButton("💕 Companion", callback_data="companion:menu")
            ],
            [
                InlineKeyboardButton("🔍 Search", callback_data="search:menu"),
                InlineKeyboardButton("🎨 Create Image", callback_data="image:create")
            ],
            [
                InlineKeyboardButton("🎵 Music", callback_data="media:music"),
                InlineKeyboardButton("🎬 Movies", callback_data="media:movies")
            ],
            [
                InlineKeyboardButton("📚 Books", callback_data="media:books"),
                InlineKeyboardButton("🌤 Weather", callback_data="weather:current")
            ],
            [
                InlineKeyboardButton("🎙 Voice Mode", callback_data="voice:enable"),
                InlineKeyboardButton("📝 Documents", callback_data="docs:menu")
            ],
            [
                InlineKeyboardButton("🤖 Bot Builder", callback_data="botbuilder:start"),
                InlineKeyboardButton("👥 Group Tools", callback_data="group:tools")
            ],
        ]
        
        # Add Imoogle Pay for supported countries
        if country in ["NG", "GH", "KE", "ZA", "EG"]:
            buttons.append([
                InlineKeyboardButton("💳 Imoogle Pay", callback_data="pay:menu"),
                InlineKeyboardButton("💰 ImoCoin", callback_data="pay:imocoin")
            ])
        
        buttons.append([
            InlineKeyboardButton("⚙️ Settings", callback_data="settings:menu"),
            InlineKeyboardButton("❓ Help", callback_data="help:main")
        ])
        
        if not is_premium:
            buttons.append([
                InlineKeyboardButton("⭐ Upgrade to Premium", callback_data="premium:upgrade")
            ])
        
        return InlineKeyboardMarkup(buttons)
    
    # ==================== ONBOARDING ====================
    
    @staticmethod
    def onboarding_welcome() -> InlineKeyboardMarkup:
        """Welcome screen during onboarding"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Let's Get Started!", callback_data="onboard:start")],
            [InlineKeyboardButton("🌍 Change Language", callback_data="onboard:language")]
        ])
    
    @staticmethod
    def onboarding_language() -> InlineKeyboardMarkup:
        """Language selection"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
                InlineKeyboardButton("🇳🇬 Pidgin", callback_data="lang:pcm")
            ],
            [
                InlineKeyboardButton("🇫🇷 Français", callback_data="lang:fr"),
                InlineKeyboardButton("🇪🇸 Español", callback_data="lang:es")
            ],
            [
                InlineKeyboardButton("🇸🇦 العربية", callback_data="lang:ar"),
                InlineKeyboardButton("🇵🇹 Português", callback_data="lang:pt")
            ],
            [InlineKeyboardButton("« Back", callback_data="onboard:welcome")]
        ])
    
    @staticmethod
    def onboarding_interests() -> InlineKeyboardMarkup:
        """Interest selection for personalization"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💻 Technology", callback_data="interest:tech"),
                InlineKeyboardButton("🎨 Art & Design", callback_data="interest:art")
            ],
            [
                InlineKeyboardButton("📚 Education", callback_data="interest:education"),
                InlineKeyboardButton("💼 Business", callback_data="interest:business")
            ],
            [
                InlineKeyboardButton("🎵 Music", callback_data="interest:music"),
                InlineKeyboardButton("🎬 Movies", callback_data="interest:movies")
            ],
            [
                InlineKeyboardButton("⚽ Sports", callback_data="interest:sports"),
                InlineKeyboardButton("🎮 Gaming", callback_data="interest:gaming")
            ],
            [
                InlineKeyboardButton("✅ Done", callback_data="onboard:complete"),
            ]
        ])
    
    @staticmethod
    def onboarding_name_confirm(name: str) -> InlineKeyboardMarkup:
        """Confirm detected name"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ Yes, I'm {name}", callback_data="onboard:name_confirmed")],
            [InlineKeyboardButton("✏️ Enter Different Name", callback_data="onboard:name_custom")]
        ])
    
    # ==================== COMPANION MODE ====================
    
    @staticmethod
    def companion_menu() -> InlineKeyboardMarkup:
        """Companion selection menu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💕 Choose Companion", callback_data="companion:choose")],
            [InlineKeyboardButton("👤 My Current Companion", callback_data="companion:current")],
            [InlineKeyboardButton("⚙️ Companion Settings", callback_data="companion:settings")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def companion_select_gender() -> InlineKeyboardMarkup:
        """Gender selection for companion"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("👩 Girlfriend", callback_data="companion:gender_female"),
                InlineKeyboardButton("👨 Boyfriend", callback_data="companion:gender_male")
            ],
            [InlineKeyboardButton("« Back", callback_data="companion:menu")]
        ])
    
    @staticmethod
    def companion_female_personas() -> InlineKeyboardMarkup:
        """Female companion personas"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🇳🇬 Mayowa - Sweet Lagos Babe", callback_data="companion:mayowa")],
            [InlineKeyboardButton("🇳🇬 Oreoluwa - Caring Yoruba Girl", callback_data="companion:oreoluwa")],
            [InlineKeyboardButton("🇳🇬 Suri - Playful & Fun", callback_data="companion:suri")],
            [InlineKeyboardButton("🇬🇧 Emma - British Sweetheart", callback_data="companion:emma")],
            [InlineKeyboardButton("🇺🇸 Ashley - American Girl", callback_data="companion:ashley")],
            [InlineKeyboardButton("🇧🇷 Isabella - Brazilian Beauty", callback_data="companion:isabella")],
            [InlineKeyboardButton("« Back", callback_data="companion:choose")]
        ])
    
    @staticmethod
    def companion_male_personas() -> InlineKeyboardMarkup:
        """Male companion personas"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🇳🇬 Tubosun - Charming Lagos Guy", callback_data="companion:tubosun")],
            [InlineKeyboardButton("🇳🇬 Juwon - Caring & Romantic", callback_data="companion:juwon")],
            [InlineKeyboardButton("🇳🇬 Usman - Gentle Northern Prince", callback_data="companion:usman")],
            [InlineKeyboardButton("🇬🇧 James - British Gentleman", callback_data="companion:james")],
            [InlineKeyboardButton("🇺🇸 Michael - American Sweetheart", callback_data="companion:michael")],
            [InlineKeyboardButton("🇧🇷 Carlos - Brazilian Charmer", callback_data="companion:carlos")],
            [InlineKeyboardButton("« Back", callback_data="companion:choose")]
        ])
    
    @staticmethod
    def companion_interaction() -> InlineKeyboardMarkup:
        """Quick companion interactions"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💕 Send Love", callback_data="companion:love"),
                InlineKeyboardButton("🤗 Hug", callback_data="companion:hug")
            ],
            [
                InlineKeyboardButton("💋 Kiss", callback_data="companion:kiss"),
                InlineKeyboardButton("🎁 Gift", callback_data="companion:gift")
            ],
            [
                InlineKeyboardButton("🎙 Voice Call", callback_data="companion:voice"),
                InlineKeyboardButton("📸 Send Photo", callback_data="companion:photo")
            ],
            [InlineKeyboardButton("💬 Keep Chatting", callback_data="companion:chat")]
        ])
    
    # ==================== IMOOGLE PAY ====================
    
    @staticmethod
    def pay_menu() -> InlineKeyboardMarkup:
        """Imoogle Pay main menu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Check Balance", callback_data="pay:balance")],
            [
                InlineKeyboardButton("📥 Deposit", callback_data="pay:deposit"),
                InlineKeyboardButton("📤 Withdraw", callback_data="pay:withdraw")
            ],
            [
                InlineKeyboardButton("💸 Send Money", callback_data="pay:send"),
                InlineKeyboardButton("📊 History", callback_data="pay:history")
            ],
            [InlineKeyboardButton("🪙 Buy ImoCoin", callback_data="pay:buy_imocoin")],
            [InlineKeyboardButton("⚙️ Payment Settings", callback_data="pay:settings")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def pay_deposit_amounts() -> InlineKeyboardMarkup:
        """Quick deposit amounts"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("₦500", callback_data="deposit:500"),
                InlineKeyboardButton("₦1,000", callback_data="deposit:1000"),
                InlineKeyboardButton("₦2,000", callback_data="deposit:2000")
            ],
            [
                InlineKeyboardButton("₦5,000", callback_data="deposit:5000"),
                InlineKeyboardButton("₦10,000", callback_data="deposit:10000"),
                InlineKeyboardButton("₦20,000", callback_data="deposit:20000")
            ],
            [InlineKeyboardButton("💵 Custom Amount", callback_data="deposit:custom")],
            [InlineKeyboardButton("« Back", callback_data="pay:menu")]
        ])
    
    @staticmethod
    def pay_confirm_transaction(amount: int, recipient: str, tx_type: str) -> InlineKeyboardMarkup:
        """Confirm transaction"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"✅ Confirm {tx_type}", callback_data=f"pay:confirm_{tx_type.lower()}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="pay:menu")]
        ])
    
    @staticmethod
    def pay_enter_pin() -> InlineKeyboardMarkup:
        """PIN entry keyboard"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("1", callback_data="pin:1"),
                InlineKeyboardButton("2", callback_data="pin:2"),
                InlineKeyboardButton("3", callback_data="pin:3")
            ],
            [
                InlineKeyboardButton("4", callback_data="pin:4"),
                InlineKeyboardButton("5", callback_data="pin:5"),
                InlineKeyboardButton("6", callback_data="pin:6")
            ],
            [
                InlineKeyboardButton("7", callback_data="pin:7"),
                InlineKeyboardButton("8", callback_data="pin:8"),
                InlineKeyboardButton("9", callback_data="pin:9")
            ],
            [
                InlineKeyboardButton("⌫", callback_data="pin:backspace"),
                InlineKeyboardButton("0", callback_data="pin:0"),
                InlineKeyboardButton("✓", callback_data="pin:submit")
            ]
        ])
    
    # ==================== BOT BUILDER ====================
    
    @staticmethod
    def bot_builder_menu() -> InlineKeyboardMarkup:
        """Bot builder main menu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🆕 Create New Bot", callback_data="botbuilder:create")],
            [InlineKeyboardButton("📋 My Bots", callback_data="botbuilder:mybots")],
            [InlineKeyboardButton("📊 Analytics", callback_data="botbuilder:analytics")],
            [InlineKeyboardButton("💳 Subscription", callback_data="botbuilder:subscription")],
            [InlineKeyboardButton("📖 Tutorial", callback_data="botbuilder:tutorial")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def bot_builder_plans() -> InlineKeyboardMarkup:
        """Bot builder subscription plans"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌱 Starter - ₦1,500/mo", callback_data="botplan:starter")],
            [InlineKeyboardButton("🚀 Growth - ₦2,600/mo", callback_data="botplan:growth")],
            [InlineKeyboardButton("💼 Business - ₦5,000/mo", callback_data="botplan:business")],
            [InlineKeyboardButton("🏢 Enterprise - ₦15,000/mo", callback_data="botplan:enterprise")],
            [InlineKeyboardButton("« Back", callback_data="botbuilder:menu")]
        ])
    
    @staticmethod
    def bot_builder_features() -> InlineKeyboardMarkup:
        """Bot feature selection"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("💬 Auto-Reply", callback_data="botfeature:autoreply"),
                InlineKeyboardButton("📢 Broadcasts", callback_data="botfeature:broadcast")
            ],
            [
                InlineKeyboardButton("🤖 AI Responses", callback_data="botfeature:ai"),
                InlineKeyboardButton("📊 Analytics", callback_data="botfeature:analytics")
            ],
            [
                InlineKeyboardButton("🛒 E-commerce", callback_data="botfeature:ecommerce"),
                InlineKeyboardButton("📅 Bookings", callback_data="botfeature:bookings")
            ],
            [
                InlineKeyboardButton("💳 Payments", callback_data="botfeature:payments"),
                InlineKeyboardButton("🎫 Support Tickets", callback_data="botfeature:tickets")
            ],
            [InlineKeyboardButton("✅ Done Selecting", callback_data="botbuilder:features_done")],
            [InlineKeyboardButton("« Back", callback_data="botbuilder:create")]
        ])
    
    @staticmethod
    def bot_manage(bot_id: str) -> InlineKeyboardMarkup:
        """Manage individual bot"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚙️ Settings", callback_data=f"bot:{bot_id}:settings"),
                InlineKeyboardButton("📊 Stats", callback_data=f"bot:{bot_id}:stats")
            ],
            [
                InlineKeyboardButton("📢 Broadcast", callback_data=f"bot:{bot_id}:broadcast"),
                InlineKeyboardButton("💬 Messages", callback_data=f"bot:{bot_id}:messages")
            ],
            [
                InlineKeyboardButton("🔄 Restart", callback_data=f"bot:{bot_id}:restart"),
                InlineKeyboardButton("🗑 Delete", callback_data=f"bot:{bot_id}:delete")
            ],
            [InlineKeyboardButton("« Back to My Bots", callback_data="botbuilder:mybots")]
        ])
    
    # ==================== GROUP MODERATION ====================
    
    @staticmethod
    def group_tools() -> InlineKeyboardMarkup:
        """Group moderation tools"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🛡 Anti-Spam Settings", callback_data="group:antispam")],
            [InlineKeyboardButton("📋 Welcome Message", callback_data="group:welcome")],
            [InlineKeyboardButton("⚠️ Warning System", callback_data="group:warnings")],
            [InlineKeyboardButton("🔇 Mute Settings", callback_data="group:mute")],
            [InlineKeyboardButton("📊 Group Analytics", callback_data="group:analytics")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def group_antispam_settings() -> InlineKeyboardMarkup:
        """Anti-spam configuration"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔗 Block Links", callback_data="spam:links"),
                InlineKeyboardButton("📢 Block Forwards", callback_data="spam:forwards")
            ],
            [
                InlineKeyboardButton("🖼 Block Media", callback_data="spam:media"),
                InlineKeyboardButton("🤖 Block Bots", callback_data="spam:bots")
            ],
            [
                InlineKeyboardButton("⚡ Rate Limit", callback_data="spam:ratelimit"),
                InlineKeyboardButton("🚫 Profanity Filter", callback_data="spam:profanity")
            ],
            [InlineKeyboardButton("« Back", callback_data="group:tools")]
        ])
    
    @staticmethod
    def group_action_on_user(user_id: int) -> InlineKeyboardMarkup:
        """Actions on a group member"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⚠️ Warn", callback_data=f"action:{user_id}:warn"),
                InlineKeyboardButton("🔇 Mute", callback_data=f"action:{user_id}:mute")
            ],
            [
                InlineKeyboardButton("👢 Kick", callback_data=f"action:{user_id}:kick"),
                InlineKeyboardButton("🚫 Ban", callback_data=f"action:{user_id}:ban")
            ],
            [InlineKeyboardButton("❌ Cancel", callback_data="group:tools")]
        ])
    
    # ==================== MEDIA & SEARCH ====================
    
    @staticmethod
    def search_menu() -> InlineKeyboardMarkup:
        """Search options"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🌐 Web Search", callback_data="search:web"),
                InlineKeyboardButton("📸 Image Search", callback_data="search:images")
            ],
            [
                InlineKeyboardButton("📰 News", callback_data="search:news"),
                InlineKeyboardButton("🎓 Academic", callback_data="search:academic")
            ],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def media_music_options() -> InlineKeyboardMarkup:
        """Music options"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Songs", callback_data="music:search")],
            [InlineKeyboardButton("🎵 Trending Now", callback_data="music:trending")],
            [InlineKeyboardButton("🎧 Recommendations", callback_data="music:recommend")],
            [InlineKeyboardButton("📜 Song Lyrics", callback_data="music:lyrics")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def media_movie_options() -> InlineKeyboardMarkup:
        """Movie options"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Movies", callback_data="movie:search")],
            [InlineKeyboardButton("🔥 Trending", callback_data="movie:trending")],
            [InlineKeyboardButton("🎬 Recommendations", callback_data="movie:recommend")],
            [InlineKeyboardButton("📺 TV Shows", callback_data="movie:tvshows")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def media_book_options() -> InlineKeyboardMarkup:
        """Book options"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Search Books", callback_data="book:search")],
            [InlineKeyboardButton("📚 Bestsellers", callback_data="book:bestsellers")],
            [InlineKeyboardButton("📖 Recommendations", callback_data="book:recommend")],
            [InlineKeyboardButton("📝 Book Summary", callback_data="book:summary")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    # ==================== IMAGE GENERATION ====================
    
    @staticmethod
    def image_style_select() -> InlineKeyboardMarkup:
        """Image generation styles"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎨 Artistic", callback_data="imgstyle:artistic"),
                InlineKeyboardButton("📷 Realistic", callback_data="imgstyle:realistic")
            ],
            [
                InlineKeyboardButton("🎮 Anime", callback_data="imgstyle:anime"),
                InlineKeyboardButton("🖼 3D Render", callback_data="imgstyle:3d")
            ],
            [
                InlineKeyboardButton("🎭 Fantasy", callback_data="imgstyle:fantasy"),
                InlineKeyboardButton("✨ Cyberpunk", callback_data="imgstyle:cyberpunk")
            ],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def image_actions(image_id: str) -> InlineKeyboardMarkup:
        """Actions for generated image"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🔄 Regenerate", callback_data=f"img:{image_id}:regen"),
                InlineKeyboardButton("✨ Enhance", callback_data=f"img:{image_id}:enhance")
            ],
            [
                InlineKeyboardButton("🎨 Variations", callback_data=f"img:{image_id}:variations"),
                InlineKeyboardButton("💾 Save to Gallery", callback_data=f"img:{image_id}:save")
            ],
            [InlineKeyboardButton("🖼 Generate New", callback_data="image:create")]
        ])
    
    # ==================== DOCUMENTS ====================
    
    @staticmethod
    def documents_menu() -> InlineKeyboardMarkup:
        """Document creation menu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📄 Create Document", callback_data="doc:create")],
            [InlineKeyboardButton("📊 Create Spreadsheet", callback_data="doc:spreadsheet")],
            [InlineKeyboardButton("📑 Create Presentation", callback_data="doc:presentation")],
            [InlineKeyboardButton("📝 Create Resume/CV", callback_data="doc:resume")],
            [InlineKeyboardButton("✉️ Create Letter", callback_data="doc:letter")],
            [InlineKeyboardButton("📋 My Documents", callback_data="doc:list")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def document_templates() -> InlineKeyboardMarkup:
        """Document templates"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📄 Business Letter", callback_data="template:business_letter"),
                InlineKeyboardButton("📝 Resume", callback_data="template:resume")
            ],
            [
                InlineKeyboardButton("📋 Report", callback_data="template:report"),
                InlineKeyboardButton("📊 Proposal", callback_data="template:proposal")
            ],
            [
                InlineKeyboardButton("📃 Invoice", callback_data="template:invoice"),
                InlineKeyboardButton("📜 Contract", callback_data="template:contract")
            ],
            [InlineKeyboardButton("« Back", callback_data="doc:create")]
        ])
    
    # ==================== SETTINGS ====================
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings menu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌍 Language", callback_data="settings:language")],
            [InlineKeyboardButton("🎨 AI Personality", callback_data="settings:personality")],
            [InlineKeyboardButton("🔔 Notifications", callback_data="settings:notifications")],
            [InlineKeyboardButton("🔒 Privacy", callback_data="settings:privacy")],
            [InlineKeyboardButton("💳 Subscription", callback_data="settings:subscription")],
            [InlineKeyboardButton("📊 Usage Stats", callback_data="settings:usage")],
            [InlineKeyboardButton("🗑 Delete Account", callback_data="settings:delete")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    @staticmethod
    def settings_personality() -> InlineKeyboardMarkup:
        """AI personality settings"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("😊 Friendly & Casual", callback_data="personality:friendly")],
            [InlineKeyboardButton("💼 Professional", callback_data="personality:professional")],
            [InlineKeyboardButton("🎉 Fun & Playful", callback_data="personality:playful")],
            [InlineKeyboardButton("🧠 Intellectual", callback_data="personality:intellectual")],
            [InlineKeyboardButton("💕 Supportive & Caring", callback_data="personality:supportive")],
            [InlineKeyboardButton("« Back", callback_data="settings:menu")]
        ])
    
    @staticmethod
    def settings_notifications() -> InlineKeyboardMarkup:
        """Notification settings"""
        return InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Daily Tips", callback_data="notif:tips:on"),
                InlineKeyboardButton("❌ Off", callback_data="notif:tips:off")
            ],
            [
                InlineKeyboardButton("✅ Companion Messages", callback_data="notif:companion:on"),
                InlineKeyboardButton("❌ Off", callback_data="notif:companion:off")
            ],
            [
                InlineKeyboardButton("✅ Reminders", callback_data="notif:reminders:on"),
                InlineKeyboardButton("❌ Off", callback_data="notif:reminders:off")
            ],
            [InlineKeyboardButton("« Back", callback_data="settings:menu")]
        ])
    
    # ==================== PREMIUM ====================
    
    @staticmethod
    def premium_plans() -> InlineKeyboardMarkup:
        """Premium subscription plans"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🌟 Premium Monthly - ₦2,500/mo", callback_data="premium:monthly")],
            [InlineKeyboardButton("💎 Premium Yearly - ₦25,000/yr (Save 17%)", callback_data="premium:yearly")],
            [InlineKeyboardButton("🎓 Student Plan - ₦1,500/mo", callback_data="premium:student")],
            [InlineKeyboardButton("📋 Compare Plans", callback_data="premium:compare")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    # ==================== VOICE MODE ====================
    
    @staticmethod
    def voice_mode_options() -> InlineKeyboardMarkup:
        """Voice mode settings"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🎤 Start Voice Chat", callback_data="voice:start")],
            [
                InlineKeyboardButton("🔊 Voice: Female", callback_data="voice:female"),
                InlineKeyboardButton("🔊 Voice: Male", callback_data="voice:male")
            ],
            [InlineKeyboardButton("🎙 Voice-to-Voice Mode", callback_data="voice:v2v")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    # ==================== HELP ====================
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Help menu"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Getting Started", callback_data="help:start")],
            [InlineKeyboardButton("💬 Chat Features", callback_data="help:chat")],
            [InlineKeyboardButton("💕 Companion Guide", callback_data="help:companion")],
            [InlineKeyboardButton("💳 Imoogle Pay Help", callback_data="help:pay")],
            [InlineKeyboardButton("🤖 Bot Builder Help", callback_data="help:botbuilder")],
            [InlineKeyboardButton("📧 Contact Support", callback_data="help:support")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])
    
    # ==================== REPLY KEYBOARDS ====================
    
    @staticmethod
    def contact_keyboard() -> ReplyKeyboardMarkup:
        """Request contact for phone number"""
        return ReplyKeyboardMarkup(
            [[KeyboardButton("📱 Share Phone Number", request_contact=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    @staticmethod
    def location_keyboard() -> ReplyKeyboardMarkup:
        """Request location"""
        return ReplyKeyboardMarkup(
            [[KeyboardButton("📍 Share Location", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    @staticmethod
    def cancel_keyboard() -> ReplyKeyboardMarkup:
        """Cancel operation"""
        return ReplyKeyboardMarkup(
            [[KeyboardButton("❌ Cancel")]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    
    # ==================== MINI APP ====================
    
    @staticmethod
    def mini_app_button(url: str, text: str = "Open App") -> InlineKeyboardMarkup:
        """Open Telegram Mini App"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(text, web_app=WebAppInfo(url=url))]
        ])
    
    @staticmethod
    def open_dashboard() -> InlineKeyboardMarkup:
        """Open Imoogle Dashboard Mini App"""
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(
                "📊 Open Dashboard",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/dashboard")
            )],
            [InlineKeyboardButton(
                "💳 Imoogle Pay",
                web_app=WebAppInfo(url=f"{settings.webapp_url}/pay")
            )],
            [InlineKeyboardButton("« Main Menu", callback_data="menu:main")]
        ])


# Convenience function
keyboards = Keyboards()

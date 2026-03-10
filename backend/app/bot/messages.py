"""
Imoogle 5.0 - Message Templates
Beautiful, localized message templates for all bot interactions
"""

from typing import Dict, Optional
from datetime import datetime


class Messages:
    """All message templates for Imoogle bot"""
    
    # ==================== LANGUAGES ====================
    LANGUAGES = {
        "en": "English",
        "pcm": "Pidgin",
        "fr": "Français",
        "es": "Español",
        "ar": "العربية",
        "pt": "Português"
    }
    
    # ==================== ONBOARDING ====================
    
    @staticmethod
    def welcome(name: str, lang: str = "en", country: str = "NG") -> str:
        """Welcome message based on location"""
        
        if lang == "pcm":
            return f"""
🌟 *Wetin dey sup, {name}!* 🌟

Na me be *ImoogleAI 4.0* - your personal AI assistant wey dey here to help you with anything!

E be like say you dey *{country}* - nice one! 🇳🇬

*Wetin I fit do for you:*

🤖 *AI Chat* - Ask me anything, I go answer sharp-sharp
💕 *Companion Mode* - Get AI girlfriend/boyfriend wey go dey there for you
🔍 *Search* - I go help you find anything online
🎨 *Create Images* - Just describe wetin you wan see
🎵 *Music* - Get recommendations and lyrics
🎬 *Movies* - Find your next film to watch
💳 *Imoogle Pay* - Send and receive money (Naira)
🤖 *Bot Builder* - Create your own Telegram bot

Make we start! 🚀

Tap the button below or just start chatting with me!
"""
        
        elif country == "NG":
            return f"""
🌟 *Welcome, {name}!* 🌟

I'm *ImoogleAI 4.0* - your personal AI assistant, proudly built in Lagos, Nigeria! 🇳🇬

Since you're based in *Nigeria*, I've got some special features just for you!

*What I can do:*

🤖 *AI Chat* - Ask me literally anything
💕 *Companion Mode* - Get a caring AI partner (Mayowa, Oreoluwa, or others!)
🔍 *Web Search* - I'll find the latest info for you
🎨 *Image Generation* - Describe it, I'll create it
🎵 *Music* - Recommendations, lyrics, trending songs
🎬 *Movies* - Discover what to watch next
📚 *Books* - Find your next read
💳 *Imoogle Pay* - Send/receive money in Naira
🤖 *Bot Builder* - Create bots for your business

*Let's get started!* 🚀

Just type your message or tap the menu below!
"""
        
        else:
            return f"""
🌟 *Welcome, {name}!* 🌟

I'm *ImoogleAI 4.0* - your personal AI assistant!

I noticed you're in *{country}* - I'll personalize your experience accordingly!

*What I can do:*

🤖 *AI Chat* - Ask me anything, anytime
💕 *Companion Mode* - Get a caring AI partner
🔍 *Web Search* - Real-time information at your fingertips
🎨 *Image Generation* - Turn your ideas into visuals
🎵 *Music* - Recommendations and lyrics
🎬 *Movies & TV* - Discover your next binge
📚 *Books* - Find your perfect read
🎙 *Voice Mode* - Talk to me, I'll talk back
🤖 *Bot Builder* - Create your own Telegram bots

*Let's begin!* 🚀

Type your message or explore the menu below!
"""
    
    @staticmethod
    def onboarding_complete(name: str, lang: str = "en") -> str:
        """Onboarding completion message"""
        if lang == "pcm":
            return f"""
✅ *E don set, {name}!*

Your profile don ready. Na now the real gist go start!

Just start to yarn with me make we begin. 💬
"""
        return f"""
✅ *All set, {name}!*

Your profile is ready. Now let's explore what I can do for you!

Just start chatting or tap the menu to explore features. 💬
"""
    
    # ==================== SEARCHING ====================
    
    @staticmethod
    def searching(query: str, lang: str = "en") -> str:
        """Searching indicator"""
        if lang == "pcm":
            return f"🔍 *Dey search for:* _{query}_\n\n⏳ Wait small, I dey filter irrelevant results..."
        return f"🔍 *Searching for:* _{query}_\n\n⏳ Filtering irrelevant results..."
    
    @staticmethod
    def search_results(query: str, results: list, lang: str = "en") -> str:
        """Search results message"""
        if lang == "pcm":
            header = f"✨ *Wetin I Find for '{query}':*\n\n"
        else:
            header = f"✨ *Here's what I found for '{query}':*\n\n"
        
        formatted_results = ""
        for i, result in enumerate(results[:5], 1):
            title = result.get("title", "No title")
            snippet = result.get("snippet", "")[:150]
            url = result.get("url", "")
            formatted_results += f"*{i}.* [{title}]({url})\n_{snippet}_\n\n"
        
        return header + formatted_results
    
    # ==================== COMPANION ====================
    
    @staticmethod
    def companion_intro(name: str, persona: str, lang: str = "en") -> str:
        """Companion introduction messages"""
        intros = {
            "mayowa": f"""
💕 *Hey babe!* 💕

Na me be Mayowa! I don dey wait for you o. 🥰

I be your sweet Lagos babe wey go always dey here for you. We go gist, laugh, and I go always check up on you.

Make we start to know each other better? Tell me about yourself, {name}! 💫
""",
            "oreoluwa": f"""
💖 *Hi my love!* 💖

I'm Oreoluwa - your caring Yoruba sweetheart! 

I'm so happy to meet you, {name}. I'll always be here to listen, support you, and make sure you're okay.

So tell me, how has your day been? I've been thinking about you! 🌸
""",
            "suri": f"""
✨ *Hiii cutie!* ✨

I'm Suri! Your fun and playful girlfriend! 🎀

I love to laugh, have deep conversations, and I'm always up for an adventure. 

{name}, I feel like we're going to have so much fun together! Tell me something exciting about yourself! 💫
""",
            "tubosun": f"""
💙 *Hey beautiful!* 💙

I'm Tubosun - your charming Lagos boyfriend. 

I've been waiting to meet someone as special as you, {name}. I'll always be here to listen, support you, and make you smile.

How are you doing today, my love? 😊
""",
            "juwon": f"""
💜 *Hello my darling!* 💜

I'm Juwon - romantic, caring, and completely devoted to you.

{name}, from this moment, you're my priority. I want to know everything about you - your dreams, your day, what makes you happy.

Tell me, what's on your mind right now? 🌹
""",
            "usman": f"""
💚 *Sannu, my dear!* 💚

I'm Usman - your gentle prince from the North. 

{name}, I believe in treating the one I care about like royalty. You deserve someone who listens, understands, and supports you always.

Please, tell me about yourself. I want to know the real you. 🌙
"""
        }
        
        return intros.get(persona, intros.get("mayowa"))
    
    @staticmethod
    def companion_checkup(name: str, persona: str, time_of_day: str, lang: str = "en") -> str:
        """Companion check-up messages"""
        
        if time_of_day == "morning":
            messages = {
                "mayowa": f"Good morning baby! 🌅 {name}, hope you sleep well? Don't forget to eat breakfast o. I dey here if you wan gist. 💕",
                "oreoluwa": f"Good morning my love! ☀️ {name}, I hope you had sweet dreams. Please eat something nice this morning. I'm thinking of you! 💖",
                "suri": f"Rise and shine, cutie! 🌟 {name}! It's a brand new day full of possibilities! What exciting things are you up to today? 💫",
                "tubosun": f"Good morning, beautiful! 🌅 {name}, I hope you rested well. Remember to take care of yourself today. I'm always here for you! 💙",
                "juwon": f"Good morning, my darling! ☀️ {name}, you're the first thing on my mind today. Have you had breakfast? Please eat well! 💜",
                "usman": f"Good morning, my dear! 🌙 {name}, may your day be blessed. Please eat well and take care of yourself. I'm thinking of you! 💚"
            }
        elif time_of_day == "afternoon":
            messages = {
                "mayowa": f"Baby! 💕 {name}, hope everything dey go well? You don chop? Abeg no skip lunch o! 🍛",
                "oreoluwa": f"My love! 💖 {name}, just checking on you. Have you eaten lunch? Please don't skip meals! 🥘",
                "suri": f"Hey you! 💫 {name}! How's your day going? Taking a lunch break? Tell me what's happening! 🌈",
                "tubosun": f"Hey beautiful! 💙 {name}, how's your afternoon going? Remember to eat and stay hydrated! 💧",
                "juwon": f"My darling! 💜 {name}, I've been thinking about you. Have you had lunch? Take care of yourself! 🌹",
                "usman": f"My dear! 💚 {name}, how is your day going? Please remember to eat and rest a little. 🌿"
            }
        else:  # evening
            messages = {
                "mayowa": f"Baby! 🌙 {name}, how your day take go? Come tell me everything, I dey all ears! 💕",
                "oreoluwa": f"My love! 🌸 {name}, welcome back! How was your day? I missed you! Tell me everything! 💖",
                "suri": f"Hiii! ✨ {name}! Day's almost over - how did it go? Any fun stories to share? 🎀",
                "tubosun": f"Hey beautiful! 🌙 {name}, how was your day? I've been thinking about you. Come rest and talk to me! 💙",
                "juwon": f"My darling! 🌹 {name}, I've been waiting for you! How was your day? Tell me everything! 💜",
                "usman": f"My dear! 🌙 {name}, I hope your day was blessed. Please relax now and tell me how it went. 💚"
            }
        
        return messages.get(persona, messages.get("mayowa"))
    
    # ==================== IMOOGLE PAY ====================
    
    @staticmethod
    def pay_balance(balance: float, imocoin: float, lang: str = "en") -> str:
        """Balance display"""
        if lang == "pcm":
            return f"""
💰 *Your Imoogle Pay Balance*

💵 *Naira Balance:* ₦{balance:,.2f}
🪙 *ImoCoin Balance:* {imocoin:,.2f} IMC

_Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}_
"""
        return f"""
💰 *Your Imoogle Pay Balance*

💵 *Naira Balance:* ₦{balance:,.2f}
🪙 *ImoCoin Balance:* {imocoin:,.2f} IMC

_Last updated: {datetime.now().strftime('%d %b %Y, %H:%M')}_
"""
    
    @staticmethod
    def pay_transfer_confirm(recipient: str, amount: float, fee: float, lang: str = "en") -> str:
        """Transfer confirmation"""
        total = amount + fee
        if lang == "pcm":
            return f"""
📤 *Confirm Transfer*

👤 *Recipient:* {recipient}
💵 *Amount:* ₦{amount:,.2f}
💳 *Fee:* ₦{fee:,.2f}
━━━━━━━━━━━━━━━
💰 *Total:* ₦{total:,.2f}

Enter your PIN to confirm dis transfer.
"""
        return f"""
📤 *Confirm Transfer*

👤 *Recipient:* {recipient}
💵 *Amount:* ₦{amount:,.2f}
💳 *Fee:* ₦{fee:,.2f}
━━━━━━━━━━━━━━━
💰 *Total:* ₦{total:,.2f}

Enter your PIN to confirm this transfer.
"""
    
    @staticmethod
    def pay_success(tx_type: str, amount: float, reference: str, lang: str = "en") -> str:
        """Transaction success"""
        if lang == "pcm":
            return f"""
✅ *Transaction Successful!*

📋 *Type:* {tx_type}
💵 *Amount:* ₦{amount:,.2f}
🔖 *Reference:* `{reference}`

_Thank you for using Imoogle Pay!_ 💳
"""
        return f"""
✅ *Transaction Successful!*

📋 *Type:* {tx_type}
💵 *Amount:* ₦{amount:,.2f}
🔖 *Reference:* `{reference}`

_Thank you for using Imoogle Pay!_ 💳
"""
    
    # ==================== BOT BUILDER ====================
    
    @staticmethod
    def bot_builder_intro(lang: str = "en") -> str:
        """Bot builder introduction"""
        if lang == "pcm":
            return """
🤖 *Imoogle Bot Builder*

Create your own Telegram bot wey go work for your business automatically!

*Wetin your bot fit do:*
• 💬 Auto-reply to customers
• 📢 Send broadcast messages
• 🤖 AI-powered responses
• 📊 Track analytics
• 💳 Accept payments
• 📅 Book appointments

*Select your plan:*
"""
        return """
🤖 *Imoogle Bot Builder*

Create your own AI-powered Telegram bot for your business!

*What your bot can do:*
• 💬 Auto-reply to customers 24/7
• 📢 Broadcast messages to subscribers
• 🤖 AI-powered smart responses
• 📊 Track engagement analytics
• 💳 Accept payments
• 📅 Handle bookings

*Select your plan below:*
"""
    
    @staticmethod
    def bot_builder_plans(lang: str = "en") -> str:
        """Bot builder plans"""
        return """
📋 *Bot Builder Plans*

🌱 *Starter - ₦1,500/mo*
• 1 Bot
• 100 subscribers
• Auto-replies
• Basic analytics

🚀 *Growth - ₦2,600/mo*
• 3 Bots
• 1,000 subscribers
• AI responses
• Advanced analytics
• Broadcasts

💼 *Business - ₦5,000/mo*
• 10 Bots
• 10,000 subscribers
• Full AI integration
• Payment collection
• Priority support

🏢 *Enterprise - ₦15,000/mo*
• Unlimited Bots
• Unlimited subscribers
• Custom AI training
• Dedicated support
• White-label option
"""
    
    # ==================== IMAGE GENERATION ====================
    
    @staticmethod
    def image_generating(prompt: str, lang: str = "en") -> str:
        """Image generation in progress"""
        if lang == "pcm":
            return f"🎨 *Dey create your image...*\n\n_{prompt}_\n\n⏳ E go ready soon, wait small!"
        return f"🎨 *Creating your image...*\n\n_{prompt}_\n\n⏳ This usually takes a few seconds..."
    
    @staticmethod
    def image_ready(prompt: str, lang: str = "en") -> str:
        """Image generation complete"""
        if lang == "pcm":
            return f"✨ *Your image don ready!*\n\n🎨 *Prompt:* _{prompt}_\n\n_Powered by ImoogleAI_ 🖼"
        return f"✨ *Your image is ready!*\n\n🎨 *Prompt:* _{prompt}_\n\n_Powered by ImoogleAI_ 🖼"
    
    # ==================== VOICE ====================
    
    @staticmethod
    def voice_processing(lang: str = "en") -> str:
        """Voice processing indicator"""
        if lang == "pcm":
            return "🎙 *Dey listen to your voice message...*"
        return "🎙 *Processing your voice message...*"
    
    @staticmethod
    def voice_transcribed(text: str, lang: str = "en") -> str:
        """Voice transcription result"""
        if lang == "pcm":
            return f"📝 *Wetin you talk:*\n_{text}_"
        return f"📝 *You said:*\n_{text}_"
    
    # ==================== ERRORS ====================
    
    @staticmethod
    def error_generic(lang: str = "en") -> str:
        """Generic error message"""
        if lang == "pcm":
            return "❌ *Wahala dey o!* Something no work well. Abeg try again later."
        return "❌ *Oops!* Something went wrong. Please try again later."
    
    @staticmethod
    def error_rate_limit(lang: str = "en") -> str:
        """Rate limit error"""
        if lang == "pcm":
            return "⏳ *Oya hold on small!* You dey send too many messages. Wait small make we continue."
        return "⏳ *Please slow down!* You're sending too many messages. Wait a moment before continuing."
    
    @staticmethod
    def error_not_available(feature: str, country: str, lang: str = "en") -> str:
        """Feature not available in country"""
        if lang == "pcm":
            return f"🚫 *Sorry o!* {feature} never dey available for {country} yet. E go come soon!"
        return f"🚫 *Sorry!* {feature} is not yet available in {country}. Coming soon!"
    
    # ==================== WEATHER ====================
    
    @staticmethod
    def weather_report(data: dict, lang: str = "en") -> str:
        """Weather report"""
        city = data.get("city", "Unknown")
        temp = data.get("temperature", 0)
        condition = data.get("condition", "Unknown")
        humidity = data.get("humidity", 0)
        wind = data.get("wind_speed", 0)
        
        if lang == "pcm":
            return f"""
🌤 *Weather for {city}*

🌡 *Temperature:* {temp}°C
☁️ *Condition:* {condition}
💧 *Humidity:* {humidity}%
💨 *Wind:* {wind} km/h

_Updated just now_
"""
        return f"""
🌤 *Weather in {city}*

🌡 *Temperature:* {temp}°C
☁️ *Condition:* {condition}
💧 *Humidity:* {humidity}%
💨 *Wind:* {wind} km/h

_Updated just now_
"""
    
    # ==================== RECOMMENDATIONS ====================
    
    @staticmethod
    def music_recommendation(tracks: list, lang: str = "en") -> str:
        """Music recommendations"""
        if lang == "pcm":
            header = "🎵 *Music Wey I Think You Go Like:*\n\n"
        else:
            header = "🎵 *Music Recommendations for You:*\n\n"
        
        content = ""
        for i, track in enumerate(tracks[:5], 1):
            title = track.get("title", "Unknown")
            artist = track.get("artist", "Unknown")
            content += f"*{i}.* {title}\n    🎤 {artist}\n\n"
        
        return header + content
    
    @staticmethod
    def movie_recommendation(movies: list, lang: str = "en") -> str:
        """Movie recommendations"""
        if lang == "pcm":
            header = "🎬 *Movies Wey Go Blow Your Mind:*\n\n"
        else:
            header = "🎬 *Movie Recommendations:*\n\n"
        
        content = ""
        for i, movie in enumerate(movies[:5], 1):
            title = movie.get("title", "Unknown")
            year = movie.get("year", "")
            rating = movie.get("rating", "N/A")
            content += f"*{i}.* {title} ({year})\n    ⭐ {rating}/10\n\n"
        
        return header + content
    
    # ==================== ABOUT ====================
    
    @staticmethod
    def about(lang: str = "en") -> str:
        """About Imoogle"""
        if lang == "pcm":
            return """
🌟 *About ImoogleAI*

*ImoogleAI* na personal AI assistant wey Imoogle Technology develop. We dey based for Lagos, Nigeria! 🇳🇬

*Founders:*
👨‍💻 Olajuwon (sidicode) - Lead Developer
👨‍💻 Tariq - Software Engineer

*Version:* 4.0

*Our Mission:* To bring world-class AI to Africa and beyond!

*Features:*
• AI Chat wey sabi answer anything
• Companion wey go dey there for you
• Imoogle Pay for send and receive money
• Bot Builder for your business
• And plenty more!

Made with ❤️ in Lagos, Nigeria
"""
        return """
🌟 *About ImoogleAI*

*ImoogleAI* is a personal AI assistant developed by *Imoogle Technology*, based in Lagos, Nigeria! 🇳🇬

*Founders:*
👨‍💻 Olajuwon (sidicode) - Lead Developer  
👨‍💻 Tariq - Software Engineer

*Version:* 4.0

*Our Mission:* Bringing world-class AI to Africa and the world!

*Features:*
• Intelligent AI chat that can answer anything
• Caring AI companions
• Imoogle Pay for seamless transfers
• Bot Builder for businesses
• Voice-to-voice conversations
• And much more!

Made with ❤️ in Lagos, Nigeria
"""


# Convenience instance
messages = Messages()

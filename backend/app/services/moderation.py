"""
Imoogle 5.0 Group Moderation Service
Spam detection, flood control, and group management.
"""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.database.models import GroupSettings


class ModerationService:
    """
    Group moderation service with:
    1. Spam detection
    2. Flood control
    3. Banned word filtering
    4. Welcome messages for new members
    5. Admin management
    """
    
    def __init__(self):
        # Track message counts for flood control (in-memory, resets on restart)
        self.message_counts: Dict[str, Dict[int, List[datetime]]] = defaultdict(lambda: defaultdict(list))
        
        # Common spam patterns
        self.spam_patterns = [
            r"https?://[^\s]+\.(ru|cn|xyz|top|click)/",  # Suspicious domains
            r"(?i)(make money|earn \$|free bitcoin|crypto airdrop)",
            r"(?i)(join now|click here|limited offer|act fast)",
            r"(?i)(telegram\.me/joinchat|t\.me/joinchat)",  # Invite links
            r"(.)\1{10,}",  # Repeated characters
            r"(?i)(adult|xxx|porn|sex chat)",
        ]
        
        # Compiled patterns for efficiency
        self.compiled_patterns = [re.compile(p) for p in self.spam_patterns]
    
    async def get_or_create_group_settings(
        self,
        db: AsyncSession,
        chat_id: int,
        title: str = None,
    ) -> GroupSettings:
        """Get or create group settings."""
        result = await db.execute(
            select(GroupSettings).where(GroupSettings.chat_id == chat_id)
        )
        settings = result.scalar_one_or_none()
        
        if not settings:
            settings = GroupSettings(
                chat_id=chat_id,
                title=title,
                anti_spam=True,
                anti_flood=True,
                welcome_enabled=True,
            )
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
        
        return settings
    
    async def update_group_settings(
        self,
        db: AsyncSession,
        chat_id: int,
        **kwargs,
    ) -> Dict[str, Any]:
        """Update group settings."""
        settings = await self.get_or_create_group_settings(db, chat_id)
        
        allowed_fields = [
            "anti_spam", "anti_flood", "max_messages_per_minute",
            "welcome_enabled", "welcome_message", "ai_enabled", "ai_trigger",
            "banned_patterns", "admin_ids",
        ]
        
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(settings, field, value)
        
        settings.updated_at = datetime.now()
        await db.commit()
        
        return {"success": True, "message": "Settings updated"}
    
    def is_spam(self, text: str) -> tuple[bool, str]:
        """Check if a message is spam."""
        if not text:
            return False, ""
        
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True, f"Matched pattern: {pattern.pattern[:50]}..."
        
        return False, ""
    
    def check_custom_banned_words(
        self,
        text: str,
        banned_patterns: List[str],
    ) -> tuple[bool, str]:
        """Check against custom banned words/patterns."""
        if not text or not banned_patterns:
            return False, ""
        
        text_lower = text.lower()
        
        for pattern in banned_patterns:
            if pattern.startswith("regex:"):
                # It's a regex pattern
                try:
                    if re.search(pattern[6:], text, re.IGNORECASE):
                        return True, f"Matched: {pattern}"
                except re.error:
                    continue
            else:
                # Simple word match
                if pattern.lower() in text_lower:
                    return True, f"Banned word: {pattern}"
        
        return False, ""
    
    def check_flood(
        self,
        chat_id: int,
        user_id: int,
        max_per_minute: int = 10,
    ) -> tuple[bool, int]:
        """
        Check if user is flooding the chat.
        Returns (is_flooding, message_count)
        """
        key = str(chat_id)
        now = datetime.now()
        one_minute_ago = now - timedelta(minutes=1)
        
        # Clean old messages
        self.message_counts[key][user_id] = [
            t for t in self.message_counts[key][user_id]
            if t > one_minute_ago
        ]
        
        # Add current message
        self.message_counts[key][user_id].append(now)
        
        count = len(self.message_counts[key][user_id])
        
        return count > max_per_minute, count
    
    async def process_message(
        self,
        db: AsyncSession,
        chat_id: int,
        user_id: int,
        text: str,
        is_admin: bool = False,
    ) -> Dict[str, Any]:
        """
        Process a group message and check for violations.
        Returns action to take.
        """
        settings = await self.get_or_create_group_settings(db, chat_id)
        
        # Admins bypass checks
        if is_admin or user_id in (settings.admin_ids or []):
            return {"action": "allow"}
        
        result = {"action": "allow", "violations": []}
        
        # Check spam
        if settings.anti_spam:
            is_spam, reason = self.is_spam(text)
            if is_spam:
                result["action"] = "delete"
                result["violations"].append(f"Spam detected: {reason}")
                result["warn"] = True
        
        # Check custom banned patterns
        if settings.banned_patterns:
            is_banned, reason = self.check_custom_banned_words(text, settings.banned_patterns)
            if is_banned:
                result["action"] = "delete"
                result["violations"].append(reason)
                result["warn"] = True
        
        # Check flood
        if settings.anti_flood:
            is_flooding, count = self.check_flood(
                chat_id, user_id, settings.max_messages_per_minute
            )
            if is_flooding:
                result["action"] = "mute"
                result["mute_duration"] = 300  # 5 minutes
                result["violations"].append(f"Flood detected: {count} messages/minute")
        
        return result
    
    async def get_welcome_message(
        self,
        db: AsyncSession,
        chat_id: int,
        user_name: str,
        group_title: str,
    ) -> Optional[str]:
        """Get welcome message for new members."""
        settings = await self.get_or_create_group_settings(db, chat_id, group_title)
        
        if not settings.welcome_enabled:
            return None
        
        if settings.welcome_message:
            # Replace placeholders
            message = settings.welcome_message
            message = message.replace("{name}", user_name)
            message = message.replace("{group}", group_title)
            return message
        
        # Default welcome message
        return f"Welcome to {group_title}, {user_name}! Feel free to introduce yourself."
    
    async def add_banned_pattern(
        self,
        db: AsyncSession,
        chat_id: int,
        pattern: str,
    ) -> Dict[str, Any]:
        """Add a banned word/pattern."""
        settings = await self.get_or_create_group_settings(db, chat_id)
        
        patterns = settings.banned_patterns or []
        if pattern not in patterns:
            patterns.append(pattern)
            settings.banned_patterns = patterns
            await db.commit()
        
        return {"success": True, "total_patterns": len(patterns)}
    
    async def remove_banned_pattern(
        self,
        db: AsyncSession,
        chat_id: int,
        pattern: str,
    ) -> Dict[str, Any]:
        """Remove a banned word/pattern."""
        settings = await self.get_or_create_group_settings(db, chat_id)
        
        patterns = settings.banned_patterns or []
        if pattern in patterns:
            patterns.remove(pattern)
            settings.banned_patterns = patterns
            await db.commit()
            return {"success": True}
        
        return {"success": False, "error": "Pattern not found"}
    
    async def add_admin(
        self,
        db: AsyncSession,
        chat_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Add a user as group admin (for bot purposes)."""
        settings = await self.get_or_create_group_settings(db, chat_id)
        
        admins = settings.admin_ids or []
        if user_id not in admins:
            admins.append(user_id)
            settings.admin_ids = admins
            await db.commit()
        
        return {"success": True}
    
    async def remove_admin(
        self,
        db: AsyncSession,
        chat_id: int,
        user_id: int,
    ) -> Dict[str, Any]:
        """Remove a user from group admins."""
        settings = await self.get_or_create_group_settings(db, chat_id)
        
        admins = settings.admin_ids or []
        if user_id in admins:
            admins.remove(user_id)
            settings.admin_ids = admins
            await db.commit()
            return {"success": True}
        
        return {"success": False, "error": "User is not an admin"}
    
    def format_group_settings(
        self,
        settings: GroupSettings,
        use_pidgin: bool = False,
    ) -> str:
        """Format group settings for display."""
        anti_spam = "On" if settings.anti_spam else "Off"
        anti_flood = "On" if settings.anti_flood else "Off"
        welcome = "On" if settings.welcome_enabled else "Off"
        ai = "On" if settings.ai_enabled else "Off"
        
        if use_pidgin:
            return f"""**Group Settings for {settings.title}**

Anti-Spam: {anti_spam}
Anti-Flood: {anti_flood} (max {settings.max_messages_per_minute} msgs/min)
Welcome Message: {welcome}
AI Responses: {ai} (trigger: {settings.ai_trigger})
Banned Words: {len(settings.banned_patterns or [])}
Admins: {len(settings.admin_ids or [])}

Use /groupsettings command to change settings."""
        else:
            return f"""**Group Settings for {settings.title}**

Anti-Spam: {anti_spam}
Anti-Flood: {anti_flood} (max {settings.max_messages_per_minute} messages/minute)
Welcome Message: {welcome}
AI Responses: {ai} (trigger: {settings.ai_trigger})
Banned Patterns: {len(settings.banned_patterns or [])}
Bot Admins: {len(settings.admin_ids or [])}

Use /groupsettings to change these settings."""


# Singleton instance
moderation_service = ModerationService()

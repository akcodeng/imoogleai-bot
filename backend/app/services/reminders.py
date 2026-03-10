"""
Imoogle 5.0 Reminder Service
Schedule and manage reminders for users.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.database.models import User, Reminder


class ReminderService:
    """
    Reminder service with:
    1. Natural language time parsing
    2. One-time and recurring reminders
    3. Timezone awareness
    """
    
    def __init__(self):
        pass
    
    def parse_time(
        self,
        time_str: str,
        timezone: str = "Africa/Lagos",
    ) -> Optional[datetime]:
        """
        Parse natural language time expressions.
        Examples:
        - "in 5 minutes"
        - "in 2 hours"
        - "tomorrow at 9am"
        - "next monday"
        - "2024-03-15 14:00"
        """
        import pytz
        
        now = datetime.now(pytz.timezone(timezone))
        time_str = time_str.lower().strip()
        
        # Relative time patterns
        patterns = [
            (r"in (\d+) minute", lambda m: now + timedelta(minutes=int(m.group(1)))),
            (r"in (\d+) hour", lambda m: now + timedelta(hours=int(m.group(1)))),
            (r"in (\d+) day", lambda m: now + timedelta(days=int(m.group(1)))),
            (r"in (\d+) week", lambda m: now + timedelta(weeks=int(m.group(1)))),
            (r"tomorrow", lambda m: now + timedelta(days=1)),
            (r"next week", lambda m: now + timedelta(weeks=1)),
        ]
        
        for pattern, func in patterns:
            match = re.search(pattern, time_str)
            if match:
                return func(match).replace(tzinfo=None)
        
        # Try to parse as datetime
        formats = [
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%d/%m/%Y %H:%M",
            "%d/%m/%Y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue
        
        return None
    
    async def create_reminder(
        self,
        db: AsyncSession,
        user_id: int,
        title: str,
        time_str: str,
        description: str = None,
        recurring: str = None,
        timezone: str = "Africa/Lagos",
    ) -> Dict[str, Any]:
        """Create a new reminder."""
        remind_at = self.parse_time(time_str, timezone)
        
        if not remind_at:
            return {
                "success": False,
                "error": "Could not understand the time. Try formats like 'in 2 hours', 'tomorrow', or '2024-03-15 14:00'"
            }
        
        if remind_at < datetime.now():
            return {
                "success": False,
                "error": "Cannot set a reminder in the past"
            }
        
        reminder = Reminder(
            user_id=user_id,
            title=title,
            description=description,
            remind_at=remind_at,
            is_recurring=recurring is not None,
            recurrence_pattern=recurring,
        )
        
        db.add(reminder)
        await db.commit()
        await db.refresh(reminder)
        
        return {
            "success": True,
            "reminder_id": reminder.id,
            "title": title,
            "remind_at": remind_at.strftime("%Y-%m-%d %H:%M"),
            "message": f"Reminder set for {remind_at.strftime('%B %d, %Y at %I:%M %p')}"
        }
    
    async def get_user_reminders(
        self,
        db: AsyncSession,
        user_id: int,
        include_completed: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get all reminders for a user."""
        query = select(Reminder).where(Reminder.user_id == user_id)
        
        if not include_completed:
            query = query.where(Reminder.is_completed == False)
        
        query = query.order_by(Reminder.remind_at)
        
        result = await db.execute(query)
        reminders = result.scalars().all()
        
        return [
            {
                "id": r.id,
                "title": r.title,
                "description": r.description,
                "remind_at": r.remind_at.strftime("%Y-%m-%d %H:%M"),
                "is_recurring": r.is_recurring,
                "recurrence_pattern": r.recurrence_pattern,
                "is_completed": r.is_completed,
            }
            for r in reminders
        ]
    
    async def get_due_reminders(
        self,
        db: AsyncSession,
    ) -> List[Reminder]:
        """Get all reminders that are due to be sent."""
        now = datetime.now()
        
        result = await db.execute(
            select(Reminder)
            .where(Reminder.remind_at <= now)
            .where(Reminder.is_sent == False)
            .where(Reminder.is_completed == False)
        )
        
        return result.scalars().all()
    
    async def mark_reminder_sent(
        self,
        db: AsyncSession,
        reminder_id: int,
    ) -> None:
        """Mark a reminder as sent."""
        result = await db.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        reminder = result.scalar_one_or_none()
        
        if not reminder:
            return
        
        if reminder.is_recurring and reminder.recurrence_pattern:
            # Schedule next occurrence
            next_time = self._calculate_next_occurrence(
                reminder.remind_at,
                reminder.recurrence_pattern,
            )
            reminder.remind_at = next_time
            reminder.is_sent = False
        else:
            reminder.is_sent = True
            reminder.is_completed = True
        
        await db.commit()
    
    def _calculate_next_occurrence(
        self,
        current: datetime,
        pattern: str,
    ) -> datetime:
        """Calculate next occurrence for recurring reminder."""
        patterns = {
            "daily": timedelta(days=1),
            "weekly": timedelta(weeks=1),
            "monthly": timedelta(days=30),
        }
        
        delta = patterns.get(pattern, timedelta(days=1))
        return current + delta
    
    async def complete_reminder(
        self,
        db: AsyncSession,
        user_id: int,
        reminder_id: int,
    ) -> Dict[str, Any]:
        """Mark a reminder as completed."""
        result = await db.execute(
            select(Reminder)
            .where(Reminder.id == reminder_id)
            .where(Reminder.user_id == user_id)
        )
        reminder = result.scalar_one_or_none()
        
        if not reminder:
            return {"success": False, "error": "Reminder not found"}
        
        reminder.is_completed = True
        await db.commit()
        
        return {"success": True, "message": "Reminder marked as completed"}
    
    async def delete_reminder(
        self,
        db: AsyncSession,
        user_id: int,
        reminder_id: int,
    ) -> Dict[str, Any]:
        """Delete a reminder."""
        result = await db.execute(
            select(Reminder)
            .where(Reminder.id == reminder_id)
            .where(Reminder.user_id == user_id)
        )
        reminder = result.scalar_one_or_none()
        
        if not reminder:
            return {"success": False, "error": "Reminder not found"}
        
        await db.delete(reminder)
        await db.commit()
        
        return {"success": True, "message": "Reminder deleted"}
    
    def format_reminders(
        self,
        reminders: List[Dict[str, Any]],
        use_pidgin: bool = False,
    ) -> str:
        """Format reminders for display."""
        if not reminders:
            if use_pidgin:
                return "You no get any reminder. Use /remind to set one."
            return "You don't have any reminders. Use /remind to set one."
        
        if use_pidgin:
            formatted = "**Your Reminders:**\n\n"
        else:
            formatted = "**Your Reminders:**\n\n"
        
        for r in reminders:
            status = "Done" if r["is_completed"] else "Pending"
            recurring = " (Recurring)" if r["is_recurring"] else ""
            
            formatted += f"**{r['id']}.** {r['title']}{recurring}\n"
            formatted += f"   When: {r['remind_at']}\n"
            if r["description"]:
                formatted += f"   Note: {r['description']}\n"
            formatted += f"   Status: {status}\n\n"
        
        return formatted


# Singleton instance
reminder_service = ReminderService()

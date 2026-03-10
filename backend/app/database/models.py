"""
Imoogle 5.0 Database Models
SQLAlchemy models for PostgreSQL database.
"""

from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Boolean, Float,
    DateTime, ForeignKey, JSON, Enum, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
import enum

Base = declarative_base()


class UserTier(str, enum.Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    BUSINESS = "business"


class TransactionType(str, enum.Enum):
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    TRANSFER = "transfer"
    SUBSCRIPTION = "subscription"
    BOT_PAYMENT = "bot_payment"


class TransactionStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BotStatus(str, enum.Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    
    # Personalization
    language = Column(String(10), default="en")
    country = Column(String(100), nullable=True)
    city = Column(String(100), nullable=True)
    timezone = Column(String(50), default="Africa/Lagos")
    use_pidgin = Column(Boolean, default=False)
    
    # Subscription
    tier = Column(Enum(UserTier), default=UserTier.FREE)
    subscription_expires = Column(DateTime, nullable=True)
    
    # Usage tracking
    messages_today = Column(Integer, default=0)
    images_today = Column(Integer, default=0)
    voice_today = Column(Integer, default=0)
    last_message_date = Column(DateTime, nullable=True)
    
    # Companion settings
    companion_enabled = Column(Boolean, default=False)
    companion_persona = Column(String(50), nullable=True)
    companion_nickname = Column(String(100), nullable=True)
    
    # Preferences
    preferences = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_active = Column(DateTime, server_default=func.now())
    
    # Relationships
    wallet = relationship("Wallet", back_populates="user", uselist=False)
    conversations = relationship("Conversation", back_populates="user")
    reminders = relationship("Reminder", back_populates="user")
    bots = relationship("UserBot", back_populates="owner")
    
    __table_args__ = (
        Index("idx_user_telegram", "telegram_id"),
        Index("idx_user_tier", "tier"),
    )


class Wallet(Base):
    __tablename__ = "wallets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    
    # Balance in Naira (stored as kobo - smallest unit)
    balance = Column(BigInteger, default=0)
    
    # ImoCoin balance
    imocoin_balance = Column(BigInteger, default=0)
    
    # Security
    pin_hash = Column(String(255), nullable=True)
    pin_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="wallet")
    transactions = relationship("Transaction", back_populates="wallet")


class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    wallet_id = Column(Integer, ForeignKey("wallets.id", ondelete="CASCADE"))
    
    # Transaction details
    reference = Column(String(100), unique=True, nullable=False)
    type = Column(Enum(TransactionType), nullable=False)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING)
    
    # Amount in kobo
    amount = Column(BigInteger, nullable=False)
    fee = Column(BigInteger, default=0)
    
    # For transfers
    recipient_wallet_id = Column(Integer, ForeignKey("wallets.id"), nullable=True)
    
    # Metadata
    description = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    
    # Payment provider reference
    provider_reference = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    wallet = relationship("Wallet", back_populates="transactions", foreign_keys=[wallet_id])
    
    __table_args__ = (
        Index("idx_transaction_reference", "reference"),
        Index("idx_transaction_wallet", "wallet_id"),
        Index("idx_transaction_status", "status"),
    )


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Conversation type
    is_companion = Column(Boolean, default=False)
    companion_persona = Column(String(50), nullable=True)
    
    # Context
    context = Column(JSON, default=list)  # List of messages
    summary = Column(Text, nullable=True)  # AI-generated summary for long contexts
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id", ondelete="CASCADE"))
    
    # Message content
    role = Column(String(20), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Media
    has_voice = Column(Boolean, default=False)
    has_image = Column(Boolean, default=False)
    media_url = Column(String(500), nullable=True)
    
    # Metadata
    tokens_used = Column(Integer, default=0)
    model_used = Column(String(100), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class Reminder(Base):
    __tablename__ = "reminders"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Reminder details
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Scheduling
    remind_at = Column(DateTime, nullable=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_pattern = Column(String(50), nullable=True)  # daily, weekly, monthly
    
    # Status
    is_completed = Column(Boolean, default=False)
    is_sent = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reminders")
    
    __table_args__ = (
        Index("idx_reminder_user", "user_id"),
        Index("idx_reminder_time", "remind_at"),
    )


class UserBot(Base):
    """Bots created by users through Bot Builder"""
    __tablename__ = "user_bots"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    
    # Bot details
    bot_token = Column(String(255), nullable=False)
    bot_username = Column(String(255), nullable=True)
    bot_name = Column(String(255), nullable=False)
    
    # Configuration
    system_prompt = Column(Text, nullable=True)
    welcome_message = Column(Text, nullable=True)
    personality = Column(String(50), default="professional")
    
    # Features
    enable_ai_chat = Column(Boolean, default=True)
    enable_web_search = Column(Boolean, default=False)
    enable_image_gen = Column(Boolean, default=False)
    
    # Auto-responses
    auto_responses = Column(JSON, default=dict)  # keyword -> response mapping
    
    # Group moderation settings
    anti_spam = Column(Boolean, default=False)
    welcome_new_members = Column(Boolean, default=True)
    
    # Status
    status = Column(Enum(BotStatus), default=BotStatus.ACTIVE)
    
    # Subscription
    plan = Column(String(20), default="basic")
    expires_at = Column(DateTime, nullable=True)
    
    # Stats
    total_messages = Column(Integer, default=0)
    total_users = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="bots")
    
    __table_args__ = (
        Index("idx_userbot_owner", "owner_id"),
        Index("idx_userbot_status", "status"),
    )


class GroupSettings(Base):
    """Settings for groups where Imoogle is admin"""
    __tablename__ = "group_settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    
    # Basic info
    title = Column(String(255), nullable=True)
    
    # Moderation settings
    anti_spam = Column(Boolean, default=True)
    anti_flood = Column(Boolean, default=True)
    max_messages_per_minute = Column(Integer, default=10)
    
    # Welcome settings
    welcome_enabled = Column(Boolean, default=True)
    welcome_message = Column(Text, nullable=True)
    
    # AI settings
    ai_enabled = Column(Boolean, default=True)
    ai_trigger = Column(String(50), default="@imoogle")  # How to trigger AI in group
    
    # Banned words/patterns
    banned_patterns = Column(JSON, default=list)
    
    # Admin list (Telegram user IDs)
    admin_ids = Column(JSON, default=list)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    __table_args__ = (
        Index("idx_group_chat", "chat_id"),
    )

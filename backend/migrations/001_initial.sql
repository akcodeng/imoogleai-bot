-- ============================================
-- IMOOGLE 5.0 - Initial Database Migration
-- Run this on your PostgreSQL database
-- ============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============== USERS ==============
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY,  -- Telegram user ID
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    language VARCHAR(10) DEFAULT 'en',
    country VARCHAR(10),
    city VARCHAR(255),
    timezone VARCHAR(50) DEFAULT 'Africa/Lagos',
    
    -- Preferences
    ai_personality VARCHAR(50) DEFAULT 'friendly',
    voice_mode BOOLEAN DEFAULT FALSE,
    voice_to_voice BOOLEAN DEFAULT FALSE,
    preferred_voice VARCHAR(50) DEFAULT 'female',
    interests TEXT[],
    
    -- Status
    is_premium BOOLEAN DEFAULT FALSE,
    is_banned BOOLEAN DEFAULT FALSE,
    onboarding_complete BOOLEAN DEFAULT FALSE,
    current_mode VARCHAR(50) DEFAULT 'chat',
    active_companion_id UUID,
    
    -- Stats
    total_messages INTEGER DEFAULT 0,
    images_generated INTEGER DEFAULT 0,
    voice_messages INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_country ON users(country);
CREATE INDEX idx_users_last_active ON users(last_active);

-- ============== CONVERSATIONS ==============
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    mode VARCHAR(50) DEFAULT 'chat',
    title VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    message_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_active ON conversations(is_active);

-- ============== MESSAGES ==============
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text',  -- 'text', 'voice', 'image', 'document'
    metadata JSONB,
    tokens_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_messages_conversation ON messages(conversation_id);
CREATE INDEX idx_messages_user ON messages(user_id);
CREATE INDEX idx_messages_created ON messages(created_at);

-- ============== COMPANIONS ==============
CREATE TABLE IF NOT EXISTS companions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    persona_name VARCHAR(100) NOT NULL,
    persona_gender VARCHAR(20),
    persona_country VARCHAR(10),
    
    -- Relationship
    relationship_level INTEGER DEFAULT 0,
    mood VARCHAR(50) DEFAULT 'happy',
    total_messages INTEGER DEFAULT 0,
    
    -- Memory
    memory JSONB DEFAULT '{}',
    last_checkup TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_companions_user ON companions(user_id);
CREATE INDEX idx_companions_active ON companions(is_active);

-- ============== WALLETS ==============
CREATE TABLE IF NOT EXISTS wallets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    naira_balance DECIMAL(15, 2) DEFAULT 0.00,
    imocoin_balance DECIMAL(15, 2) DEFAULT 0.00,
    
    -- Security
    pin_hash VARCHAR(255),
    pin_attempts INTEGER DEFAULT 0,
    is_locked BOOLEAN DEFAULT FALSE,
    
    -- Bank details
    bank_code VARCHAR(10),
    account_number VARCHAR(20),
    account_name VARCHAR(255),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_wallets_user ON wallets(user_id);

-- ============== TRANSACTIONS ==============
CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    wallet_id UUID REFERENCES wallets(id) ON DELETE CASCADE,
    
    transaction_type VARCHAR(50) NOT NULL,  -- deposit, withdraw, send, receive, buy_imocoin
    amount DECIMAL(15, 2) NOT NULL,
    fee DECIMAL(15, 2) DEFAULT 0.00,
    currency VARCHAR(10) DEFAULT 'NGN',
    
    -- Counterparty
    counterparty_id BIGINT REFERENCES users(id),
    
    -- Payment provider
    provider VARCHAR(50),  -- paystack, korapay, internal
    provider_reference VARCHAR(255),
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',  -- pending, completed, failed, reversed
    
    -- Metadata
    description TEXT,
    metadata JSONB,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_wallet ON transactions(wallet_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_reference ON transactions(provider_reference);

-- ============== USER BOTS ==============
CREATE TABLE IF NOT EXISTS user_bots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    owner_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    bot_token VARCHAR(255) NOT NULL,
    bot_username VARCHAR(255),
    bot_name VARCHAR(255),
    
    -- Configuration
    welcome_message TEXT,
    auto_replies JSONB DEFAULT '{}',
    ai_enabled BOOLEAN DEFAULT FALSE,
    ai_prompt TEXT,
    
    -- Features
    features TEXT[],
    
    -- Stats
    subscriber_count INTEGER DEFAULT 0,
    total_messages INTEGER DEFAULT 0,
    
    -- Subscription
    subscription_plan VARCHAR(50),
    subscription_expires TIMESTAMP WITH TIME ZONE,
    
    -- Status
    is_active BOOLEAN DEFAULT FALSE,
    webhook_url VARCHAR(500),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_user_bots_owner ON user_bots(owner_id);
CREATE INDEX idx_user_bots_username ON user_bots(bot_username);
CREATE INDEX idx_user_bots_active ON user_bots(is_active);

-- ============== BOT SUBSCRIPTIONS ==============
CREATE TABLE IF NOT EXISTS bot_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    plan VARCHAR(50) NOT NULL,  -- starter, growth, business, enterprise
    price DECIMAL(10, 2) NOT NULL,
    
    -- Period
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    auto_renew BOOLEAN DEFAULT TRUE,
    
    -- Payment
    transaction_id UUID REFERENCES transactions(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_bot_subs_user ON bot_subscriptions(user_id);
CREATE INDEX idx_bot_subs_active ON bot_subscriptions(is_active);

-- ============== REMINDERS ==============
CREATE TABLE IF NOT EXISTS reminders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    
    remind_at TIMESTAMP WITH TIME ZONE NOT NULL,
    repeat_interval VARCHAR(50),  -- none, daily, weekly, monthly
    
    -- Status
    is_sent BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_reminders_user ON reminders(user_id);
CREATE INDEX idx_reminders_time ON reminders(remind_at);
CREATE INDEX idx_reminders_active ON reminders(is_active);

-- ============== GENERATED IMAGES ==============
CREATE TABLE IF NOT EXISTS generated_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    prompt TEXT NOT NULL,
    style VARCHAR(50),
    provider VARCHAR(50),  -- stability, leonardo, mistral
    
    image_url TEXT,
    thumbnail_url TEXT,
    
    -- Metadata
    width INTEGER,
    height INTEGER,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_images_user ON generated_images(user_id);
CREATE INDEX idx_images_created ON generated_images(created_at);

-- ============== GROUP SETTINGS ==============
CREATE TABLE IF NOT EXISTS group_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id BIGINT UNIQUE NOT NULL,
    
    -- Basic info
    title VARCHAR(255),
    added_by BIGINT REFERENCES users(id),
    
    -- Moderation settings
    anti_spam BOOLEAN DEFAULT TRUE,
    block_links BOOLEAN DEFAULT FALSE,
    block_forwards BOOLEAN DEFAULT FALSE,
    block_media BOOLEAN DEFAULT FALSE,
    profanity_filter BOOLEAN DEFAULT FALSE,
    
    -- Messages
    welcome_message TEXT,
    rules TEXT,
    
    -- Warnings
    max_warnings INTEGER DEFAULT 3,
    warn_action VARCHAR(50) DEFAULT 'mute',
    
    -- Stats
    member_count INTEGER DEFAULT 0,
    message_count INTEGER DEFAULT 0,
    
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_group_settings_chat ON group_settings(chat_id);

-- ============== GROUP WARNINGS ==============
CREATE TABLE IF NOT EXISTS group_warnings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chat_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    
    reason TEXT,
    warned_by BIGINT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_warnings_chat_user ON group_warnings(chat_id, user_id);

-- ============== PREMIUM SUBSCRIPTIONS ==============
CREATE TABLE IF NOT EXISTS premium_subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    
    plan VARCHAR(50) NOT NULL,  -- monthly, yearly, student
    price DECIMAL(10, 2) NOT NULL,
    
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    
    is_active BOOLEAN DEFAULT TRUE,
    auto_renew BOOLEAN DEFAULT TRUE,
    
    transaction_id UUID REFERENCES transactions(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_premium_user ON premium_subscriptions(user_id);
CREATE INDEX idx_premium_active ON premium_subscriptions(is_active);

-- ============== FEEDBACK ==============
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    
    category VARCHAR(50),  -- bug, feature, complaint, praise
    message TEXT NOT NULL,
    
    is_resolved BOOLEAN DEFAULT FALSE,
    admin_response TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_feedback_user ON feedback(user_id);
CREATE INDEX idx_feedback_resolved ON feedback(is_resolved);

-- ============== ANALYTICS ==============
CREATE TABLE IF NOT EXISTS analytics_daily (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    
    -- User metrics
    new_users INTEGER DEFAULT 0,
    active_users INTEGER DEFAULT 0,
    premium_users INTEGER DEFAULT 0,
    
    -- Message metrics
    total_messages INTEGER DEFAULT 0,
    ai_messages INTEGER DEFAULT 0,
    voice_messages INTEGER DEFAULT 0,
    
    -- Feature usage
    images_generated INTEGER DEFAULT 0,
    searches_performed INTEGER DEFAULT 0,
    payments_made INTEGER DEFAULT 0,
    
    -- Revenue
    revenue_ngn DECIMAL(15, 2) DEFAULT 0,
    
    UNIQUE(date)
);

CREATE INDEX idx_analytics_date ON analytics_daily(date);

-- ============== FUNCTIONS ==============

-- Update timestamp trigger
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_companions_updated_at BEFORE UPDATE ON companions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_wallets_updated_at BEFORE UPDATE ON wallets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_bots_updated_at BEFORE UPDATE ON user_bots
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_group_settings_updated_at BEFORE UPDATE ON group_settings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============== DONE ==============
COMMENT ON DATABASE imoogle IS 'Imoogle 5.0 - AI Telegram Bot Database';

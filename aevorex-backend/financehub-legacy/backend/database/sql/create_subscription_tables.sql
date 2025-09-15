-- SQL Schema for Subscription Management
-- File: modules/financehub/backend/database/sql/create_subscription_tables.sql

-- Enable pgcrypto for modern UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- User Table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    auth_provider_id VARCHAR(255), -- Pl. Google user ID, Clerk user ID
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    is_active BOOLEAN DEFAULT TRUE NOT NULL
);

-- Add index for faster lookups by auth_provider_id
CREATE INDEX IF NOT EXISTS idx_users_auth_provider_id ON users (auth_provider_id);

-- Subscription Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    external_id VARCHAR(255) NOT NULL, -- Provider-specific subscription ID
    provider VARCHAR(50) NOT NULL,    -- 'stripe', 'lemonsqueezy', 'paddle'
    plan VARCHAR(50) NOT NULL,         -- 'free', 'pro', 'team', 'enterprise'
    status VARCHAR(50) NOT NULL,       -- 'active', 'trialing', 'past_due', 'canceled', etc.
    current_period_start TIMESTAMP WITH TIME ZONE NOT NULL,
    current_period_end TIMESTAMP WITH TIME ZONE NOT NULL,
    trial_start TIMESTAMP WITH TIME ZONE,
    trial_end TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE(provider, external_id) -- Ensures uniqueness for provider-specific IDs
);

-- Enhanced indexes for better performance
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON subscriptions (user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions (status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_status ON subscriptions (user_id, status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_period ON subscriptions (user_id, current_period_end);

-- Ensure only one active subscription per user
CREATE UNIQUE INDEX IF NOT EXISTS idx_subscriptions_user_active 
ON subscriptions (user_id) 
WHERE status IN ('active', 'trialing', 'past_due');

-- Webhook Events Table (for Idempotency)
CREATE TABLE IF NOT EXISTS webhook_events (
    id VARCHAR(255) PRIMARY KEY, -- Unique ID from the webhook event (e.g., Stripe event ID)
    provider VARCHAR(50) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Add index for faster lookups by event ID and provider
CREATE INDEX IF NOT EXISTS idx_webhook_events_provider_id ON webhook_events (provider, id);
CREATE INDEX IF NOT EXISTS idx_webhook_events_received ON webhook_events (received_at);

-- Plan Mapping Table (for flexible plan configuration)
CREATE TABLE IF NOT EXISTS plan_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    provider VARCHAR(50) NOT NULL, -- 'lemonsqueezy', 'stripe', 'paddle'
    external_id VARCHAR(255) NOT NULL, -- Provider-specific variant/price ID
    plan VARCHAR(50) NOT NULL, -- 'free', 'pro', 'team', 'enterprise'
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    UNIQUE(provider, external_id)
);

-- Add index for plan mappings
CREATE INDEX IF NOT EXISTS idx_plan_mappings_provider_external ON plan_mappings (provider, external_id);
CREATE INDEX IF NOT EXISTS idx_plan_mappings_plan ON plan_mappings (plan);
CREATE INDEX IF NOT EXISTS idx_plan_mappings_active ON plan_mappings (is_active) WHERE is_active = TRUE;

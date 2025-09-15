-- Checkout Tracking Table for Lemon Squeezy Integration
-- This table tracks checkout sessions to correlate webhook events with users

CREATE TABLE IF NOT EXISTS checkout_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    checkout_id VARCHAR(255) NOT NULL UNIQUE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    variant_id VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    webhook_processed_at TIMESTAMP WITH TIME ZONE,
    webhook_event_id VARCHAR(255),
    
    -- Indexes for efficient lookups
    CONSTRAINT valid_status CHECK (status IN ('pending', 'active', 'failed', 'cancelled')),
    CONSTRAINT valid_variant_id CHECK (variant_id ~ '^[0-9]+$')
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_checkout_tracking_checkout_id ON checkout_tracking(checkout_id);
CREATE INDEX IF NOT EXISTS idx_checkout_tracking_user_id ON checkout_tracking(user_id);
CREATE INDEX IF NOT EXISTS idx_checkout_tracking_status ON checkout_tracking(status);
CREATE INDEX IF NOT EXISTS idx_checkout_tracking_created_at ON checkout_tracking(created_at);

-- UNIQUE constraints for idempotency
CREATE UNIQUE INDEX IF NOT EXISTS idx_checkout_tracking_checkout_id_unique ON checkout_tracking(checkout_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_checkout_tracking_webhook_event_id_unique ON checkout_tracking(webhook_event_id) WHERE webhook_event_id IS NOT NULL;

-- Trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_checkout_tracking_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_checkout_tracking_updated_at
    BEFORE UPDATE ON checkout_tracking
    FOR EACH ROW
    EXECUTE FUNCTION update_checkout_tracking_updated_at();

-- Comments for documentation
COMMENT ON TABLE checkout_tracking IS 'Tracks Lemon Squeezy checkout sessions for webhook correlation';
COMMENT ON COLUMN checkout_tracking.checkout_id IS 'Lemon Squeezy checkout ID from API response';
COMMENT ON COLUMN checkout_tracking.user_id IS 'Internal user ID for correlation';
COMMENT ON COLUMN checkout_tracking.variant_id IS 'Lemon Squeezy variant ID (product plan)';
COMMENT ON COLUMN checkout_tracking.status IS 'Checkout status: pending, active, failed, cancelled';
COMMENT ON COLUMN checkout_tracking.webhook_event_id IS 'Lemon Squeezy webhook event ID for idempotency';

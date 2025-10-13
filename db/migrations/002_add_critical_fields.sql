-- Migration 002: Add critical fields for production readiness
-- Adds: double opt-in, idempotency, EMA indicators, asset type support

-- 1. Add double opt-in to email_subscribers
ALTER TABLE email_subscribers 
  ADD COLUMN IF NOT EXISTS confirmed BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS confirmation_token VARCHAR(64) UNIQUE,
  ADD COLUMN IF NOT EXISTS confirmed_at TIMESTAMPTZ;

COMMENT ON COLUMN email_subscribers.confirmed IS 'True after user clicks confirmation link (double opt-in)';
COMMENT ON COLUMN email_subscribers.confirmation_token IS 'Token sent in confirmation email';

-- 2. Add idempotency to signals (prevent duplicates on job reruns)
ALTER TABLE signals
  ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255) UNIQUE,
  ADD COLUMN IF NOT EXISTS rule_version VARCHAR(50);

COMMENT ON COLUMN signals.idempotency_key IS 'Format: {symbol}:{rule_version}:{timestamp} - prevents duplicate signals';
COMMENT ON COLUMN signals.rule_version IS 'Signal algorithm version (e.g., "rsi_v1", "ema_cross_v1")';

-- 3. Add EMA indicators (RSI + EMA per docs, not MACD)
ALTER TABLE indicators
  ADD COLUMN IF NOT EXISTS ema_12 DECIMAL(20, 8),
  ADD COLUMN IF NOT EXISTS ema_26 DECIMAL(20, 8);

COMMENT ON COLUMN indicators.ema_12 IS 'Exponential Moving Average (12-period)';
COMMENT ON COLUMN indicators.ema_26 IS 'Exponential Moving Average (26-period)';

-- 4. Fix asset_type constraint to support all 4 MVP asset classes
ALTER TABLE symbols DROP CONSTRAINT IF EXISTS symbols_asset_type_check;
ALTER TABLE symbols ADD CONSTRAINT symbols_asset_type_check 
  CHECK (asset_type IN ('crypto', 'stock', 'etf', 'forex'));

-- 5. Update active subscribers index to respect double opt-in
DROP INDEX IF EXISTS idx_email_subscribers_active;
CREATE INDEX idx_email_subscribers_active ON email_subscribers(email)
  WHERE confirmed = true AND unsubscribed = false;

COMMENT ON INDEX idx_email_subscribers_active IS 'Active confirmed subscribers only';


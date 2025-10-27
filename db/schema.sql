-- Trading Signals MVP Database Schema
-- PostgreSQL 15+
--
-- Complete initial schema including double opt-in, idempotency, and EMA indicators
-- This is the first migration for the project (no prior migrations have been run)
--
-- See db/README.md for setup instructions and design rationale

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Core symbols we track (MVP: 4 assets across different classes)
CREATE TABLE symbols (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    asset_type VARCHAR(20) NOT NULL CHECK (asset_type IN ('crypto', 'stock', 'etf', 'forex')),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Raw OHLCV market data from Yahoo Finance
CREATE TABLE market_data (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) REFERENCES symbols(symbol) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    open DECIMAL(20, 8) NOT NULL CHECK (open > 0),
    high DECIMAL(20, 8) NOT NULL CHECK (high > 0),
    low DECIMAL(20, 8) NOT NULL CHECK (low > 0),
    close DECIMAL(20, 8) NOT NULL CHECK (close > 0),
    volume BIGINT NOT NULL CHECK (volume >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(symbol, timestamp)
);

CREATE INDEX idx_market_data_symbol_time ON market_data(symbol, timestamp DESC);
CREATE INDEX idx_market_data_created ON market_data(created_at DESC);

-- Calculated technical indicators (RSI + EMA for MVP, MACD optional)
CREATE TABLE indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) REFERENCES symbols(symbol) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,

    -- RSI (Relative Strength Index)
    rsi DECIMAL(5, 2) CHECK (rsi >= 0 AND rsi <= 100),

    -- EMA (Exponential Moving Average)
    ema_12 DECIMAL(20, 8),
    ema_26 DECIMAL(20, 8),

    -- MACD (Moving Average Convergence Divergence - optional)
    macd DECIMAL(10, 4),
    macd_signal DECIMAL(10, 4),
    macd_histogram DECIMAL(10, 4),

    calculated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(symbol, timestamp)
);

CREATE INDEX idx_indicators_symbol_time ON indicators(symbol, timestamp DESC);
CREATE INDEX idx_indicators_rsi ON indicators(rsi) WHERE rsi IS NOT NULL;

-- Generated trading signals
CREATE TABLE signals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) REFERENCES symbols(symbol) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('BUY', 'SELL', 'HOLD')),
    strength DECIMAL(5, 2) NOT NULL CHECK (strength >= 0 AND strength <= 100),
    reasoning TEXT[] NOT NULL,
    price_at_signal DECIMAL(20, 8),
    idempotency_key VARCHAR(255) UNIQUE,
    rule_version VARCHAR(50),
    generated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(symbol, timestamp)
);

CREATE INDEX idx_signals_symbol_time ON signals(symbol, timestamp DESC);
CREATE INDEX idx_signals_strength ON signals(strength DESC);
CREATE INDEX idx_signals_type ON signals(signal_type);

-- Backtest summaries
CREATE TABLE IF NOT EXISTS backtests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) REFERENCES symbols(symbol) ON DELETE CASCADE,
    range_label VARCHAR(10),
    start_timestamp TIMESTAMPTZ,
    end_timestamp TIMESTAMPTZ,
    trades INTEGER,
    win_rate DECIMAL(5, 2),
    avg_return DECIMAL(6, 2),
    total_return DECIMAL(10, 2),
    rule_version VARCHAR(50),
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_backtests_symbol_range_rule
ON backtests(symbol, range_label, rule_version);

-- Email subscribers (no authentication, email-only with double opt-in)
CREATE TABLE email_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    confirmed BOOLEAN DEFAULT false,
    confirmation_token VARCHAR(64) UNIQUE,
    confirmed_at TIMESTAMPTZ,
    last_email_sent_at TIMESTAMPTZ,
    unsubscribed BOOLEAN DEFAULT false,
    unsubscribe_token VARCHAR(64) UNIQUE DEFAULT encode(gen_random_bytes(32), 'hex')
);

CREATE INDEX idx_email_subscribers_email ON email_subscribers(email);
CREATE INDEX idx_email_subscribers_active ON email_subscribers(email) WHERE confirmed = true AND unsubscribed = false;

-- Track sent notifications (for rate limiting)
CREATE TABLE sent_notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    signal_id UUID REFERENCES signals(id) ON DELETE CASCADE,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sent_notifications_email ON sent_notifications(email, sent_at DESC);
CREATE INDEX idx_sent_notifications_signal ON sent_notifications(signal_id);

-- Performance tracking view (last 30 days)
CREATE OR REPLACE VIEW signal_performance AS
SELECT
    s.symbol,
    s.signal_type,
    COUNT(*) as total_signals,
    AVG(s.strength) as avg_strength,
    MIN(s.timestamp) as first_signal,
    MAX(s.timestamp) as last_signal
FROM signals s
WHERE s.timestamp > NOW() - INTERVAL '30 days'
GROUP BY s.symbol, s.signal_type;

-- Comments
COMMENT ON TABLE symbols IS 'Tracked assets (BTC-USD, AAPL, IVV, BRL=X for MVP - 4 asset classes)';
COMMENT ON TABLE market_data IS 'Raw OHLCV data from Yahoo Finance, 15-min bars';
COMMENT ON TABLE indicators IS 'Calculated technical indicators (RSI, EMA12, EMA26)';
COMMENT ON TABLE signals IS 'Generated trading signals with confidence scores and idempotency';
COMMENT ON TABLE email_subscribers IS 'Email subscribers with double opt-in confirmation';
COMMENT ON TABLE sent_notifications IS 'Audit log of sent emails for rate limiting and tracking';

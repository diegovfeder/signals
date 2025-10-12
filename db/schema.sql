-- Trading Signals MVP Database Schema
-- PostgreSQL 15+

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Core symbols we track (MVP: 3 symbols only)
CREATE TABLE symbols (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    asset_type VARCHAR(20) NOT NULL CHECK (asset_type IN ('crypto', 'stock')),
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

-- Calculated technical indicators (RSI + MACD only for MVP)
CREATE TABLE indicators (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(20) REFERENCES symbols(symbol) ON DELETE CASCADE,
    timestamp TIMESTAMPTZ NOT NULL,

    -- RSI (Relative Strength Index)
    rsi DECIMAL(5, 2) CHECK (rsi >= 0 AND rsi <= 100),

    -- MACD (Moving Average Convergence Divergence)
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
    generated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(symbol, timestamp)
);

CREATE INDEX idx_signals_symbol_time ON signals(symbol, timestamp DESC);
CREATE INDEX idx_signals_strength ON signals(strength DESC);
CREATE INDEX idx_signals_type ON signals(signal_type);

-- Email subscribers (no authentication, email-only)
CREATE TABLE email_subscribers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    subscribed_at TIMESTAMPTZ DEFAULT NOW(),
    last_email_sent_at TIMESTAMPTZ,
    unsubscribed BOOLEAN DEFAULT false,
    unsubscribe_token VARCHAR(64) UNIQUE DEFAULT encode(gen_random_bytes(32), 'hex')
);

CREATE INDEX idx_email_subscribers_email ON email_subscribers(email);
CREATE INDEX idx_email_subscribers_active ON email_subscribers(unsubscribed, subscribed_at DESC);

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
COMMENT ON TABLE symbols IS 'Tracked assets (BTC-USD, ETH-USD, TSLA for MVP)';
COMMENT ON TABLE market_data IS 'Raw OHLCV data from Yahoo Finance, fetched hourly';
COMMENT ON TABLE indicators IS 'Calculated technical indicators (RSI, MACD)';
COMMENT ON TABLE signals IS 'Generated trading signals with confidence scores';
COMMENT ON TABLE email_subscribers IS 'Users subscribed to email notifications';
COMMENT ON TABLE sent_notifications IS 'Audit log of sent emails for rate limiting';

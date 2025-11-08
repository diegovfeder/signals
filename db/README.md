# Database Design

## Current State (MVP)

Single PostgreSQL database shared by the pipeline and backend. Today we store *daily* OHLCV bars for two assets (BTC-USD, AAPL), indicators, generated signals, and subscriber metadata.

### Tables & Daily Volume

| Table | Purpose | Rows/Day | Notes |
|-------|---------|----------|-------|
| `symbols` | Asset registry | Static | 2 default rows (`BTC-USD`, `AAPL`). |
| `market_data` | Daily OHLCV bars | 2 (1 per symbol) | Backfill up to 10y per asset. |
| `indicators` | RSI/EMA/MACD per bar | 2 | Mirrors `market_data` timestamps. |
| `signals` | BUY/HOLD results | 2 | Daily signals with reasoning + strength. |
| `email_subscribers` | Double opt-in records | Growth dependent | Stores confirmation/unsubscribe tokens. |
| `sent_notifications` | (future) signal notification audit | On demand | Populated when notification dispatcher emails subscribers. |

### Size Estimates

- **Initial 10y backfill** (2 assets × ~2,500 trading days):
  - `market_data`: ~5K rows ⇒ ~1 MB
  - `indicators`: ~5K rows ⇒ ~0.8 MB
- **6 months daily runtime** adds ~360 rows per table (~80 KB).

Total footprint remains <5 MB, far below Supabase’s free 500 MB limit. Adding more assets increases linearly (≈0.4 MB per year per symbol at daily cadence).

## Design Principles

1. **Daily OHLCV snapshots** – nightly pipeline fetches Yahoo Finance daily bars (backfill up to 10y) so indicator windows/backtests have sufficient context.
2. **Double opt-in email** – `confirmation_token` + `unsubscribe_token` keep the list clean.
3. **Idempotent signals** – `idempotency_key` prevents duplicate inserts when Prefect reruns a day.
4. **Minimal indexes** – composite indexes on `(symbol, timestamp)` plus partial indexes for signal strength.
5. **Auth-lite** – only email addresses today; Supabase auth comes later.

## Critical Constraints

```sql
-- Prevent duplicate bars
ALTER TABLE market_data
  ADD CONSTRAINT market_data_unique UNIQUE (symbol, timestamp);

-- Prevent duplicate signals on rerun
ALTER TABLE signals
  ADD CONSTRAINT signals_idempotent UNIQUE (idempotency_key);

-- Double opt-in tokens
ALTER TABLE email_subscribers
  ADD CONSTRAINT subscribers_confirmation_token UNIQUE (confirmation_token);

-- Data integrity checks
ALTER TABLE market_data
  ADD CONSTRAINT prices_positive CHECK (open > 0 AND high > 0 AND low > 0 AND close > 0 AND volume >= 0);

ALTER TABLE signals
  ADD CONSTRAINT valid_signal CHECK (signal_type IN ('BUY', 'SELL', 'HOLD'));
```

## Key Queries

### Fetch latest bars for indicator calculation

```sql
SELECT timestamp, close 
FROM market_data 
WHERE symbol = 'BTC-USD' 
ORDER BY timestamp DESC 
LIMIT 50;  -- Last 50 bars for RSI-14, EMA-26 warmup
```

### Find strong signals pending notification

```sql
SELECT s.* 
FROM signals s
WHERE s.strength >= 70
  AND s.id NOT IN (
    SELECT signal_id FROM sent_notifications
  );
```

### Get active confirmed subscribers

```sql
SELECT email 
FROM email_subscribers 
WHERE confirmed = true 
  AND unsubscribed = false;
```

### Email engagement metrics (last 7 days)

```sql
SELECT 
  COUNT(*) as total_sent,
  COUNT(DISTINCT email) as unique_recipients
FROM sent_notifications
WHERE sent_at > NOW() - INTERVAL '7 days';
```

## Setup

### Initial setup

**Recommended**: Use the setup scripts for automated initialization:

```bash
# 1. Initialize schema and seed 4 assets
python scripts/apply_db.py

# 2. Backfill ~10 years of historical data
uv run --directory pipe python -m pipe.flows.market_data_backfill --symbols AAPL,BTC-USD --backfill-range 10y

# 3. Verify data loaded
psql $DATABASE_URL -c "SELECT symbol, COUNT(*), MIN(timestamp), MAX(timestamp) FROM market_data GROUP BY symbol;"
```

**Manual setup** (if needed):

```bash
# Create database and run schema
psql $DATABASE_URL -f db/schema.sql

# Seed default assets (BTC-USD, AAPL)
psql $DATABASE_URL -f db/seeds/symbols.sql

# Verify
psql $DATABASE_URL -c "SELECT * FROM symbols;"
```

**See** `README.md` for detailed setup instructions and troubleshooting.

### Local development (Docker)

```bash
# Start PostgreSQL
docker-compose up -d

# Connect
psql postgresql://signals_user:signals_password@localhost:5432/trading_signals

# Apply schema and seeds
\i db/schema.sql
\i db/seeds/symbols.sql
```

## Migrations

Place new migrations in `db/migrations/` with format: `NNN_description.sql`

Example workflow:

```bash
# Create new migration
touch db/migrations/003_add_regime_detection.sql

# Edit migration
vim db/migrations/003_add_regime_detection.sql

# Apply to dev
psql $DEV_DATABASE_URL -f db/migrations/003_add_regime_detection.sql

# Apply to prod (after testing)
psql $DATABASE_URL -f db/migrations/003_add_regime_detection.sql
```

## Future Evolution (Phase 2+)

### When to add

**Regime detection** (when we implement ADX):

```sql
ALTER TABLE indicators 
  ADD COLUMN adx DECIMAL(5, 2),
  ADD COLUMN regime VARCHAR(20) CHECK (regime IN ('trend', 'range', 'uncertain'));
```

**Delivery tracking** (when we add Resend webhooks):

```sql
ALTER TABLE sent_notifications
  ADD COLUMN delivered_at TIMESTAMPTZ,
  ADD COLUMN opened_at TIMESTAMPTZ,
  ADD COLUMN clicked_at TIMESTAMPTZ,
  ADD COLUMN bounced BOOLEAN DEFAULT false;
```

**Auth migration** (when we add Supabase auth):

```sql
-- Migrate to auth.users, keep sent_notifications for history
-- Use RLS policies for user-specific data
```

**Data quality flags** (when we need quality gates):

```sql
ALTER TABLE market_data 
  ADD COLUMN data_quality VARCHAR(20) DEFAULT 'valid'
    CHECK (data_quality IN ('valid', 'gap', 'stale', 'spike'));
```

### Retention Strategy

- **MVP**: Keep all data forever (tiny size: ~35 MB in 6 months)
- **Scale**: After 1M rows, consider TimescaleDB compression for OHLCV >90 days old
- **Archive**: Move `sent_notifications` >1 year old to cold storage

## Performance Targets

| Query | Target | Notes |
|-------|--------|-------|
| Fetch latest 50 bars | <10ms | Indexed on (symbol, timestamp DESC) |
| Insert new signal | <5ms | Simple insert with idempotency check |
| Find strong signals | <20ms | Partial index on strength >= 70 |
| Email engagement metrics | <50ms | 7-day window aggregation |

## Schema Validation

```sql
-- Check for orphaned records
SELECT COUNT(*) FROM market_data 
WHERE symbol NOT IN (SELECT symbol FROM symbols);
-- Should return 0

-- Check for signals without notifications (>24 hours old, strength ≥ 70)
SELECT COUNT(*) FROM signals s
WHERE s.strength >= 70
  AND s.generated_at < NOW() - INTERVAL '24 hours'
  AND NOT EXISTS (
    SELECT 1 FROM sent_notifications WHERE signal_id = s.id
  );
-- Should return 0 (or investigate)

-- Check for unconfirmed subscribers (>24 hours)
SELECT COUNT(*) FROM email_subscribers
WHERE confirmed = false
  AND subscribed_at < NOW() - INTERVAL '24 hours';
-- Manual cleanup if >100
```

## Troubleshooting

### Issue: Duplicate signals

```sql
-- Check for missing idempotency keys
SELECT COUNT(*) FROM signals WHERE idempotency_key IS NULL;

-- Fix: Set idempotency_key format
UPDATE signals 
SET idempotency_key = symbol || ':' || rule_version || ':' || timestamp::text
WHERE idempotency_key IS NULL;
```

### Issue: Emails not sending

```sql
-- Check for unconfirmed subscribers
SELECT COUNT(*) FROM email_subscribers WHERE confirmed = false;

-- Check notification backlog
SELECT COUNT(*) FROM signals s
WHERE strength >= 70 
  AND id NOT IN (SELECT signal_id FROM sent_notifications);
```

### Issue: Slow queries

```sql
-- Check index usage
EXPLAIN ANALYZE 
SELECT * FROM market_data 
WHERE symbol = 'BTC-USD' 
ORDER BY timestamp DESC LIMIT 50;

-- Should use: idx_market_data_symbol_time
```

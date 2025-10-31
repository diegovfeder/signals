# Database Design

## Current State (MVP)

Single PostgreSQL database with 6 core tables optimized for solo dev speed.

### Tables & Daily Volume

| Table | Purpose | Rows/Day | Row Size |
|-------|---------|----------|----------|
| `symbols` | Asset registry (4 assets) | 0 (static) | ~100 bytes |
| `market_data` | 15-min OHLCV bars | ~384 (96 × 4 assets) | ~100 bytes |
| `indicators` | RSI + EMA values | ~384 (1 per bar) | ~80 bytes |
| `signals` | BUY/HOLD signals | ~5-10 max | ~200 bytes |
| `email_subscribers` | Email signups | ~2-5 (growth) | ~150 bytes |
| `sent_notifications` | Email audit log | ~500-1000 | ~120 bytes |

### Size Estimates

**After Initial Backfill (~60 days of 15m bars)**:

- **OHLCV**: ~23K rows × 100 bytes ≈ **2.3 MB**
- **Indicators**: ~23K rows × 80 bytes ≈ **1.8 MB**
- **Total**: ~4 MB

**After 6 Months of Live Data**:

- **OHLCV**: 70K rows × 100 bytes ≈ **7 MB**
- **Indicators**: 70K rows × 80 bytes ≈ **5.6 MB**
- **Signals**: 1.8K rows × 200 bytes ≈ **360 KB**
- **Subscribers**: 500 rows × 150 bytes ≈ **75 KB**
- **Notifications**: 180K rows × 120 bytes ≈ **22 MB**

**Total: ~35 MB** (well within Supabase free tier: 500 MB)

**Note**: Yahoo Finance limits 15m interval data to ~60 days. For longer historical periods, you'd need daily data or a different data source.

## Design Principles

1. **Direct 15-min fetch** - Yahoo Finance provides 15m bars directly; no resampling needed
2. **Double opt-in email** - `confirmation_token` flow prevents spam, improves deliverability
3. **Idempotent signals** - `idempotency_key` prevents duplicates when Prefect jobs rerun
4. **No auth yet** - Email-only subscriptions; migrate to Supabase auth in Phase 2
5. **Minimal indexes** - Only composite indexes for common query patterns

## Critical Constraints

```sql
-- Prevent duplicate bars
UNIQUE(symbol, timestamp) ON market_data

-- Prevent duplicate signals on job reruns
idempotency_key UNIQUE ON signals

-- Double opt-in flow
confirmation_token UNIQUE ON email_subscribers

-- Data integrity
CHECK (open > 0, high > 0, low > 0, close > 0, volume >= 0)
CHECK (signal_type IN ('BUY', 'SELL', 'HOLD'))
CHECK (asset_type IN ('crypto', 'stock', 'etf', 'forex'))
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

# 2. Backfill ~60 days of historical data
# 3. Verify data loaded
psql $DATABASE_URL -c "SELECT symbol, COUNT(*), MIN(timestamp), MAX(timestamp) FROM market_data GROUP BY symbol;"
```

**Manual setup** (if needed):

```bash
# Create database and run schema
psql $DATABASE_URL -f db/schema.sql

# Seed assets (4 MVP symbols)
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

-- Check for signals without notifications (>15 min old, strength ≥ 70)
SELECT COUNT(*) FROM signals s
WHERE s.strength >= 70
  AND s.generated_at < NOW() - INTERVAL '15 minutes'
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

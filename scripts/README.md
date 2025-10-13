# Setup Scripts

Utility scripts for database initialization and historical data seeding.

## Quick Start

```bash
# 1. Setup database schema and seed symbols
python scripts/setup_db.py

# 2. Backfill historical market data
python scripts/seed_historical_data.py

# 3. Verify data loaded
psql $DATABASE_URL -c "SELECT symbol, COUNT(*), MIN(timestamp), MAX(timestamp) FROM market_data GROUP BY symbol;"
```

## Database Setup

### `setup_db.py`

Initializes PostgreSQL database with schema and seeds the 4 MVP assets.

**What it does:**
1. Connects to database (from `$DATABASE_URL` env var)
2. Runs `db/schema.sql` to create tables
3. Runs `db/seeds/symbols.sql` to insert 4 assets (BTC-USD, AAPL, IVV, BRL=X)
4. Verifies setup by querying `symbols` table

**Usage:**
```bash
# Local (Docker)
export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"
python scripts/setup_db.py

# Production (Supabase)
export DATABASE_URL="postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres"
python scripts/setup_db.py
```

**Expected output:**
```
============================================================
Trading Signals - Database Setup
============================================================

Connecting to database...
✓ Connected successfully

1. Creating database schema...
Running schema.sql...
✓ Completed schema.sql

2. Seeding initial data...
Running symbols.sql...
✓ Completed symbols.sql

3. Verifying setup...
✓ Found 4 symbols:
  - BTC-USD: Bitcoin
  - AAPL: Apple Inc.
  - IVV: iShares Core S&P 500 ETF
  - BRL=X: Brazilian Real / US Dollar

============================================================
✓ Database setup complete!
============================================================
```

## Historical Data Seeding

### `seed_historical_data.py`

Backfills historical OHLCV data from Yahoo Finance for all MVP assets.

**What it does:**
1. Fetches maximum available 15-minute bars (~60 days) from Yahoo Finance
2. Falls back to hourly data if 15m not available (some forex pairs)
3. Inserts into `market_data` table with duplicate prevention
4. Continues processing remaining symbols if one fails

**Limitations:**
- Yahoo Finance limits 15m interval data to ~60 days
- Forex pairs (like BRL=X) may have less data available
- Some assets may only have hourly granularity

**Usage:**
```bash
export DATABASE_URL="postgresql://..."
python scripts/seed_historical_data.py
```

**Expected output:**
```
============================================================
Trading Signals - Seed Historical Data
============================================================
✓ Connected to database

Processing BTC-USD...
------------------------------------------------------------
Fetching 15m data for BTC-USD...
✓ Fetched 3840 candles (60 days: 2025-08-15 to 2025-10-13)
Inserting data into database...
✓ Inserted 3840 records
✓ Completed BTC-USD

Processing AAPL...
------------------------------------------------------------
Fetching 15m data for AAPL...
✓ Fetched 1560 candles (60 days: 2025-08-15 to 2025-10-13)
Inserting data into database...
✓ Inserted 1560 records
✓ Completed AAPL

[... IVV and BRL=X ...]

============================================================
✓ Historical data seeding complete!
============================================================
```

**Note on data volume:**
- BTC-USD: 24/7 market = ~96 bars/day × 60 days = ~5,760 bars
- AAPL: Market hours only = ~26 bars/day × 60 days = ~1,560 bars
- IVV: Same as AAPL
- BRL=X: May vary depending on trading hours

## Verification

### Check data loaded correctly

```bash
# Count rows per symbol
psql $DATABASE_URL -c "
SELECT
  symbol,
  COUNT(*) as bars,
  MIN(timestamp) as oldest,
  MAX(timestamp) as newest,
  MAX(timestamp) - MIN(timestamp) as range
FROM market_data
GROUP BY symbol
ORDER BY symbol;
"
```

Expected output:
```
 symbol  | bars | oldest              | newest              | range
---------+------+---------------------+---------------------+---------
 AAPL    | 1560 | 2025-08-15 09:30:00 | 2025-10-13 16:00:00 | 59 days
 BRL=X   | 3200 | 2025-08-15 00:00:00 | 2025-10-13 23:45:00 | 60 days
 BTC-USD | 5760 | 2025-08-15 00:00:00 | 2025-10-13 23:45:00 | 60 days
 IVV     | 1560 | 2025-08-15 09:30:00 | 2025-10-13 16:00:00 | 59 days
```

### Verify indicators can be calculated

```sql
-- Ensure enough data for RSI-14 (needs 15 bars) and EMA-26 (needs 27 bars)
SELECT symbol, COUNT(*)
FROM market_data
GROUP BY symbol
HAVING COUNT(*) < 27;
-- Should return 0 rows
```

## Troubleshooting

### Database connection error

```bash
# Check DATABASE_URL format
echo $DATABASE_URL
# Should be: postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL -c "SELECT 1;"
```

### "No data returned for symbol"

Some assets may not have 15m data available. The script will:
1. Try 15m interval first
2. Fall back to 1h interval
3. Skip symbol and continue if both fail

Check output for warnings:
```
⚠ No 15m data available for BRL=X, trying 1h interval...
```

### "Table does not exist"

Run `setup_db.py` first to create schema:
```bash
python scripts/setup_db.py
```

### Duplicate key errors

The script uses `ON CONFLICT DO NOTHING`, so re-running is safe. If you see errors, check:
```sql
-- Verify UNIQUE constraint exists
\d market_data
-- Should show: UNIQUE (symbol, timestamp)
```

## Local Development (Docker)

### Complete setup from scratch

```bash
# 1. Start PostgreSQL
docker-compose up -d

# Wait for postgres to be ready
sleep 5

# 2. Set connection string
export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"

# 3. Run setup
python scripts/setup_db.py

# 4. Seed data
python scripts/seed_historical_data.py

# 5. Verify
psql $DATABASE_URL -c "SELECT symbol, COUNT(*) FROM market_data GROUP BY symbol;"
```

### Reset database

```bash
# Drop all tables and start fresh
psql $DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run setup
python scripts/setup_db.py
python scripts/seed_historical_data.py
```

## Production (Supabase)

### First-time setup

```bash
# 1. Create Supabase project at https://supabase.com

# 2. Get connection string from Settings → Database → Connection String (URI)
export DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres"

# 3. Run setup
python scripts/setup_db.py
python scripts/seed_historical_data.py

# 4. Verify in Supabase Table Editor
```

### Update historical data

```bash
# Re-run seeding to update with latest bars (safe, uses ON CONFLICT DO NOTHING)
python scripts/seed_historical_data.py
```

## Next Steps

After seeding historical data:

1. **Test indicators**: See `data/README.md` for RSI/EMA calculation examples
2. **Run Prefect flow**: See `pipe/README.md` to test signal generation locally
3. **Start API**: See `backend/README.md` to serve signals via FastAPI
4. **Build frontend**: See root `README.md` for full stack setup

## Dependencies

Required Python packages:
```bash
pip install yfinance psycopg2-binary
```

Or install from project requirements:
```bash
pip install -r requirements.txt  # If you have a root requirements.txt
```

## Data Retention

**MVP**: Keep all data forever (60 days × 4 assets ≈ 35 MB total)

**Phase 2**: Consider archival strategy after 6+ months:
- Compress OHLCV >90 days old (TimescaleDB)
- Aggregate 15m → 1h for old data
- Keep raw 15m for recent 90 days only

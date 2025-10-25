# Pipe Scripts

Testing and data utilities for the Trading Signals pipeline.

## Prerequisites

```bash
# Install pipe dependencies
cd pipe
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Testing Utilities

Manual testing scripts that bypass Prefect flows for local development and debugging.

### testing/seed_mock_data.py

Generate mock OHLCV data for testing without Yahoo Finance API.

**What it does:**
- Creates 50 bars per symbol (BTC-USD, AAPL, IVV, BRL=X)
- Generates realistic random walk price data
- Inserts directly into `market_data` table using psycopg3
- Useful when Yahoo Finance API is slow/down

**Usage:**

```bash
export DATABASE_URL="postgresql://..."
python pipe/scripts/testing/seed_mock_data.py
```

**Expected output:**

```
Seeding MVP database with mock OHLCV data...

Generating data for BTC-USD...
✓ BTC-USD: 50 bars generated
Generating data for AAPL...
✓ AAPL: 50 bars generated
Generating data for IVV...
✓ IVV: 50 bars generated
Generating data for BRL=X...
✓ BRL=X: 50 bars generated

Total market_data rows inserted: 200

Market data counts:
  AAPL: 50 bars
  BRL=X: 50 bars
  BTC-USD: 50 bars
  IVV: 50 bars

✓ Database seeded successfully!
Next: Run calculate indicators and generate signals
```

### testing/manual_signal_gen.py

Calculate indicators and generate signals from existing market_data.

**What it does:**
- Reads OHLCV data from database
- Calculates RSI-14, EMA-12, EMA-26 for all bars
- Generates signal for latest bar using MVP rules
- Upserts into `indicators` and `signals` tables
- Shows strong signals (strength >= 70)

**Usage:**

```bash
export DATABASE_URL="postgresql://..."
python pipe/scripts/testing/manual_signal_gen.py
```

**Expected output:**

```
Calculating indicators and generating signals...

BTC-USD:
  ✓ Indicators: 50 rows
  ✓ Signal: BUY (strength: 75.0/100)
    ⚠️  STRONG SIGNAL: BTC-USD BUY @ $45234.50
AAPL:
  ✓ Indicators: 50 rows
  ✓ Signal: HOLD (strength: 42.0/100)
IVV:
  ✓ Indicators: 50 rows
  ✓ Signal: HOLD (strength: 38.0/100)
BRL=X:
  ✓ Indicators: 50 rows
  ✓ Signal: BUY (strength: 72.0/100)
    ⚠️  STRONG SIGNAL: BRL=X BUY @ $5.12

✓ All symbols processed!

Database summary:
  Indicators: 200 rows
  Signals: 4 rows
```

**When to use these:**
- 🐌 Yahoo Finance API is down/slow
- 🧪 Testing indicator calculations
- 🔍 Debugging signal generation logic
- 💻 Local development without external API calls
- ⚡ Fast iteration on signal rules

**Note:** Production pipeline uses `pipe/flows/signal_generation.py` with Prefect orchestration.

## Data Utilities

### data/fetch_fixture_data.py

Generate small Yahoo Finance OHLCV fixtures for offline tests (15m bars by default).

**Usage:**

```bash
python pipe/scripts/data/fetch_fixture_data.py \
  --symbols AAPL BTC-USD \
  --interval 15m \
  --period 5d \
  --rows 120 \
  --out pipe/tests/fixtures
```

**Output:**
- CSV files under `pipe/tests/fixtures/`
- Columns: `timestamp, open, high, low, close, volume`
- Timestamps are UTC ISO-8601 with `Z`

## Complete Testing Workflow

```bash
# 1. Start local database
docker-compose up -d

# 2. Setup schema
python backend/scripts/setup_db.py

# 3. Generate mock data
python pipe/scripts/testing/seed_mock_data.py

# 4. Calculate indicators and signals
python pipe/scripts/testing/manual_signal_gen.py

# 5. Verify in database
psql $DATABASE_URL -c "SELECT * FROM signals ORDER BY strength DESC;"

# 6. Test API
cd backend
uvicorn api.main:app --reload

# 7. Open API docs and test endpoints
open http://localhost:8000/api/docs
```

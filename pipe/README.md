# Prefect Data Pipeline

Simple orchestration for fetching market data, calculating indicators, generating signals, and sending emails.

## Quick Overview

**One flow, four tasks, runs every 15 minutes:**

```bash
generate_signals_flow():
  ├─ Task 1: fetch_market_data()     # Yahoo Finance → market_data table
  ├─ Task 2: calculate_indicators()  # RSI + EMA → indicators table
  ├─ Task 3: generate_signals()      # Rules → signals table
  └─ Task 4: send_notifications()    # Emails → sent_notifications table
```

**Why one flow?**

- ✅ Simpler to understand and debug
- ✅ No flow dependencies to manage
- ✅ All logic in one file (`flows/signal_generation.py`)
- ✅ Easy to test locally before deploying
- ⏭️ Can split later if needed (Prefect costs by task runs, not flows)

## Files

```bash
pipe/
├── flows/
│   └── signal_generation.py      # Single flow with 4 tasks
├── tasks/
│   ├── data_fetching.py          # Yahoo Finance helpers
│   ├── data_validation.py        # Quality checks (Phase 2)
│   └── email_sending.py          # Resend API helpers
├── schedules.py                   # Deploy flow to Prefect Cloud
├── pyproject.toml                 # Dependencies
└── README.md                      # This file
```

## Quick Start

### 1. Install dependencies

```bash
cd pipe
uv sync
```

### 2. Set environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/trading_signals
RESEND_API_KEY=re_...
```

### 3. Test locally

```bash
# Run the flow once (from project root)
uv run --directory pipe python -m pipe.flows.signal_generation

# Check what happened
psql $DATABASE_URL -c "SELECT * FROM signals ORDER BY timestamp DESC LIMIT 5;"
```

### 4. Deploy to Prefect Cloud

```bash
# Login (first time only)
prefect cloud login

# Deploy with 15-minute schedule (from project root)
uv run --directory pipe python schedules.py
```

## Flow Structure

### `flows/signal_generation.py`

```python
from prefect import flow, task
import yfinance as yf
from sqlalchemy import create_engine
import os

SYMBOLS = ['BTC-USD', 'AAPL', 'IVV', 'BRL=X']

@task(name="fetch-market-data", retries=3, retry_delay_seconds=60)
def fetch_market_data(symbol: str):
    """Fetch 15m bar from Yahoo Finance and store in market_data table."""
    # 1. Fetch from Yahoo Finance
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="1d", interval="15m")
    
    # 2. Store in database (INSERT ... ON CONFLICT for idempotency)
    engine = create_engine(os.getenv("DATABASE_URL"))
    df.to_sql("market_data", engine, if_exists="append", index=False)
    
    return len(df)

@task(name="calculate-indicators")
def calculate_indicators(symbol: str):
    """Fetch last 50 bars, calculate RSI + EMA, store in indicators table."""
    # 1. Fetch bars
    engine = create_engine(os.getenv("DATABASE_URL"))
    df = pd.read_sql(
        f"SELECT * FROM market_data WHERE symbol='{symbol}' ORDER BY timestamp DESC LIMIT 50",
        engine
    )
    
    # 2. Calculate RSI-14, EMA-12, EMA-26
    df['rsi'] = calculate_rsi(df['close'], period=14)
    df['ema_12'] = df['close'].ewm(span=12).mean()
    df['ema_26'] = df['close'].ewm(span=26).mean()
    
    # 3. Store latest indicator values
    latest = df.iloc[-1]
    # INSERT into indicators table...

@task(name="generate-signals")
def generate_signals(symbol: str):
    """Apply RSI/EMA rules, generate signal, store in signals table."""
    # 1. Fetch latest indicators
    # 2. Apply rules (RSI < 30 = BUY, EMA cross = BUY)
    # 3. Calculate strength (0-100)
    # 4. Store signal with idempotency_key
    pass

@task(name="send-notifications")
def send_notifications():
    """Send emails for strong signals (>= 70) to confirmed subscribers."""
    # 1. Fetch signals WHERE strength >= 70 AND not yet notified
    # 2. Fetch confirmed subscribers
    # 3. Send via Resend API
    # 4. Record in sent_notifications table
    pass

@flow(name="generate-signals", log_prints=True)
def generate_signals_flow():
    """Main flow: runs every 15 minutes."""
    print("🚀 Starting signal generation flow...")
    
    for symbol in SYMBOLS:
        # Fetch → Calculate → Generate for each symbol
        bars_count = fetch_market_data(symbol)
        print(f"✅ {symbol}: Fetched {bars_count} bars")
        
        calculate_indicators(symbol)
        print(f"✅ {symbol}: Indicators calculated")
        
        generate_signals(symbol)
        print(f"✅ {symbol}: Signal generated")
    
    # Send notifications (once for all symbols)
    send_notifications()
    print("📧 Notifications sent!")

if __name__ == "__main__":
    # Test locally
    generate_signals_flow()
```

## Schedule

### `schedules.py`

```python
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule
from flows.signal_generation import generate_signals_flow

# Deploy with 15-minute cron schedule
deployment = Deployment.build_from_flow(
    flow=generate_signals_flow,
    name="production",
    schedule=CronSchedule(cron="0,15,30,45 * * * *"),  # Every 15 min
    work_queue_name="default"
)

deployment.apply()
print("✅ Deployed to Prefect Cloud!")
```

Run: `uv run --directory pipe python schedules.py`

## Development Tips

### Test individual tasks

```python
# Test just the fetch task
from flows.signal_generation import fetch_market_data

bars = fetch_market_data("BTC-USD")
print(f"Fetched {bars} bars")
```

### Run flow with specific symbols

```python
from flows.signal_generation import generate_signals_flow

# Override SYMBOLS temporarily
import flows.signal_generation as sg
sg.SYMBOLS = ['BTC-USD']  # Test with just BTC
generate_signals_flow()
```

### Check Prefect logs

```bash
# Local server for testing
prefect server start

# View at http://localhost:4200
```

### Troubleshooting

**No data fetched:**

```sql
-- Check if bars are being stored
SELECT symbol, COUNT(*), MAX(timestamp) 
FROM market_data 
GROUP BY symbol;
```

**Indicators not calculating:**

```python
# Add debug prints in calculate_indicators task
print(f"Fetched {len(df)} bars for {symbol}")
print(f"Latest RSI: {df['rsi'].iloc[-1]}")
```

**Flow not running on schedule:**

- Check Prefect Cloud UI → Deployments → "production"
- Verify cron schedule: `0,15,30,45 * * * *`
- Check work queue is running

## Phase 2: Split into Multiple Flows

When your pipeline gets more complex, you can split into separate flows:

```python
# Option 1: Keep as one flow (current - simple!)

# Option 2: Split into 4 flows (better observability)
@flow
def ingest_flow():
    for symbol in SYMBOLS:
        fetch_market_data(symbol)

@flow
def calculate_flow():
    for symbol in SYMBOLS:
        calculate_indicators(symbol)

@flow
def generate_flow():
    for symbol in SYMBOLS:
        generate_signals(symbol)

@flow
def notify_flow():
    send_notifications()
```

**When to split:**

- Different schedules needed (e.g., ingest every 5min, notify every 30min)
- Want to run tasks in parallel
- Need better failure isolation

**For now:** Stick with one flow! It's perfect for learning and debugging.

## Helper Functions

You'll need to implement:

**RSI Calculation** (`data/indicators/rsi.py`):

```python
def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
    delta = prices.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
```

**Signal Rules** (`data/signals/signal_generator.py`):

```python
def generate_signal(rsi: float, ema_12: float, ema_26: float) -> dict:
    signal_type = "HOLD"
    strength = 0
    reasoning = []
    
    # RSI oversold
    if rsi < 30:
        signal_type = "BUY"
        strength = 100 - rsi  # Lower RSI = stronger signal
        reasoning.append(f"RSI oversold ({rsi:.1f})")
    
    # EMA bullish cross
    if ema_12 > ema_26:
        signal_type = "BUY"
        strength = max(strength, 70)
        reasoning.append("EMA-12 above EMA-26 (bullish)")
    
    return {
        "signal_type": signal_type,
        "strength": int(strength),
        "reasoning": reasoning
    }
```

See `docs/DATA-SCIENCE.md` for full indicator explanations.

## Next Steps

1. ✅ Set up database (see `db/README.md`)
2. ✅ Implement `fetch_market_data()` task
3. ✅ Implement `calculate_indicators()` task
4. ✅ Implement `generate_signals()` task
5. ✅ Implement `send_notifications()` task
6. ✅ Test locally with `python -m pipe.flows.signal_generation`
7. ✅ Deploy to Prefect Cloud with `python schedules.py`

**Keep it simple, get it working, iterate!** 🚀

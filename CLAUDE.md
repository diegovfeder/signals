# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trading Signals MVP - An automated system that monitors multiple asset classes (crypto, stocks, ETFs, forex), calculates technical indicators (RSI + EMA), generates trading signals, and sends email notifications to subscribers.

**Small dev team project** designed for incremental learning and building. Start small, add complexity as you understand each piece.

## Architecture

This is a **multi-component system** with 4 independent parts:

```bash
Yahoo Finance API → Prefect Pipeline → Supabase → FastAPI → Next.js → User
```

**Key principle**: Each component can be developed and tested independently.

### Component Responsibilities

1. **Prefect Pipeline** (`pipe/`): Fetch data, calculate indicators, generate signals, send emails
   - Includes `pipe/lib/` - Indicator calculations (RSI, EMA) and signal generation logic
2. **FastAPI Backend** (`backend/`): REST API serving signals and market data to frontend
3. **Next.js Frontend** (`frontend/`): Public dashboard displaying signals and email signup
4. **Database** (`db/`): Supabase PostgreSQL schema with 6 core tables

**Data flow**: Pipeline writes → Database stores → API reads → Frontend displays

## Development Commands

**Package Manager**: This project uses [uv](https://docs.astral.sh/uv/) for fast, reliable Python dependency management. Install it globally:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Database Setup

- **Option A: Local (Docker) - Recommended for Development**

```bash
# Start PostgreSQL with auto-initialized schema
docker-compose up -d

# Connection string (already configured in docker-compose.yml)
export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"

# Schema and seeds are auto-loaded on first start
# See docker-compose.yml volumes section
```

- **Option B: Production (Supabase)**

```bash
# 1. Create Supabase project at supabase.com
# 2. Copy connection string

# 3. Run schema (single consolidated file, no migrations)
psql $DATABASE_URL -f db/schema.sql

# 4. Seed initial data
psql $DATABASE_URL -f db/seeds/symbols.sql
```

### Backend (FastAPI)

```bash
cd backend

# Install dependencies with uv (faster than pip)
uv sync

# Create .env from template
cp .env.example .env
# Edit .env with your DATABASE_URL and RESEND_API_KEY

# Run development server (uv creates virtual environment automatically)
uv run uvicorn api.main:app --reload --port 8000

# API docs available at: http://localhost:8000/api/docs
# Health check: http://localhost:8000/health
```

**Backend Requirements** (Python 3.11+):

- FastAPI + Uvicorn
- SQLAlchemy 2.0+
- `psycopg[binary,pool]` (Python 3.13 compatible, replaces asyncpg/psycopg2-binary)
- Pydantic 2.4+
- Resend (email service)

### Frontend (Next.js)

```bash
cd frontend
npm install   # or bun install

# Create .env.local from template
cp .env.example .env.local
# Edit with NEXT_PUBLIC_API_URL=http://localhost:8000

# Development
npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Production build
npm run start        # Start production server
npm run lint         # ESLint check
npm run type-check   # TypeScript check
```

**Frontend Stack**:

- Next.js 15 (App Router)
- React 19
- TypeScript 5.6
- TailwindCSS 4.0
- Chart.js + react-chartjs-2 (for signal visualization)

### Prefect Pipeline

```bash
# Setup (one-time) - from project root
cd pipe
uv sync  # Install all dependencies using uv
cd ..  # Back to project root

# Create .env from template
cp pipe/.env.example pipe/.env
# Edit with DATABASE_URL and RESEND_API_KEY

# IMPORTANT: Always run flows from project root, not from pipe/ directory

# Test single unified flow locally
uv run --directory pipe python -m pipe.flows.signal_generation --symbols BTC-USD,AAPL

# Deploy to Prefect Cloud (runs daily at 10 PM UTC)
prefect cloud login
uv run --directory pipe python -m pipe.deployments.register --work-pool default-prefect-managed-wp

# View flow runs
prefect flow-run ls
```

**Important**: MVP uses a **single unified flow** (`signal_generation.py`) that handles all steps:

1. Fetch OHLCV from Yahoo Finance
2. Calculate RSI + EMA indicators
3. Generate BUY/HOLD signals
4. Store in database
5. Notify if strength >= 70

This replaces the separate flows mentioned in older docs (market_data_ingestion, indicator_calculation, notification_sender).

### Data Science (Indicators)

```bash
# The lib/ folder contains all indicator logic
# Test indicators in isolation (run from project root):

uv run --directory pipe python -c "from pipe.lib.indicators.rsi import calculate_rsi; print('RSI module loaded')"
uv run --directory pipe python -c "from pipe.lib.signals.strategies import get_strategy; print('Signal strategies loaded')"
```

## Database Schema

**6 Core Tables** (see `db/schema.sql`):

1. **symbols** - Assets we track: BTC-USD (crypto), AAPL (stock)
2. **market_data** - Raw OHLCV from Yahoo Finance for all assets
3. **indicators** - Calculated RSI, MACD (note: docs mention EMA, schema has MACD - use RSI+EMA for MVP)
4. **signals** - Generated BUY/HOLD signals with strength scores per asset
5. **email_subscribers** - Users subscribed to notifications
6. **sent_notifications** - Audit log of emails sent

**Key indexes**: All tables have `(symbol, timestamp DESC)` indexes for fast time-series queries.

## Code Structure Patterns

### Prefect Flows (`pipe/`)

```bash
pipe/
├── flows/
│   └── signal_generation.py    # Single unified flow (MVP approach)
│       # Contains all tasks inline: fetch → calculate → generate → store → notify
│   # Historical flows (not used in MVP):
│   ├── market_data_ingestion.py
│   ├── indicator_calculation.py
│   └── notification_sender.py
├── tasks/              # Reusable tasks (for future refactoring)
│   ├── data_fetching.py
│   ├── data_validation.py
│   └── email_sending.py
└── schedules.py        # Prefect Cloud deployment config (15-min cron)
```

**MVP Pattern**: Single `signal_generation_flow` with all tasks defined inline for simplicity. This can be refactored into separate flows in Phase 2 if needed.

### Data Science (`pipe/lib/`)

```bash
pipe/
├── lib/                      # Indicator calculations and signal logic
│   ├── indicators/          # Technical indicator calculations
│   │   ├── rsi.py          # RSI (14-period)
│   │   ├── ema.py          # EMA (12, 26 period)
│   │   └── macd.py         # MACD (not in MVP, use for Phase 2)
│   ├── signals/            # Signal generation logic
│   │   ├── strategies/     # Strategy implementations (crypto_momentum, stock_mean_reversion)
│   │   ├── signal_generator.py  # Main signal rules
│   │   └── signal_scorer.py     # Strength scoring (0-100)
│   ├── api/                # Data source integrations
│   │   ├── alpha_vantage.py
│   │   └── yahoo.py
│   └── utils/              # Shared utilities (calculate_ema helper)
├── flows/                   # Prefect flow definitions
│   ├── signal_generation.py      # Main flow
│   ├── historical_backfill.py    # Backfill historical data
│   └── signal_replay.py          # Replay signals for backtesting
└── tasks/                   # Reusable Prefect tasks
    ├── market_data.py       # Fetch and store OHLCV
    ├── indicators.py        # Calculate and store indicators
    └── signals.py           # Generate and store signals
```

**Pattern**: Each indicator is a pure function: `calculate_indicator(df) -> df_with_indicator`

### FastAPI Backend (`backend/`)

```bash
backend/
├── api/
│   ├── main.py           # FastAPI app + CORS + health check endpoint
│   ├── routers/          # API endpoints (✅ All implemented)
│   │   ├── signals.py    # GET /api/signals/, /api/signals/{symbol}, /api/signals/{symbol}/history
│   │   ├── market_data.py # GET /api/market-data/{symbol}/ohlcv, /indicators
│   │   └── subscribe.py  # POST /api/subscribe/, POST /api/subscribe/unsubscribe/{token}
│   ├── models.py         # SQLAlchemy ORM models (Symbol, MarketData, Indicator, Signal, EmailSubscriber, etc.)
│   ├── schemas.py        # Pydantic response schemas
│   ├── database.py       # Database connection and session management
│   ├── config.py         # Environment config (DATABASE_URL, RESEND_API_KEY, etc.)
│   └── .env.example      # Environment template
├── requirements.txt
└── vercel.json           # Vercel deployment config
```

**Pattern**: All endpoints are **fully implemented**. Each router file handles one resource domain. SQLAlchemy models map to database tables, Pydantic schemas validate responses.

**Implementation Status** (See `docs/IMPLEMENTATION_SUMMARY.md` for details):

- ✅ All read endpoints (signals, market data)
- ✅ Subscribe/unsubscribe (stores to DB, tokens generated)
- ✅ Health check with DB connection test
- 🔜 Email sending via Resend (Phase 2)

### Next.js Frontend (`frontend/`)

```bash
frontend/
├── src/
│   ├── app/                    # App Router pages
│   │   ├── page.tsx           # Landing page
│   │   └── dashboard/         # Signal dashboard
│   │       └── page.tsx       # Uses 'use client' + useSignals() hook
│   ├── components/
│   │   ├── landing/           # Landing page sections
│   │   │   ├── Hero.tsx
│   │   │   ├── LiveSignals.tsx
│   │   │   └── EmailSignup.tsx
│   │   └── dashboard/         # Dashboard components
│   │       └── SignalCard.tsx # Card component for each symbol
│   └── lib/
│       └── hooks/
│           └── useSignals.ts  # Client-side data fetching hook
├── package.json
├── next.config.ts
└── .env.example               # NEXT_PUBLIC_API_URL template
```

**Pattern**: The dashboard uses **Client Components** with a custom `useSignals()` hook for data fetching. This replaces the Server Component pattern mentioned in older docs.

```typescript
// Example from dashboard/page.tsx
'use client'
import { useSignals } from '@/lib/hooks/useSignals'

export default function Dashboard() {
  const { signals, loading, error } = useSignals()
  // ...
}
```

## Key Integration Points

### 1. Pipeline → Database

The unified flow writes directly to PostgreSQL using psycopg2:

```python
# In pipe/flows/signal_generation.py
import psycopg2
from psycopg2.extras import execute_values

def _get_db_conn():
    db_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(db_url)

# Upsert market data
@task(name="upsert-market-data")
def upsert_market_data(df: pd.DataFrame):
    query = (
        "INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume) "
        "VALUES %s ON CONFLICT (symbol, timestamp) DO NOTHING"
    )
    with _get_db_conn() as conn, conn.cursor() as cur:
        execute_values(cur, query, rows)
```

### 2. Database → FastAPI

Backend reads from PostgreSQL using SQLAlchemy 2.0:

```python
# In backend/api/routers/signals.py
from sqlalchemy import select, desc
from api.database import get_db
from api.models import Signal

def get_signals(db: Session = Depends(get_db)):
    query = select(Signal).order_by(desc(Signal.timestamp)).limit(10)
    signals = db.execute(query).scalars().all()
    return {"signals": [SignalResponse.from_orm(s) for s in signals]}
```

All endpoints are implemented:

- `GET /api/signals/` - List all signals (filterable)
- `GET /api/signals/{symbol}` - Latest signal for symbol
- `GET /api/signals/{symbol}/history` - Historical signals
- `GET /api/market-data/{symbol}/ohlcv` - OHLCV bars
- `GET /api/market-data/{symbol}/indicators` - Calculated indicators

### 3. FastAPI → Next.js

Frontend fetches via custom React hook (Client Component):

```typescript
// In frontend/src/lib/hooks/useSignals.ts
export function useSignals() {
  const [signals, setSignals] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/signals`)
      .then(r => r.json())
      .then(data => setSignals(data.signals))
      .catch(setError)
      .finally(() => setLoading(false))
  }, [])

  return { signals, loading, error }
}

// In frontend/src/app/dashboard/page.tsx
'use client'
const { signals, loading, error } = useSignals()
```

### 4. Resend Email Integration

**Status**: Phase 2 (not yet implemented in MVP)

The pipeline currently logs strong signals instead of sending emails:

```python
# In pipe/flows/signal_generation.py
@task(name="notify-if-strong")
def notify_if_strong(result: Dict) -> None:
    if result["strength"] >= 60.0:
        print(f"[notify] Strong signal {result['symbol']} {result['signal_type']} {result['strength']}/100")
        # TODO Phase 2: Send email via Resend
```

Email sending will be added in Phase 2 with:

- Welcome emails on subscription
- Confirmation emails (double opt-in)
- Signal notification emails

## MVP Scope & Simplifications

**What's IN** (build this first):

- 2 assets: BTC-USD (crypto), AAPL (stock)
- 2 indicators: RSI + EMA (MACD fields in schema but NULL for MVP)
- Asset-agnostic approach: Same indicator logic for all asset types
- 24/7 operation: Ignore market hours (even for stocks/ETFs that close on weekends)
- 1 unified Prefect flow: `signal_generation.py` with all tasks inline
- Fetch 15m data directly from Yahoo Finance (no resampling)
- Logging notifications (email sending in Phase 2)

**What's OUT** (Phase 2):

- More assets per category
- Asset-specific strategies (different indicators per asset type)
- Market hours handling (stocks/ETFs closed detection)
- MACD, Bollinger Bands, or other indicators
- User authentication
- 5-minute to 15-minute resampling
- Real-time WebSocket updates

**Schema Note**: The `indicators` table includes both EMA fields (`ema_12`, `ema_26`) and MACD fields (`macd`, `macd_signal`, `macd_histogram`). MVP uses RSI+EMA only; MACD fields are NULL and available for Phase 2.

## Important Notes

### Environment Variables Required

**Backend**:

- `DATABASE_URL` - Supabase connection string
- `RESEND_API_KEY` - For email sending
- `POSTHOG_API_KEY` - For analytics (optional)

**Frontend**:

- `NEXT_PUBLIC_API_URL` - Backend API URL (<http://localhost:8000> locally)
- `NEXT_PUBLIC_POSTHOG_KEY` - For analytics (optional)

**Pipeline**:

- `DATABASE_URL` - Same as backend
- `RESEND_API_KEY` - For notifications

### Testing Strategy

**Setup**: Project has `pytest.ini` configured at root. Each domain has its own tests.

```bash
# Run pipe tests
cd pipe
pytest tests/ -v

# Run backend tests
cd backend
pytest tests/ -v

# Run with coverage
cd pipe
pytest tests/ --cov=data --cov=flows
```

**Test Structure**:

```bash
pipe/tests/
├── README.md          # Testing guide
├── test_indicators.py # Indicator calculation tests
└── test_signals.py    # Signal generation tests

backend/tests/
└── (to be added)      # API endpoint tests
```

**Example unit test**:

```python
# pipe/tests/test_indicators.py
import pandas as pd
from data.indicators.rsi import calculate_rsi

def test_rsi_calculation():
    df = pd.DataFrame({'close': [100, 102, 101, 103, 105, 104, 106]})
    rsi = calculate_rsi(df, period=6)
    assert rsi.iloc[-1] >= 0 and rsi.iloc[-1] <= 100
```

**Integration tests**: Mark with `@pytest.mark.integration` for tests that hit Yahoo Finance API or database.

### Common Gotchas

1. **Timezones**: Always use UTC for timestamps. Supabase stores TIMESTAMPTZ, but Python datetime must be timezone-aware.

2. **Yahoo Finance rate limits**: yfinance is free but can be flaky. Add retry logic (Prefect handles this).

3. **Signal duplicates**: Use `UNIQUE(symbol, timestamp)` constraint in signals table to prevent dupes.

4. **Email deliverability**: Must configure DKIM/SPF/DMARC in Resend for production.

5. **Prefect local vs cloud**: `prefect.serve()` runs locally. `prefect deploy` sends to Prefect Cloud.

## Working with Indicators

Each indicator follows this pattern:

```python
# pipe/lib/indicators/rsi.py
import pandas as pd

def calculate_rsi(df: pd.DataFrame, period: int = 14, price_column: str = 'close') -> pd.Series:
    """
    Calculate RSI (Relative Strength Index)

    Args:
        df: DataFrame with price column
        period: Lookback period (default 14)
        price_column: Name of price column (default 'close')

    Returns:
        Series of RSI values (0-100)
    """
    delta = df[price_column].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

**To add a new indicator**:

1. Create `pipe/lib/indicators/new_indicator.py` with `calculate_new_indicator()` function
2. Import in `pipe/tasks/indicators.py` and add to `_build_indicator_frame()`
3. Add column to `indicators` table in `db/schema.sql`
4. Update `pipe/lib/signals/strategies/` to use it in signal generation

## Working with Signals

Signal generation logic uses strategy pattern in `pipe/lib/signals/strategies/`:

```python
def generate_signal(df: pd.DataFrame) -> dict:
    """
    Generate BUY/HOLD signal based on indicators

    Returns:
        {
            'signal': 'BUY' or 'HOLD',
            'strength': 0-100,
            'reasoning': ['RSI oversold', 'EMA crossover'],
            'price': current_price
        }
    """
    latest = df.iloc[-1]

    if latest['rsi'] < 30:
        return {'signal': 'BUY', 'strength': 85, ...}

    # ... more rules
```

**Signal strength threshold**: Only email if `strength >= 70`

## Deployment

### Overview

- **Frontend**: Vercel (Next.js)
- **Backend**: Vercel (FastAPI serverless)
- **Pipeline**: Prefect Cloud (scheduled flows)
- **Database**: Supabase (managed PostgreSQL)

All components deploy independently from repo root.

### Database Setup (Supabase)

1. **Create Supabase project** at [supabase.com](https://supabase.com)
2. **Run schema**:
   ```bash
   # Get connection string from Supabase Dashboard → Settings → Database
   psql "postgresql://postgres.[project]:[password]@[host]:5432/postgres" -f db/schema.sql
   ```
3. **Get connection string** for deployments:
   - Go to: Dashboard → Project Settings → Database
   - Copy "Connection string" under **Connection pooling**
   - Select **Session mode** (port 6543)
   - Format: `postgresql://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres`

### Backend Deployment (Vercel)

```bash
cd backend
vercel deploy --prod
```

**Environment variables to set in Vercel dashboard:**

```bash
DATABASE_URL=postgresql+psycopg://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
RESEND_API_KEY=re_xxxxxxxxxxxxx
ENVIRONMENT=production
CORS_ORIGINS=["https://your-frontend.vercel.app"]
```

**Note:** Add `+psycopg` to Supabase URL for SQLAlchemy compatibility.

### Frontend Deployment (Vercel)

```bash
cd frontend
vercel deploy --prod
```

**Environment variables to set in Vercel dashboard:**

```bash
NEXT_PUBLIC_API_URL=https://your-backend.vercel.app
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxx
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
```

### Pipeline Deployment (Prefect Cloud)

1. **Set DATABASE_URL in Prefect Cloud:**

   Option A: Using Prefect Variables (simpler):
   ```bash
   prefect cloud login
   prefect variable set DATABASE_URL "postgresql://postgres.[project]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres"
   ```

   Option B: Using Prefect Secrets (more secure):
   - Go to Prefect Cloud → Blocks → Add Block → Secret
   - Name: `database-url`
   - Value: Your Supabase connection string
   - Reference in code: `from_secret("database-url")`

2. **Deploy flow:**
   ```bash
   cd pipe
   source venv/bin/activate
   prefect cloud login
   python deployments/register.py
   ```

3. **Set additional variables:**
   ```bash
   prefect variable set RESEND_API_KEY "re_xxxxxxxxxxxxx"
   prefect variable set SIGNAL_SYMBOLS "AAPL,BTC-USD"
   ```

### Local vs Production

**Local development** (uses Docker database):
- Backend: `DATABASE_URL=postgresql+psycopg://signals_user:signals_password@localhost:5432/trading_signals`
- Pipe: `DATABASE_URL=postgresql://signals_user:signals_password@localhost:5432/trading_signals`

**Production** (uses Supabase):
- Set `DATABASE_URL` in deployment platforms (Vercel, Prefect Cloud)
- No code changes needed - same codebase reads from platform-provided env vars

### Troubleshooting

**Check backend is using correct database:**
```bash
# Backend logs on startup will show: "Connected to database: [host]"
# Check Vercel logs after deployment
```

**Check pipeline is using correct database:**
```bash
# Prefect flow logs will show: "Database connection: [host]"
# Check Prefect Cloud flow run logs
```

**Common issues:**
- **Wrong port**: Supabase pooler uses 6543 (not 5432)
- **Missing `+psycopg`**: Backend needs `postgresql+psycopg://...` for SQLAlchemy
- **Transaction mode**: Use Session mode in Supabase pooler for long-running queries

## Documentation

- **README.md** - Quick start guide and project overview
- **docs/MVP.md** - Project scope, user persona, success metrics
- **docs/ARCHITECTURE.md** - System design with code examples
- **docs/DATA-SCIENCE.md** - RSI + EMA explained with Python code
- **docs/IMPLEMENTATION_SUMMARY.md** - Current implementation status (backend endpoints, database, what's done vs Phase 2)
- **docs/archive/** - Original comprehensive docs (reference only)

When stuck, read docs in this order: MVP.md → ARCHITECTURE.md → IMPLEMENTATION_SUMMARY.md → DATA-SCIENCE.md

## Current Implementation Status

### ✅ Completed (MVP Phase 1)

1. **Database**: Complete schema with EMA support, double opt-in, idempotency (`db/schema.sql`)
2. **Backend API**: All endpoints implemented and ready for testing
   - Signals endpoints (list, get by symbol, history)
   - Market data endpoints (OHLCV, indicators)
   - Subscribe/unsubscribe endpoints (stores to DB)
   - Health check with DB connection test
3. **Prefect Pipeline**: Single unified flow working with all 4 assets
   - Fetches 15m data from Yahoo Finance
   - Calculates RSI + EMA indicators
   - Generates and stores signals with idempotency
   - Logs strong signals (strength >= 70)
4. **Data Science**: RSI, EMA (MACD available but not used)
5. **Frontend**: Dashboard with `useSignals()` hook, signal cards
6. **Testing**: pytest structure configured

### 🔜 Next Steps (Phase 2)

1. **Email Integration**: Implement Resend email sending
   - Welcome emails on subscription
   - Confirmation emails (double opt-in flow)
   - Signal notification emails
2. **Frontend Enhancements**: Landing page, signal detail pages, charts
3. **Testing**: Write comprehensive tests for indicators and API endpoints
4. **Deployment**: Deploy to Vercel (frontend + backend) and Prefect Cloud (pipeline)
5. **Monitoring**: Set up PostHog analytics, error tracking

### 📝 Development Workflow

Start with local Docker setup → Test pipeline → Verify API endpoints → Connect frontend → Deploy

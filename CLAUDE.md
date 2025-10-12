# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trading Signals MVP - An automated system that monitors Bitcoin and Ethereum, calculates technical indicators (RSI + EMA), generates trading signals, and sends email notifications to subscribers.

**Solo dev project** designed for incremental learning and building. Start small, add complexity as you understand each piece.

## Architecture

This is a **multi-component system** with 4 independent parts:

```zsh
Yahoo Finance API → Prefect Pipeline → Supabase → FastAPI → Next.js → User
```

**Key principle**: Each component can be developed and tested independently.

### Component Responsibilities

1. **Prefect Pipeline** (`pipe/`): Fetch data, calculate indicators, generate signals, send emails
2. **Data Science** (`data/`): Indicator calculations (RSI, EMA) and signal generation logic
3. **FastAPI Backend** (`backend/`): REST API serving signals and market data to frontend
4. **Next.js Frontend** (`frontend/`): Public dashboard displaying signals and email signup
5. **Database** (`db/`): Supabase PostgreSQL schema with 6 core tables

**Data flow**: Pipeline writes → Database stores → API reads → Frontend displays

## Development Commands

### Database Setup (Supabase)

```bash
# 1. Create Supabase project at supabase.com
# 2. Copy connection string

# 3. Run schema
psql $DATABASE_URL -f db/schema.sql

# 4. Seed initial data
psql $DATABASE_URL -f db/seeds/symbols.sql
```

### Backend (FastAPI)

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run development server
uvicorn api.main:app --reload --port 8000

# API docs available at: http://localhost:8000/docs
```

### Frontend (Next.js)

```bash
cd frontend
npm install

# Development
npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Production build
npm run start        # Start production server
npm run lint         # ESLint check
npm run type-check   # TypeScript check
```

### Prefect Pipeline

```bash
cd pipe
pip install -r requirements.txt

# Test flows locally (dry run)
python flows/market_data_ingestion.py
python flows/indicator_calculation.py
python flows/signal_generation.py

# Deploy to Prefect Cloud
prefect cloud login
prefect deploy --all

# View flow runs
prefect flow-run ls
```

### Data Science (Indicators)

```bash
# The data/ folder contains pure Python modules
# Test indicators in isolation:

cd data
python -c "from indicators.rsi import calculate_rsi; print('RSI module loaded')"
python -c "from signals.signal_generator import generate_signal; print('Signal generator loaded')"
```

## Database Schema

**6 Core Tables** (see `db/schema.sql`):

1. **symbols** - Assets we track (BTC-USD, ETH-USD)
2. **market_data** - Raw OHLCV from Yahoo Finance
3. **indicators** - Calculated RSI, MACD (note: docs mention EMA, schema has MACD - use RSI+EMA for MVP)
4. **signals** - Generated BUY/HOLD signals with strength scores
5. **email_subscribers** - Users subscribed to notifications
6. **sent_notifications** - Audit log of emails sent

**Key indexes**: All tables have `(symbol, timestamp DESC)` indexes for fast time-series queries.

## Code Structure Patterns

### Prefect Flows (`pipe/`)

```zsh
pipe/
├── flows/              # Main Prefect flows (high-level orchestration)
│   ├── market_data_ingestion.py
│   ├── indicator_calculation.py
│   ├── signal_generation.py
│   └── notification_sender.py
├── tasks/              # Reusable tasks (low-level operations)
│   ├── data_fetching.py
│   ├── data_validation.py
│   └── email_sending.py
└── schedules.py        # Cron schedules for flows
```

**Pattern**: Flows orchestrate, tasks execute. Keep tasks pure/testable.

### Data Science (`data/`)

```zsh
data/
├── indicators/         # Technical indicator calculations
│   ├── rsi.py         # RSI (14-period)
│   └── macd.py        # MACD (not in MVP, use for Phase 2)
├── signals/           # Signal generation logic
│   ├── signal_generator.py  # Main signal rules
│   └── signal_scorer.py     # Strength scoring (0-100)
└── utils/             # Shared utilities
```

**Pattern**: Each indicator is a pure function: `calculate_indicator(df) -> df_with_indicator`

### FastAPI Backend (`backend/`)

```zsh
backend/
├── api/
│   ├── main.py           # FastAPI app + CORS
│   ├── routes/           # API endpoints
│   │   ├── signals.py    # GET /api/signals
│   │   ├── subscribe.py  # POST /api/subscribe
│   │   └── health.py     # GET /api/health
│   ├── models/           # Pydantic models
│   └── db.py             # Database connection
├── requirements.txt
└── vercel.json           # Vercel deployment config
```

**Pattern**: Each route file handles one resource. Use Pydantic for validation.

### Next.js Frontend (`frontend/`)

```zsh
frontend/
├── src/
│   ├── app/                    # App Router pages
│   │   ├── page.tsx           # Landing page
│   │   ├── dashboard/         # Signal dashboard
│   │   └── signal/[symbol]/   # Signal detail
│   └── components/
│       ├── landing/           # Landing page sections
│       │   ├── Hero.tsx
│       │   ├── LiveSignals.tsx
│       │   └── EmailSignup.tsx
│       └── dashboard/         # Dashboard components
├── package.json
└── next.config.ts
```

**Pattern**: Server Components for data fetching, Client Components for interactivity.

## Key Integration Points

### 1. Pipeline → Database

Prefect flows write directly to Supabase tables:

```python
# In pipe/tasks/data_fetching.py
from sqlalchemy import create_engine

engine = create_engine(os.getenv("DATABASE_URL"))
df.to_sql('market_data', engine, if_exists='append')
```

### 2. Database → FastAPI

Backend reads from Supabase using SQLAlchemy:

```python
# In backend/api/routes/signals.py
from sqlalchemy import select

signals = session.execute(
    select(Signal).order_by(Signal.timestamp.desc()).limit(10)
).scalars().all()
```

### 3. FastAPI → Next.js

Frontend fetches via fetch API (Server Components):

```typescript
// In frontend/src/app/dashboard/page.tsx
const signals = await fetch(`${API_URL}/api/signals?limit=50`)
  .then(r => r.json())
```

### 4. Resend Email Integration

Used in both pipeline (notifications) and backend (confirmations):

```python
import resend

resend.api_key = os.getenv("RESEND_API_KEY")
resend.Emails.send({
    "from": "signals@yourdomain.com",
    "to": email,
    "subject": "BTC-USD BUY Signal",
    "html": template
})
```

## MVP Scope & Simplifications

**What's IN** (build this first):

- 2 assets: BTC-USD, ETH-USD only
- 2 indicators: RSI + EMA (skip MACD for now, despite schema having it)
- 1 Prefect flow: Fetch → Calculate → Signal → Email (all in one)
- Fetch 15m data directly from Yahoo Finance (no resampling)
- Email notifications only (no Telegram)

**What's OUT** (Phase 2):

- More cryptocurrencies or stocks
- MACD, Bollinger Bands, or other indicators
- User authentication
- 5-minute to 15-minute resampling
- Real-time WebSocket updates

**Important**: Database schema includes MACD fields, but MVP docs specify RSI+EMA only. You can populate MACD fields with NULL initially, or add EMA fields to schema.

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

**Unit tests**: Test indicators in isolation with known inputs

```python
# Example: test RSI calculation
def test_rsi_calculation():
    prices = pd.Series([100, 102, 101, 103, 105])
    rsi = calculate_rsi(prices, period=14)
    assert 0 <= rsi.iloc[-1] <= 100
```

**Integration tests**: Test flows with real Yahoo Finance data (mark as `@pytest.mark.integration`)

**Visual tests**: Use matplotlib to plot indicators and verify they look correct

### Common Gotchas

1. **Timezones**: Always use UTC for timestamps. Supabase stores TIMESTAMPTZ, but Python datetime must be timezone-aware.

2. **Yahoo Finance rate limits**: yfinance is free but can be flaky. Add retry logic (Prefect handles this).

3. **Signal duplicates**: Use `UNIQUE(symbol, timestamp)` constraint in signals table to prevent dupes.

4. **Email deliverability**: Must configure DKIM/SPF/DMARC in Resend for production.

5. **Prefect local vs cloud**: `prefect.serve()` runs locally. `prefect deploy` sends to Prefect Cloud.

## Working with Indicators

Each indicator follows this pattern:

```python
# data/indicators/rsi.py
import pandas as pd

def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate RSI (Relative Strength Index)

    Args:
        df: DataFrame with 'Close' column
        period: Lookback period (default 14)

    Returns:
        Series of RSI values (0-100)
    """
    delta = df['Close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi
```

**To add a new indicator**:

1. Create `data/indicators/new_indicator.py` with `calculate_new_indicator()` function
2. Add to `pipe/flows/indicator_calculation.py` flow
3. Add column to `indicators` table in schema
4. Update `data/signals/signal_generator.py` to use it

## Working with Signals

Signal generation logic in `data/signals/signal_generator.py`:

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

**Frontend & Backend**: Vercel (zero-config, just `vercel deploy`)

**Pipeline**: Prefect Cloud (managed scheduling, free tier)

**Database**: Supabase (managed PostgreSQL, free tier)

**All deploy from repo root, each component independently.**

## Documentation

- **README.md** - Quick start guide
- **docs/MVP.md** - Project scope, user persona, success metrics
- **docs/ARCHITECTURE.md** - System design with code examples
- **docs/DATA-SCIENCE.md** - RSI + EMA explained with Python code
- **docs/archive/** - Original comprehensive docs (reference only)

When stuck, read docs in this order: MVP.md → ARCHITECTURE.md → DATA-SCIENCE.md

## Next Steps for Development

1. **Week 1**: Set up Supabase, build basic Prefect flow to fetch and store data
2. **Week 2**: Implement RSI+EMA calculations, generate signals, store in DB
3. **Week 3**: Build FastAPI endpoints, test with Postman/curl
4. **Week 4**: Build Next.js frontend, connect to API, add email signup

Start simple: fetch data for 1 asset, calculate 1 indicator, store in DB. Then expand.

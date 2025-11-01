# Signals

Track automated trading signals across multiple asset classes. Get email alerts when technical indicators detect high-confidence opportunities in crypto, stocks, ETFs, and forex.

## What It Does

Daily at 10 PM UTC, the system:

1. Fetches the latest daily OHLCV data from Yahoo Finance.
2. Calculates RSI / EMA indicators per asset.
3. Runs signal analysis to generate BUY / SELL / HOLD signals with strength scores.
4. Sends email notifications when strength exceeds threshold (≥70).

See the **Data Pipeline Workflow** section below for the exact Prefect flows and schedules.

## MVP Asset Coverage

Starting simple with 2 assets:

- **BTC-USD** (Bitcoin)
- **AAPL** (Apple)

Expanding to ETFs and forex as the platform grows.

## Tech Stack

- **Frontend**: Next.js 15 + TypeScript + TailwindCSS (deployed on Vercel)
- **Backend**: FastAPI + Python 3.11
- **Database**: Supabase (PostgreSQL)
- **Pipeline**: Prefect for orchestration
- **Email**: Resend API
- **Analytics**: PostHog

## Project Structure

```bash
signals/
├── frontend/           # Next.js application
├── backend/            # FastAPI server
├── pipe/               # Prefect flows (data pipeline)
├── db/                 # Database schemas and migrations
└── docs/               # Documentation
    ├── MVP.md          # Project scope and goals
    ├── ARCHITECTURE.md # System design
    └── DATA-SCIENCE.md # Indicators explained
```

Provider clients live under `pipe/data/sources` (Alpha Vantage intraday + Yahoo chart fallback).

## Data Pipeline Workflow

| Flow | Module | Purpose | Default Schedule |
| --- | --- | --- | --- |
| `market-data-backfill` | `pipe/flows/market_data_backfill.py` | Fetch multi-year daily OHLCV history for new symbols. | Manual (on demand) |
| `market-data-sync` | `pipe/flows/market_data_sync.py` | Fetch the latest daily OHLCV bars for all symbols. | Daily at 10:00 PM UTC |
| `signal-analyzer` | `pipe/flows/signal_analyzer.py` | Calculate indicators and generate BUY/SELL/HOLD signals. | Daily at 10:15 PM UTC |
| `notification-dispatcher` | `pipe/flows/notification_dispatcher.py` | Email subscribers about strong signals (strength ≥70). | Daily at 10:30 PM UTC |

Run flows ad-hoc with `python -m pipe.flows.<name>` or register the deployments with Prefect Cloud (see [docs/RUNBOOK.md](docs/RUNBOOK.md)).
Enable schedules via `python -m deployments.register --work-pool <pool>` and manage them with Prefect Cloud or `prefect deployment pause|resume <flow>/<deployment>`.

## Quick Setup (Local Development)

**Get running in 5 minutes:**

```bash
# 1. Database (Docker)
docker-compose up -d
export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"

# 2. Schema & Historical Data (~2 years of daily bars)
python scripts/apply_db.py
uv run --directory pipe python -m pipe.flows.historical_backfill --symbols BTC-USD,AAPL --backfill-range 2y
uv run --directory pipe python -m pipe.flows.signal_replay --symbols BTC-USD,AAPL --range-label 2y

# 3. Backend API
cd backend && uv run uvicorn api.main:app --reload  # http://localhost:8000

# 4. Frontend
cd frontend && bun run dev  # http://localhost:3000

# 5. Test Pipeline (optional)
uv run --directory pipe python -m pipe.flows.signal_generation --symbols BTC-USD,AAPL
uv run --directory pipe python -m pipe.flows.notification_sender --min-strength 60
```

**See** `scripts/README.md` for production setup (Supabase) and troubleshooting.

---

## Detailed Setup

### Prerequisites

- Python 3.11+
- Node.js 22+
- Docker (for local DB) OR Supabase account
- Resend API key (for email notifications)

### 1. Database Setup

- **Option A: Local (Docker)**

```bash
# Start PostgreSQL
docker-compose up -d

# Set connection string
export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"

# Initialize schema and seed 4 assets
python scripts/apply_db.py

# Backfill ~60 days of historical data
```

- **Option B: Production (Supabase)**

```bash
# Create project at https://supabase.com
# Copy connection string from Settings → Database

export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"

# Initialize schema and seed
python scripts/apply_db.py
```

### 2. Backend Setup

```bash
cd backend
uv sync

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run the API
uv run uvicorn api.main:app --reload
# API available at http://localhost:8000
```

### 3. Frontend Setup

```bash
cd frontend
bun install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with API URL

# Run the dev server
bun run dev
# App available at http://localhost:3000
```

### 4. Pipeline Setup (Prefect)

```bash
cd pipe
uv sync

# Create .env file
cp .env.example .env
# Edit .env with DATABASE_URL and RESEND_API_KEY

# Backfill + indicators (run from project root)
cd ..
uv run --directory pipe python -m pipe.flows.historical_backfill --symbols BTC-USD,AAPL --backfill-range 2y
uv run --directory pipe python -m pipe.flows.signal_replay --symbols BTC-USD,AAPL --range-label 2y

# Generate latest intraday signals + send notifications
uv run --directory pipe python -m pipe.flows.signal_generation --symbols BTC-USD,AAPL
uv run --directory pipe python -m pipe.flows.notification_sender --min-strength 60

# Optional: register Prefect deployments / schedules
prefect cloud login
uv run --directory pipe python -m deployments.register --work-pool default-prefect-managed-wp
# Pause/resume with Prefect CLI:
#   prefect deployment pause signal-generation/intraday-15m
#   prefect deployment resume signal-generation/intraday-15m
```

See [`docs/RUNBOOK.md`](docs/RUNBOOK.md) for flow commands, deployment management, and troubleshooting.

## Environment Variables

### Backend / Pipeline (`backend/.env`, `pipe/.env`)

```env
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
RESEND_FROM_EMAIL="Signals Bot <onboarding@resend.dev>"
SIGNAL_NOTIFY_THRESHOLD=60
APP_BASE_URL=https://signalsapp.dev
SIGNAL_SYMBOLS=BTC-USD,AAPL
POSTHOG_API_KEY=phc_...
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=phc_...
```

## Development Workflow

### Run Everything Locally

```bash
# Terminal 1: Backend
cd backend && uv run uvicorn api.main:app --reload

# Terminal 2: Frontend
cd frontend && bun run dev

# Terminal 3: Prefect (optional for testing)
uv run --directory pipe python -m pipe.flows.signal_generation
```

### Diagnostics & Testing

- **Pipeline smoke test**: `curl "http://localhost:8000/api/market-data/BTC-USD/ohlcv?range=2y&limit=5000"` to confirm history is loaded.
- **Diagnostics UI**: visit `http://localhost:3000/admin/backtest` to inspect signals, OHLCV rows, and backtest summaries after each flow run.
- **Automated tests**: `uv run pytest -q` (see `tests/README.md`).

## Documentation

- **[MVP.md](docs/MVP.md)** - What we're building and why
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flow
- **[DATA-SCIENCE.md](docs/DATA-SCIENCE.md)** - Indicators explained (concepts)
- **[data/README.md](data/README.md)** - Implementation guide (code)

## Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy
```

### Backend (Vercel)

```bash
cd backend
vercel deploy
```

### Prefect Flows (Prefect Cloud)

```bash
cd prefect
prefect deploy
```

## Key Features

- ✅ Real-time price monitoring (15-minute intervals)
- ✅ Technical indicators (RSI, EMA)
- ✅ Email notifications via Resend
- ✅ Public dashboard (no login required)
- ✅ Signal strength scoring (0-100)
- ✅ Plain English explanations

## MVP Scope

**In Scope:**

- 4 representative assets (1 per type: crypto, stock, ETF, forex)
- RSI and EMA indicators
- Email notifications
- Public dashboard
- Multi-asset signal comparison

**Out of Scope (Phase 2):**

- Market hours handling (stocks/ETFs closed on weekends)
- More assets per category
- Additional indicators (MACD, Bollinger Bands)
- Asset-specific strategies (different indicators per asset type)
- Portfolio tracking
- User authentication
- Payment system (Stripe)
- Telegram notifications

## Success Metrics

- 100 email signups in 30 days
- 20% activation rate (users who click a signal within 7 days)
- 15% signal click-through
- 25% email open rate
- 90% email delivered
- 95% data pipeline reliability
- 10+ people say "I traded based on your signal"
- 5+ people say "I learned something new"
- 0 people say "This feels like spam"

## License

MIT

## Contributing

This is an MVP project. Contributions welcome after initial launch.

## Support

For questions or issues, open a GitHub issue.

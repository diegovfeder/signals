# Signals

Track automated trading signals across multiple asset classes. Get email alerts when technical indicators detect high-confidence opportunities in crypto, stocks, ETFs, and forex.

> **Doc map:** [MVP](docs/MVP.md) · [Architecture](docs/ARCHITECTURE.md) · [Operations](docs/resources/OPERATIONS.md) · [Project Board](https://github.com/users/diegovfeder/projects/4/views/1)

## 🚀 Quick Start - 1 Minute Overview

**What This Does**: Automated trading signals for crypto & stocks with plain-English explanations

**Core Stack**:
- **Frontend**: Next.js 16 on Vercel → https://signals-dvf.vercel.app
- **Backend**: FastAPI on Vercel → https://signals-api-dvf.vercel.app/docs
- **Pipeline**: Prefect Cloud (daily at 10 PM UTC)
- **Database**: Supabase PostgreSQL

**Data Flow**: Yahoo Finance → Prefect → Supabase → FastAPI → Next.js → User

**Who It's For**: "The Analytical Amateur" (28-40, tech professionals, $10K-25K portfolio)
→ Wants to understand markets, not gamble. Values transparency over hype.

**Current Value**:
- BTC-USD + AAPL signals with confidence scores (0-100)
- RSI + EMA momentum analysis
- Plain-English reasoning: "RSI is at 28 (oversold) and turning upward..."

**Where to Edit for Maximum User Value**:
1. **Signal Quality**: `pipe/lib/signals/strategies/` - Tune crypto_momentum.py thresholds
2. **User Trust**: `frontend/src/components/dashboard/SignalCard.tsx` - Expand reasoning display
3. **Actionability**: `pipe/lib/signals/signal_scorer.py` - Adjust strength calculation

**Key Principle**: Trust through transparency. User motto: "If I can understand it, I can trust it."

**Environment Setup**:
```bash
# Global setup
cp .env.example .env

# Backend
cd backend && cp .env.example .env

# Frontend
cd frontend && cp .env.example .env.local

# Pipeline
cd pipe && cp .env.example .env
```

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

- **Frontend**: Next.js 16 + TypeScript + TailwindCSS (Vercel)
- **Backend**: FastAPI + Python 3.11 (Vercel)
- **Pipeline**: Prefect 2 (nightly flows in Prefect Cloud)
- **Database**: Supabase PostgreSQL (Session Mode pooler)
- **Email**: Resend API (sandbox sender for MVP)
- **Analytics**: PostHog (optional)

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

Provider clients live under `pipe/lib/api/` (Yahoo Finance for daily OHLCV data).

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
uv run --directory pipe python -m pipe.flows.market_data_backfill --symbols AAPL,BTC-USD --backfill-range 2y
uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD --range-label 2y

# 3. Backend API
cd backend && uv run uvicorn api.main:app --reload  # http://localhost:8000

# 4. Frontend
cd frontend && bun run dev  # http://localhost:3000

# 5. Test Pipeline (optional)
uv run --directory pipe python -m pipe.flows.market_data_sync --symbols AAPL,BTC-USD
uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD
uv run --directory pipe python -m pipe.flows.notification_dispatcher --min-strength 60
```

Need more detail? See `docs/resources/OPERATIONS.md` for Prefect runbooks and troubleshooting.

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

# Backfill up to 10 years of daily history (once per symbol)
uv run --directory pipe python -m pipe.flows.market_data_backfill --symbols AAPL,BTC-USD --backfill-range 10y
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
uv run --directory pipe python -m pipe.flows.historical_backfill --symbols AAPL,BTC-USD --backfill-range 2y
uv run --directory pipe python -m pipe.flows.signal_replay --symbols AAPL,BTC-USD --range-label 2y

# Generate latest intraday signals + send notifications
uv run --directory pipe python -m pipe.flows.signal_generation --symbols AAPL,BTC-USD
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
SIGNAL_SYMBOLS=AAPL,BTC-USD
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

- **[MVP.md](docs/MVP.md)** – what we're building, target user, KPIs.
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** – component responsibilities + nightly cadence.
- **[TODOs.md](docs/TODOs.md)** – project board workflow and issue template usage.
- **[resources/OPERATIONS.md](docs/resources/OPERATIONS.md)** – Prefect runbook + troubleshooting.
- **[resources/DATA-SOURCES-AND-TOOLS.md](docs/resources/DATA-SOURCES-AND-TOOLS.md)** – alternate providers + research links.
- **[resources/TECHNICAL-ANALYSIS.md](docs/resources/TECHNICAL-ANALYSIS.md)** – indicator math + strategy heuristics.

## Deployment

### Frontend (Vercel)

```bash
cd frontend
vercel deploy --prod
```

### Backend (Vercel)

```bash
cd backend
vercel deploy --prod
```

### Prefect Flows (Prefect Cloud)

```bash
prefect cloud login
uv run --directory pipe python -m deployments.register --work-pool <prefect-pool>
```

## Key Features

- ✅ Daily OHLCV ingestion + signal generation (Yahoo Finance)
- ✅ Technical indicators (RSI, EMA)
- ✅ Email notifications via Resend
- ✅ Public dashboard (no login required)
- ✅ Signal strength scoring (0-100)
- ✅ Plain English explanations

## MVP Scope

**In Scope (today):**

- Daily BTC-USD + AAPL signals (more assets post-reliability goals)
- RSI / EMA / MACD histogram indicators
- Double opt-in subscriptions (notifications live once custom domain is ready)
- Public dashboard + admin subscriber views

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

## Working With This Repo

- **Docs-first**: Update `docs/ARCHITECTURE.md`, `docs/MVP.md`, or ops guides when behavior changes.
- **Issues before code**: Open a GitHub issue via `.github/ISSUE_TEMPLATE/task.md` and add it to the [Signals – Tasks project board](https://github.com/users/diegovfeder/projects/4/views/1) before starting non-trivial work.
- **Manual validation**: Automated tests are paused; run the relevant Prefect flows, hit `/health`, and load the affected frontend pages after `bun run lint && bun run type-check`.

**Quick Links:**
- 📋 [View Project Board](https://github.com/users/diegovfeder/projects/4/views/1)
- 📝 [Open New Issue](https://github.com/diegovfeder/signals/issues/new?template=task.md)
- 📚 [Process Guide](docs/TODOs.md)

For questions or issues, open a GitHub issue.

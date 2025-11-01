# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Trading Signals MVP

An automated trading signals system across multiple asset classes. Analyzes technical indicators (RSI + EMA) for crypto, stocks, ETFs, and forex, generates high-confidence signals, and sends email alerts to subscribers.

**Small dev team MVP** - Start simple, learn incrementally, add complexity as needed.

## What It Does

Daily at 10 PM UTC:

1. Fetches daily price data from Yahoo Finance for:
   - **BTC-USD** (Bitcoin)
   - **AAPL** (Apple)
2. Calculates RSI (14-period) and EMA (12/26 periods) for each asset
3. Generates BUY/HOLD signals using same logic across all asset types
4. Saves signals to Supabase (PostgreSQL)
5. Emails subscribers if any signal strength >= 70/100

## Tech Stack

- **Frontend**: Next.js 15 + TypeScript + TailwindCSS (Vercel)
- **Backend**: FastAPI + Python 3.11 (Vercel)
- **Database**: Supabase (PostgreSQL)
- **Pipeline**: Prefect orchestration
- **Email**: Resend API
- **Analytics**: PostHog

## Architecture

### High-Level Flow

```text
Yahoo Finance → Prefect Flow → Supabase → FastAPI → Next.js → User
```

### Components

1. **Prefect Pipeline** (`pipe/`) - Fetch data, calculate indicators, generate signals, send emails
   - Includes `pipe/data/` - RSI and EMA calculation modules
2. **FastAPI Backend** (`backend/`) - REST API for signals and subscriptions
3. **Next.js Frontend** (`frontend/`) - Public dashboard and landing page
4. **Database** (`db/`) - Supabase PostgreSQL schema

### Simplified Decisions (MVP)

- **No 5m → 15m resampling**: Fetch 15m data directly from Yahoo Finance
- **Single Prefect flow**: `signal_generation.py` with all tasks inline (not separate flows)
- **2 assets**: BTC-USD (crypto), AAPL (stock)
- **2 indicators**: RSI + EMA (MACD in schema but NULL for MVP)
- **Log notifications**: Email sending via Resend in Phase 2
- **Public dashboard**: No authentication required (Phase 1)

## Project Structure

```bash
signals/
├── frontend/          # Next.js 15 application
├── backend/           # FastAPI server
├── pipe/              # Prefect flows
│   └── data/         # Indicator calculations (RSI, EMA)
├── db/                # Database schema and seeds
├── scripts/           # Utility scripts
└── docs/              # Documentation
    ├── MVP.md         # Project scope and goals
    ├── ARCHITECTURE.md # System design
    └── DATA-SCIENCE.md # Indicators explained
```

## Getting Started

### Prerequisites

- Node.js 22+
- Python 3.11+
- Supabase account
- Resend API key

### Environment Variables

**Backend** (`.env` in `/backend`):

```bash
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
POSTHOG_API_KEY=phc_...  # Optional
```

**Frontend** (`.env.local` in `/frontend`):

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=phc_...  # Optional
```

**Pipeline** (`.env` in `/pipe`):

```bash
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
```

### Quick Setup (Local with Docker)

1. **Database Setup**:

   ```bash
   # Start PostgreSQL (auto-loads schema and seeds)
   docker-compose up -d

   # Connection string (from docker-compose.yml)
   export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"

   # Verify database is ready
   psql $DATABASE_URL -c "SELECT * FROM symbols;"
   ```

   **Or use Supabase for production**:

   ```bash
   # Create project at supabase.com, then:
   psql $DATABASE_URL -f db/schema.sql
   psql $DATABASE_URL -f db/seeds/symbols.sql
   ```

2. **Backend**:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Create .env from template
   cp .env.example .env
   # Edit .env with DATABASE_URL and RESEND_API_KEY

   # Start API server
   uvicorn api.main:app --reload --port 8000
   # API docs: http://localhost:8000/api/docs
   # Health: http://localhost:8000/health
   ```

3. **Frontend**:

   ```bash
   cd frontend
   npm install   # or bun install

   # Create .env.local
   cp .env.example .env.local
   # Edit with NEXT_PUBLIC_API_URL=http://localhost:8000

   # Development
   npm run dev          # http://localhost:3000
   ```

4. **Pipeline** (optional for testing):

   ```bash
   cd pipe
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Create .env
   cp .env.example .env
   # Edit with DATABASE_URL and RESEND_API_KEY

   # Test single unified flow locally
   python -m pipe.flows.signal_generation

   # Deploy to Prefect Cloud (runs every 15 min)
   prefect cloud login
   python schedules.py
   ```

## Common Development Commands

### Database

```bash
# Connect to database
psql $DATABASE_URL

# Query signals
psql $DATABASE_URL -c "SELECT * FROM signals WHERE strength >= 70 ORDER BY signaled_at DESC LIMIT 10;"

# Check data freshness
psql $DATABASE_URL -c "SELECT asset_id, MAX(timestamp) FROM ohlcv GROUP BY asset_id;"
```

### Backend

```bash
# Start with hot reload
uvicorn api.main:app --reload --port 8000

# View API docs (Swagger)
open http://localhost:8000/api/docs

# Test health endpoint
curl http://localhost:8000/health

# Run tests
pytest -v
```

### Frontend

```bash
# Development
npm run dev

# Production build
npm run build && npm run start

# Type checking
npm run type-check

# Linting
npm run lint
```

### Pipeline

```bash
# Test single unified flow locally
cd pipe && python -m pipe.flows.signal_generation

# Check Prefect flow runs
prefect flow-run ls --limit 10

# View logs
prefect flow-run logs <flow-run-id>

# Deploy to Prefect Cloud
python schedules.py
```

## API Endpoints

**All endpoints are implemented and ready for testing.** See `docs/IMPLEMENTATION_SUMMARY.md` for details.

### Signals

- `GET /api/signals/` - List all signals (filterable by signal_type, min_strength, limit, offset)
- `GET /api/signals/{symbol}` - Latest signal for a specific symbol
- `GET /api/signals/{symbol}/history` - Signal history (default 30 days, max 90)

### Market Data

- `GET /api/market-data/{symbol}/ohlcv` - OHLCV bars (default 100, max 500)
- `GET /api/market-data/{symbol}/indicators` - Calculated indicators (RSI, EMA-12, EMA-26, MACD)

### Subscriptions

- `POST /api/subscribe/` - Subscribe email (stores to DB, generates tokens)
- `POST /api/subscribe/unsubscribe/{token}` - Unsubscribe via token

**Note**: Email confirmation endpoint (`/confirm/{token}`) planned for Phase 2.

### Health

- `GET /health` - System health check with database connection test

## Signal Generation Logic

### RSI Rules

- RSI < 30 → BUY (oversold, likely to bounce)
- RSI > 70 → HOLD (overbought, wait)
- RSI 30-70 → HOLD (neutral)

### EMA Rules

- EMA-12 crosses above EMA-26 → BUY (bullish momentum)
- EMA-12 crosses below EMA-26 → HOLD (bearish)

### Signal Strength

Weighted score (0-100) based on:

- Distance from RSI threshold (30/70)
- EMA separation magnitude
- Volume confirmation

**Notification threshold**: Log (Phase 1) or email (Phase 2) if strength >= 70

## Database Schema

**6 Core Tables** (see `db/schema.sql`):

1. `symbols` - BTC-USD (crypto), AAPL (stock)
2. `market_data` - 15-minute OHLCV price data for all assets
3. `indicators` - RSI, EMA-12, EMA-26 (MACD fields available but NULL in MVP)
4. `signals` - Generated signals with strength scores, idempotency_key, reasoning
5. `email_subscribers` - Double opt-in subscribers with confirmation/unsubscribe tokens
6. `sent_notifications` - Audit log for email sending (Phase 2)

**Key Indexes**: `(symbol, timestamp DESC)` on all tables for fast time-series queries.

**Schema Location**: Single consolidated `db/schema.sql` file (no migrations).

## Frontend Design

### Design System

- **Framework**: TailwindCSS
- **Theme**: Dark mode inspired by Resend
- **Colors**: Minimal, professional palette
- **Typography**: Clean, readable fonts
- **Layout**: Responsive, mobile-first

### Key Pages

- **Landing** (`/`) - Hero, live signals, email signup, how it works
- **Dashboard** (`/dashboard`) - Signal cards grid, filters
- **Signal List** (`/signals`) - List of all signals
- **Signal Detail** (`/signals/[symbol]`) - Chart with indicators, reasoning, educational content

### Data Fetching

Current implementation uses **Client Components** with custom React hooks:

```typescript
// frontend/src/lib/hooks/useSignals.ts
export function useSignals() {
  const [signals, setSignals] = useState([])
  // Fetches from NEXT_PUBLIC_API_URL
}

// frontend/src/app/dashboard/page.tsx
'use client'
const { signals, loading, error } = useSignals()
```

Consider TanStack Query for Phase 2 (caching, polling).

## Email Notifications

**Status**: Phase 2 (not yet implemented)

### Planned Flow (Phase 2)

1. User subscribes → Confirmation email sent
2. User confirms → Welcome email
3. Strong signal (strength >= 70) → Notification email with plain English explanation
4. One-click unsubscribe

### Current Behavior (Phase 1)

- Subscription stores email to database with tokens generated
- Strong signals are **logged to console** instead of emailed
- Unsubscribe endpoint works (updates database)

### Configuration (Phase 2)

- DKIM/SPF/DMARC for domain
- `List-Unsubscribe` header
- Webhooks for tracking opens/bounces

## Deployment

### Vercel (Frontend + API)

```bash
# Frontend
cd frontend && vercel deploy

# Backend
cd backend && vercel deploy
```

### Prefect Cloud (Pipeline)

```bash
cd pipe
prefect cloud login
prefect deploy
```

### Local Database

**Local (Docker)**:

```bash
docker-compose up -d  # Auto-initializes schema
```

**Supabase (Production)**:

- Create project at supabase.com
- Run `db/schema.sql` via SQL editor (no migrations)
- Copy connection string to environment variables

## Monitoring

- **Prefect Cloud**: Flow runs, task failures, execution logs
- **Supabase**: Query performance, connection pool
- **Vercel**: Page views, API latency, error rates
- **PostHog**: User events, funnels, retention
- **Resend**: Email delivery, opens, bounces

## Troubleshooting

### Database Connection

```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1;"

# Check if tables exist
psql $DATABASE_URL -c "\dt"
```

### API Issues

```bash
# Check if API is running
curl http://localhost:8000/health

# View API logs
# (Logs in terminal where uvicorn is running)
```

### Prefect Issues

```bash
# Check flow runs
prefect flow-run ls --limit 5

# View specific run logs
prefect flow-run logs <run-id>
```

### Frontend Issues

```bash
# Clear node_modules
rm -rf node_modules && npm install

# Check Next.js build
npm run build
```

## Important Notes

### MVP Scope

**✅ Phase 1 (Implemented)**:

- 2 assets: BTC-USD (crypto), AAPL (stock)
- RSI + EMA indicators (same logic for all asset types)
- 24/7 operation (ignore market hours for stocks/ETFs)
- Complete backend API (all endpoints working)
- Database schema with double opt-in, idempotency
- Single unified Prefect flow
- Frontend dashboard with client-side hooks
- Logging notifications (console)
- Testing structure (pytest)

**🔜 Phase 2 (Planned)**:

- Email notifications via Resend
- Email confirmation flow (double opt-in)
- More assets per category
- MACD, Bollinger Bands
- Asset-specific strategies (different indicators per asset type)
- Market hours handling
- User authentication
- Telegram notifications
- Portfolio tracking

### Development Philosophy

- **Start simple**: Get one flow working end-to-end before adding complexity
- **Test incrementally**: Test each component independently before integration
- **Document as you go**: Update docs when you make significant changes
- **Deploy early**: Don't wait for perfection, deploy and iterate

### Risk Disclosure

⚠️ **NOT financial advice** - This is an educational tool. Users trade at their own risk.

## Key Resources

- **Documentation**: See `docs/` folder
  - `MVP.md` - Project scope and goals
  - `ARCHITECTURE.md` - System design and patterns
  - `DATA-SCIENCE.md` - RSI and EMA explained
  - `IMPLEMENTATION_SUMMARY.md` - ✅ **Current implementation status (what's done vs Phase 2)**
- **CLAUDE.md** - Guidance for Claude Code AI assistant
- **README.md** - Project overview and quick start

---

**Version**: 1.1.0 (Phase 1 Complete)
**Last Updated**: October 2025
**Status**: Backend + Pipeline + Frontend implemented, ready for Phase 2 (email integration)

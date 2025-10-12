# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Trading Signals MVP

An automated trading signals system across multiple asset classes. Analyzes technical indicators (RSI + EMA) for crypto, stocks, ETFs, and forex, generates high-confidence signals, and sends email alerts to subscribers.

**Solo dev MVP** - Start simple, learn incrementally, add complexity as needed.

## What It Does

Every 15 minutes:
1. Fetches price data from Yahoo Finance (15-minute bars) for:
   - **Crypto**: BTC-USD (Bitcoin)
   - **Stocks**: AAPL (Apple)
   - **ETF**: IVV (iShares Core S&P 500)
   - **Forex**: BRL=X (Brazilian Real / US Dollar)
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

```
Yahoo Finance → Prefect Flow → Supabase → FastAPI → Next.js → User
```

### Components

1. **Prefect Pipeline** (`pipe/`) - Fetch data, calculate indicators, generate signals, send emails
2. **Data Science** (`data/`) - RSI and EMA calculation modules
3. **FastAPI Backend** (`backend/`) - REST API for signals and subscriptions
4. **Next.js Frontend** (`frontend/`) - Public dashboard and landing page
5. **Database** (`db/`) - Supabase PostgreSQL schema

### Simplified Decisions (MVP)

- **No 5m → 15m resampling**: Fetch 15m data directly from Yahoo Finance
- **Single Prefect flow**: Everything in one flow to start (split later if needed)
- **2 assets only**: BTC-USD and ETH-USD
- **2 indicators only**: RSI + EMA (skip MACD for now)
- **Email only**: No Telegram/SMS in MVP
- **Public dashboard**: No authentication required

## Project Structure

```
signals/
├── frontend/          # Next.js 15 application
├── backend/           # FastAPI server
├── data/              # Indicator calculations (RSI, EMA)
├── pipe/              # Prefect flows
├── db/                # Database schema and seeds
├── scripts/           # Utility scripts
└── docs/              # Documentation
    ├── MVP.md         # Project scope and goals
    ├── ARCHITECTURE.md # System design
    └── DATA-SCIENCE.md # Indicators explained
```

## Getting Started

### Prerequisites

- Node.js 18+
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

### Quick Setup

1. **Database Setup**:
   ```bash
   # Create Supabase project at supabase.com
   # Copy connection string

   # Run schema
   psql $DATABASE_URL -f db/schema.sql

   # Seed data
   psql $DATABASE_URL -f db/seeds/symbols.sql
   ```

2. **Backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

   # Start API server
   uvicorn api.main:app --reload --port 8000
   ```

3. **Frontend**:
   ```bash
   cd frontend
   npm install

   # Development
   npm run dev          # http://localhost:3000
   ```

4. **Pipeline** (optional for testing):
   ```bash
   cd pipe
   pip install -r requirements.txt

   # Test flow locally
   python flows/generate_signals.py

   # Deploy to Prefect Cloud
   prefect cloud login
   prefect deploy
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

# View API docs
open http://localhost:8000/docs

# Run tests (when written)
pytest backend/tests/
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
# Test flow locally
python -m pipe.flows.generate_signals

# Check Prefect flow runs
prefect flow-run ls --limit 10

# View logs
prefect flow-run logs <flow-run-id>
```

## API Endpoints

### Signals

- `GET /api/signals` - List recent signals (paginated)
- `GET /api/signals/{id}` - Single signal with OHLCV context

### Subscriptions

- `POST /api/subscribe` - Start double opt-in flow
- `GET /api/confirm?token=xxx` - Confirm subscription
- `GET /api/unsubscribe?token=xxx` - Unsubscribe

### Health

- `GET /api/health` - System health check

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

**Email threshold**: Only send if strength >= 70

## Database Schema

**5 Core Tables**:

1. `assets` - BTC-USD (crypto), AAPL (stocks), IVV (ETF), BRL=X (forex)
2. `ohlcv` - 15-minute price data for all assets
3. `indicators` - RSI, EMA-12, EMA-26 values per asset
4. `signals` - Generated signals with strength scores per asset
5. `email_subscribers` - Double opt-in subscribers

**Key Indexes**: `(asset_id, timestamp DESC)` on all tables for fast time-series queries.

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
- **Signal Detail** (`/signal/[id]`) - Chart with indicators, reasoning, educational content

### Data Fetching

- Start with Server Components (SSR for SEO)
- Consider TanStack Query for client-side data management post-MVP
- Keep it simple initially

## Email Notifications

### Flow

1. User subscribes → Confirmation email
2. User confirms → Welcome email
3. Strong signal → Notification email (plain English explanation)
4. One-click unsubscribe

### Configuration

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

### Supabase (Database)

- Create project at supabase.com
- Run migrations via SQL editor
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

**IN**:
- 4 representative assets: BTC-USD (crypto), AAPL (stocks), IVV (ETF), BRL=X (forex)
- RSI + EMA indicators (same logic for all asset types)
- 24/7 operation (ignore market hours for stocks/ETFs)
- Email notifications
- Public dashboard

**OUT** (Phase 2):
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
- **CLAUDE.md** - Guidance for Claude Code AI assistant
- **README.md** - Project overview and quick start

---

**Version**: 1.0.0 (Simplified MVP)
**Last Updated**: January 2025
**Status**: Ready for development

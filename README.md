# Signals

Track automated trading signals across multiple asset classes. Get email alerts when technical indicators detect high-confidence opportunities in crypto, stocks, ETFs, and forex.

## What It Does

Every 15 minutes, the system:

1. Fetches price data from Yahoo Finance across 4 asset types
2. Calculates RSI and EMA indicators for each asset
3. Generates signals based on market conditions
4. Sends email notifications for strong signals (>70/100 confidence)

## MVP Asset Coverage

Diversified across 4 major asset classes:

- **Crypto**: BTC-USD (Bitcoin)
- **Stocks**: AAPL (Apple)
- **ETF**: IVV (iShares Core S&P 500)
- **Forex**: BRL=X (Brazilian Real / US Dollar)

## Tech Stack

- **Frontend**: Next.js 15 + TypeScript + TailwindCSS (deployed on Vercel)
- **Backend**: FastAPI + Python 3.11
- **Database**: Supabase (PostgreSQL)
- **Pipeline**: Prefect for orchestration
- **Email**: Resend API
- **Analytics**: PostHog

## Project Structure

```zsh
signals/
├── frontend/           # Next.js application
├── backend/            # FastAPI server
├── data/               # Indicators and signal logic
├── pipe/               # Prefect flows (data pipeline)
├── db/                 # Database schemas and migrations
├── scripts/            # Utility scripts
└── docs/               # Documentation
    ├── MVP.md          # Project scope and goals
    ├── ARCHITECTURE.md # System design
    └── DATA-SCIENCE.md # Indicators explained
```

## Quick Setup (Local Development)

**Get running in 5 minutes:**

```bash
# 1. Database (Docker)
docker-compose up -d
export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"

# 2. Schema & Historical Data (~60 days of 15m bars)
python scripts/setup_db.py
python scripts/seed_historical_data.py

# 3. Backend API
cd backend && uvicorn main:app --reload  # http://localhost:8000

# 4. Frontend
cd frontend && bun run dev  # http://localhost:3000

# 5. Test Pipeline (optional)
cd pipe && python -m flows.signal_generation  # Run once
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

**Option A: Local (Docker)**

```bash
# Start PostgreSQL
docker-compose up -d

# Set connection string
export DATABASE_URL="postgresql://signals_user:signals_password@localhost:5432/trading_signals"

# Initialize schema and seed 4 assets
python scripts/setup_db.py

# Backfill ~60 days of historical data
python scripts/seed_historical_data.py
```

**Option B: Production (Supabase)**

```bash
# Create project at https://supabase.com
# Copy connection string from Settings → Database

export DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"

# Initialize schema and seed
python scripts/setup_db.py
python scripts/seed_historical_data.py
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run the API
uvicorn main:app --reload
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
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with DATABASE_URL and RESEND_API_KEY

# Test the flow locally (runs once)
python -m flows.signal_generation

# Deploy to Prefect Cloud (runs every 15 min)
prefect cloud login
python schedules.py
```

**Simple approach:** One flow (`generate_signals_flow`) with 4 tasks (fetch → calculate → generate → notify). See [`pipe/README.md`](pipe/README.md) for details.

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
POSTHOG_API_KEY=phc_...
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=phc_...
```

## Development Workflow

### Run Everything Locally

```bash
# Terminal 1: Backend
cd backend && uvicorn main:app --reload

# Terminal 2: Frontend
cd frontend && bun run dev

# Terminal 3: Prefect (optional for testing)
cd prefect && python flows/generate_signals.py
```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
bun test
```

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

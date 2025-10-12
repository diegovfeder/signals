# Trading Signals MVP

Automated trading signals for Bitcoin and Ethereum. Get email alerts when technical indicators detect high-confidence opportunities.

## What It Does

Every 15 minutes, the system:

1. Fetches BTC-USD and ETH-USD price data from Yahoo Finance
2. Calculates RSI and EMA indicators
3. Generates signals based on market conditions
4. Sends email notifications for strong signals (>70/100 confidence)

## Tech Stack

- **Frontend**: Next.js 15 + TypeScript + TailwindCSS (deployed on Vercel)
- **Backend**: FastAPI + Python 3.11 (deployed on Vercel)
- **Database**: Supabase (PostgreSQL)
- **Pipeline**: Prefect for orchestration
- **Email**: Resend API
- **Analytics**: PostHog

## Project Structure

```zsh
signals/
├── frontend/          # Next.js application
├── backend/           # FastAPI server
├── data_science/      # Indicators and signal logic
├── prefect/           # Prefect flows (data pipeline)
├── database/          # Database schemas and migrations
├── scripts/           # Utility scripts
└── docs/              # Documentation
    ├── MVP.md         # Project scope and goals
    ├── ARCHITECTURE.md # System design
    └── DATA-SCIENCE.md # Indicators explained
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- Supabase account
- Resend API key

### 1. Database Setup

```bash
# Create a Supabase project at https://supabase.com
# Copy your connection string

# Run migrations
cd database
psql $DATABASE_URL -f schema.sql
psql $DATABASE_URL -f seeds.sql
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
npm install

# Create .env.local file
cp .env.example .env.local
# Edit .env.local with API URL

# Run the dev server
npm run dev
# App available at http://localhost:3000
```

### 4. Pipeline Setup

```bash
cd prefect
pip install -r requirements.txt

# Configure Prefect
prefect cloud login

# Deploy the flow
python flows/generate_signals.py
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://...
RESEND_API_KEY=re_...
YAHOO_FINANCE_API_KEY=optional
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
cd frontend && npm run dev

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
npm test
```

## Documentation

- **[MVP.md](docs/MVP.md)** - What we're building and why
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and data flow
- **[DATA-SCIENCE.md](docs/DATA-SCIENCE.md)** - Indicators and signal logic

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

- BTC-USD and ETH-USD only
- RSI and EMA indicators
- Email notifications
- Public dashboard

**Out of Scope (Phase 2):**

- More cryptocurrencies
- Additional indicators (MACD, Bollinger Bands)
- User authentication
- Telegram notifications
- Portfolio tracking

## Success Metrics

- 100 email signups in 30 days
- >20% activation rate (users who click a signal within 7 days)
- <5% unsubscribe rate
- >95% data pipeline reliability

## License

MIT

## Contributing

This is an MVP project. Contributions welcome after initial launch.

## Support

For questions or issues, open a GitHub issue.

# Local Development Setup

Complete guide to set up the Trading Signals MVP on your local machine.

## Prerequisites

- **Node.js 18+** - [Download](https://nodejs.org/)
- **Python 3.11+** - [Download](https://www.python.org/)
- **PostgreSQL 15** - via Docker or local installation
- **Git** - [Download](https://git-scm.com/)

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/diegovfeder/trading-signals-mvp.git
cd trading-signals-mvp
```

### 2. Start Database (Docker)

```bash
docker-compose up -d
```

This starts PostgreSQL on `localhost:5432` with:

- Database: `trading_signals`
- User: `signals_user`
- Password: `signals_password`

### 3. Set Up Database Schema

```bash
python scripts/setup_db.py
```

This creates all tables and seeds the 3 symbols (BTC-USD, ETH-USD, TSLA).

### 4. Backfill Historical Data

```bash
pip install yfinance psycopg2-binary
python scripts/seed_historical_data.py
```

This fetches the last 30 days of market data from Yahoo Finance.

### 5. Start Backend API

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your DATABASE_URL if needed
uvicorn api.main:app --reload --port 8000
```

API will be available at `http://localhost:8000`

### 6. Start Frontend

```bash
cd frontend
npm install
cp .env.local.example .env.local
# Edit .env.local with your API URL
npm run dev
```

Frontend will be available at `http://localhost:3000`

### 7. Set Up Prefect (Optional)

```bash
cd prefect
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Test a flow manually
python -m flows.market_data_ingestion
```

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=postgresql://signals_user:signals_password@localhost:5432/trading_signals
RESEND_API_KEY=re_xxxxxxxxxxxxx  # Get from resend.com
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=phc_xxxxxxxxxxxxx  # Get from posthog.com
```

### Prefect (.env)

```env
DATABASE_URL=postgresql://signals_user:signals_password@localhost:5432/trading_signals
RESEND_API_KEY=re_xxxxxxxxxxxxx
PREFECT_API_KEY=pnu_xxxxxxxxxxxxx  # Get from prefect.io (optional)
```

## Development Workflow

### Running All Services

You'll need 3 terminal windows:

**Terminal 1 - Backend:**

```bash
cd backend
source venv/bin/activate
uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm run dev
```

**Terminal 3 - Prefect (manual testing):**

```bash
cd prefect
source venv/bin/activate
python -m flows.market_data_ingestion
```

### Testing API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Get all signals
curl http://localhost:8000/api/signals

# Get signal for specific symbol
curl http://localhost:8000/api/signals/BTC-USD

# Subscribe email
curl -X POST http://localhost:8000/api/subscribe \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

## Troubleshooting

### Database Connection Errors

```bash
# Check if PostgreSQL is running
docker ps

# Restart PostgreSQL
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Port Already in Use

```bash
# Find process using port 8000 (backend)
lsof -ti:8000 | xargs kill -9

# Find process using port 3000 (frontend)
lsof -ti:3000 | xargs kill -9
```

### Missing Python Packages

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Frontend Build Errors

```bash
rm -rf node_modules
rm package-lock.json
npm install
```

## Next Steps

1. Implement indicator calculations in `data_science/`
2. Implement API endpoint logic in `backend/api/routers/`
3. Implement Prefect flow logic in `prefect/flows/`
4. Implement frontend components in `frontend/src/components/`

See README.md for the full 4-week implementation plan.

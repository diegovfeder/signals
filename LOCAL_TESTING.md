# Local Testing Guide for WSL Kali Linux

This guide will help you test the Signals project locally on WSL Kali Linux.

## Prerequisites

Before starting, ensure you have:
- **Docker Desktop** with WSL integration enabled
- **Python 3.12+** (check with `python3 --version`)
- **uv** package manager (install: `curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **bun** JavaScript runtime (install: `curl -fsSL https://bun.sh/install | bash`)

## Quick Setup (Automated)

Run the automated setup script:

```bash
chmod +x test-local.sh
./test-local.sh
```

This will:
1. Check prerequisites
2. Start PostgreSQL database
3. Create environment files
4. Install backend and frontend dependencies

## Manual Setup (Step by Step)

### Step 1: Start the Database

```bash
# From project root
docker-compose up -d

# Verify database is running
docker ps | grep signals-db

# Wait a few seconds for database to initialize
sleep 5
```

The database will automatically:
- Create the schema from `db/schema.sql`
- Seed initial symbols (AAPL, BTC-USD) from `db/seeds/symbols.sql`

**Database credentials:**
- Host: `localhost:5432`
- User: `quantmaster`
- Password: `buysthedip`
- Database: `signals`

### Step 2: Configure Backend

The `.env` file has been created with:
```env
DATABASE_URL=postgresql+psycopg://quantmaster:buysthedip@localhost:5432/signals
RESEND_API_KEY=
RESEND_FROM_EMAIL="Signals Bot <onboarding@resend.dev>"
APP_BASE_URL=http://localhost:3000
ENVIRONMENT=development
```

**Note:** `RESEND_API_KEY` is optional for local testing (email features won't work without it).

Install backend dependencies:
```bash
cd backend
uv sync
cd ..
```

### Step 3: Configure Frontend

The `.env.local` file has been created with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=
```

Install frontend dependencies:
```bash
cd frontend
bun install
cd ..
```

### Step 4: Start the Services

**Terminal 1 - Backend API:**
```bash
cd backend
uv run uvicorn api.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/api/docs
- Health: http://localhost:8000/health

**Terminal 2 - Frontend:**
```bash
cd frontend
bun run dev
```

The frontend will be available at:
- http://localhost:3000

## Testing the Setup

### 1. Test Database Connection

```bash
# Check if database is accessible
docker exec signals-db psql -U quantmaster -d signals -c "SELECT COUNT(*) FROM symbols;"
```

Expected output: `2` (AAPL and BTC-USD)

### 2. Test Backend API

```bash
# Health check
curl http://localhost:8000/health

# Expected: {"status":"healthy","database":"connected"}

# Get signals (may be empty if no data yet)
curl http://localhost:8000/api/signals/

# Get market data (may be empty)
curl http://localhost:8000/api/market-data/AAPL/ohlcv
```

### 3. Test Frontend

Open http://localhost:3000 in your browser. You should see:
- Landing page
- Signals dashboard (may be empty if no signals generated yet)
- Navigation to `/signals/[symbol]` pages

### 4. (Optional) Seed Market Data

To generate actual signals, you need market data. Run the pipeline flows:

```bash
# Install pipe dependencies first
cd pipe
uv sync
cd ..

# Fetch market data
uv run --directory pipe python -m pipe.flows.market_data_sync --symbols AAPL,BTC-USD

# Calculate indicators and generate signals
uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD
```

After running these, refresh the frontend to see signals!

## Troubleshooting

### Docker Issues

**"Docker not found" or "Cannot connect to Docker daemon":**
- Ensure Docker Desktop is running on Windows
- Enable WSL integration in Docker Desktop settings:
  - Settings → Resources → WSL Integration
  - Enable integration for your Kali Linux distro

**"Port 5432 already in use":**
```bash
# Check what's using the port
sudo lsof -i :5432

# Or stop existing PostgreSQL if running
sudo systemctl stop postgresql
```

### Backend Issues

**"Module not found" errors:**
```bash
cd backend
uv sync  # Reinstall dependencies
```

**"Database connection failed":**
- Verify Docker container is running: `docker ps | grep signals-db`
- Check DATABASE_URL in `backend/.env`
- Test connection: `docker exec signals-db pg_isready -U quantmaster -d signals`

### Frontend Issues

**"Cannot find module" errors:**
```bash
cd frontend
bun install  # Reinstall dependencies
```

**"API connection failed":**
- Verify backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` in `frontend/.env.local`
- Test: `curl http://localhost:8000/health`

### Database Issues

**"Relation does not exist" errors:**
The schema should auto-initialize when the container starts. If not:

```bash
# Check if schema was applied
docker exec signals-db psql -U quantmaster -d signals -c "\dt"

# If empty, manually apply schema
docker exec -i signals-db psql -U quantmaster -d signals < db/schema.sql
docker exec -i signals-db psql -U quantmaster -d signals < db/seeds/symbols.sql
```

## Next Steps

Once everything is running:

1. **Explore the API docs**: http://localhost:8000/api/docs
2. **View signals dashboard**: http://localhost:3000
3. **Check admin pages**: http://localhost:3000/admin
4. **Test subscription flow**: http://localhost:3000/subscribe

## Stopping Services

```bash
# Stop frontend: Ctrl+C in frontend terminal
# Stop backend: Ctrl+C in backend terminal
# Stop database:
docker-compose down

# To remove database data:
docker-compose down -v
```

## Useful Commands

```bash
# View database logs
docker logs signals-db

# Access database shell
docker exec -it signals-db psql -U quantmaster -d signals

# Check database tables
docker exec signals-db psql -U quantmaster -d signals -c "\dt"

# View signals in database
docker exec signals-db psql -U quantmaster -d signals -c "SELECT * FROM signals ORDER BY timestamp DESC LIMIT 5;"
```


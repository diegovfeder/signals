# Quick Start - Local Testing (WSL Kali Linux)

## 🚀 Fastest Way to Get Started

### Option 1: Automated Setup (Recommended)

Open WSL terminal and run:

```bash
cd ~/signals
chmod +x test-local.sh
./test-local.sh
```

This will set everything up automatically!

### Option 2: Manual Setup

Follow these steps in order:

#### 1. Start Database

```bash
cd ~/signals
docker-compose up -d
```

Wait ~10 seconds for database to initialize, then verify:
```bash
docker ps | grep signals-db
```

#### 2. Create Environment Files

**Backend** (`backend/.env`):
```bash
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql+psycopg://quantmaster:buysthedip@localhost:5432/signals
RESEND_API_KEY=
RESEND_FROM_EMAIL="Signals Bot <onboarding@resend.dev>"
APP_BASE_URL=http://localhost:3000
ENVIRONMENT=development
EOF
```

**Frontend** (`frontend/.env.local`):
```bash
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=
EOF
```

#### 3. Install Dependencies

**Backend:**
```bash
cd backend
uv sync
cd ..
```

**Frontend:**
```bash
cd frontend
bun install
cd ..
```

#### 4. Start Services

**Terminal 1 - Backend:**
```bash
cd backend
uv run uvicorn api.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
bun run dev
```

#### 5. Test It!

- **Backend API**: http://localhost:8000/health
- **API Docs**: http://localhost:8000/api/docs
- **Frontend**: http://localhost:3000

## ✅ Verification Checklist

- [ ] Database running: `docker ps | grep signals-db`
- [ ] Backend health: `curl http://localhost:8000/health` returns `{"status":"healthy"}`
- [ ] Frontend loads: http://localhost:3000 shows the landing page
- [ ] API docs work: http://localhost:8000/api/docs loads

## 🐛 Common Issues

**Docker not found:**
- Open Docker Desktop on Windows
- Settings → Resources → WSL Integration → Enable for Kali Linux

**Port 5432 in use:**
```bash
sudo lsof -i :5432  # See what's using it
# Or stop local postgres: sudo systemctl stop postgresql
```

**Backend won't start:**
```bash
cd backend
uv sync  # Reinstall deps
```

**Frontend won't start:**
```bash
cd frontend
bun install  # Reinstall deps
```

## 📚 More Details

See [LOCAL_TESTING.md](./LOCAL_TESTING.md) for detailed troubleshooting and advanced setup.


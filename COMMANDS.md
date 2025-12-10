# Commands to Run in WSL Kali Linux Terminal

Copy and paste these commands **one by one** into your WSL terminal, or run the automated script.

## Option 1: Automated (Recommended)

```bash
cd ~/signals
chmod +x setup-and-start.sh
./setup-and-start.sh
```

This does everything automatically. Skip to the "Test It" section below.

---

## Option 2: Manual Step-by-Step

### Step 1: Navigate to Project
```bash
cd ~/signals
```

### Step 2: Make Scripts Executable
```bash
chmod +x test-local.sh setup-and-start.sh start-servers.sh
```

### Step 3: Start Database
```bash
docker-compose up -d
```

Wait ~10 seconds, then verify:
```bash
docker ps | grep signals-db
```

### Step 4: Create Backend Environment File
```bash
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql+psycopg://quantmaster:buysthedip@localhost:5432/signals
RESEND_API_KEY=
RESEND_FROM_EMAIL="Signals Bot <onboarding@resend.dev>"
APP_BASE_URL=http://localhost:3000
ENVIRONMENT=development
EOF
```

### Step 5: Create Frontend Environment File
```bash
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_POSTHOG_KEY=
EOF
```

### Step 6: Install Backend Dependencies
```bash
cd backend
uv sync
cd ..
```

### Step 7: Install Frontend Dependencies
```bash
cd frontend
bun install
cd ..
```

### Step 8: Start Backend Server (Terminal 1)
```bash
cd backend
uv run uvicorn api.main:app --reload --port 8000
```

**Keep this terminal open!** The backend will run here.

### Step 9: Start Frontend Server (New Terminal 2)
Open a **new terminal** and run:
```bash
cd ~/signals/frontend
bun run dev
```

**Keep this terminal open too!** The frontend will run here.

---

## Test It!

Once both servers are running:

### Test Backend Health
In a **third terminal**, run:
```bash
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"healthy","database":"connected"}
```

### Open in Browser

- **Frontend**: http://localhost:3000
- **Backend API Docs**: http://localhost:8000/api/docs
- **Backend Health**: http://localhost:8000/health

---

## Quick Commands Reference

### Check if servers are running:
```bash
# Check backend
curl http://localhost:8000/health

# Check frontend (should return HTML)
curl http://localhost:3000

# Check what's using the ports
lsof -i :8000
lsof -i :3000
```

### Stop servers:
```bash
# Stop backend (Ctrl+C in backend terminal)
# Stop frontend (Ctrl+C in frontend terminal)

# Or kill by port:
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### View database:
```bash
# Check database is running
docker ps | grep signals-db

# Access database shell
docker exec -it signals-db psql -U quantmaster -d signals

# View symbols
docker exec signals-db psql -U quantmaster -d signals -c "SELECT * FROM symbols;"
```

### View logs:
If you ran servers in background with the script:
```bash
tail -f backend.log
tail -f frontend.log
```

---

## Troubleshooting

### Docker not found:
```bash
# Check if Docker Desktop is running on Windows
# Enable WSL integration in Docker Desktop settings
```

### Port already in use:
```bash
# Kill processes on ports
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Backend won't start:
```bash
cd backend
uv sync  # Reinstall dependencies
```

### Frontend won't start:
```bash
cd frontend
bun install  # Reinstall dependencies
```

### Database connection error:
```bash
# Restart database
docker-compose down
docker-compose up -d

# Wait 10 seconds, then test
docker exec signals-db pg_isready -U quantmaster -d signals
```





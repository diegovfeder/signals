# FastAPI Backend

REST API for serving our trading-signals, market data, and managing email subscriptions.

## Quick Start

### Local Development

```bash
cd backend

# Install dependencies
uv sync

# Create .env file
cp .env.example .env
# Edit .env with:
#   DATABASE_URL=postgresql://user:pass@localhost:5432/trading_signals
#   RESEND_API_KEY=re_...

# Run the server
uv run uvicorn api.main:app --reload --port 8000

# API available at http://localhost:8000
# Docs at http://localhost:8000/api/docs
```

### Test the API

```bash
# Health check
curl http://localhost:8000/health

# Get all signals
curl http://localhost:8000/api/signals/

# Get signal for specific symbol
curl http://localhost:8000/api/signals/BTC-USD
```

## Project Structure

```bash
backend/
├── api/
│   ├── main.py              # FastAPI app, CORS, routing
│   ├── config.py            # Settings (env vars)
│   ├── database.py          # DB connection, session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic request/response models
│   └── routers/
│       ├── signals.py       # GET /api/signals endpoints
│       ├── market_data.py   # GET /api/market-data endpoints
│       └── subscribe.py     # POST /api/subscribe endpoints
├── pyproject.toml          # Dependencies and project metadata
├── vercel.json             # Vercel deployment config
└── README.md               # This file
```

## API Endpoints

### Health & Status

```http
GET /              # Root health check
GET /health        # Detailed health (includes DB connection)
```

### Signals

```http
GET /api/signals/                # List all signals (with filters)
GET /api/signals/{symbol}        # Latest signal for symbol
GET /api/signals/{symbol}/history # Historical signals
```

**Query Parameters:**

- `limit` (int): Max results (default: 20, max: 100)
- `offset` (int): Pagination offset
- `signal_type` (str): Filter by BUY/SELL/HOLD
- `min_strength` (float): Minimum strength (0-100)

### Market Data

```http
GET /api/market-data/{symbol}/ohlcv       # OHLCV bars
GET /api/market-data/{symbol}/indicators  # Calculated indicators
```

### Email Subscriptions

```http
POST /api/subscribe/                    # Subscribe email
POST /api/subscribe/unsubscribe/{token} # Unsubscribe via token
```

## Interactive Docs

FastAPI auto-generates interactive documentation:

- **Swagger UI**: <http://localhost:8000/api/docs>
- **ReDoc**: <http://localhost:8000/api/redoc>

Try endpoints directly in your browser!

## Implementation Checklist

### Core Endpoints (MVP)

**Signals:**

- [ ] `GET /api/signals/` - Fetch from `signals` table with filters
- [ ] `GET /api/signals/{symbol}` - Latest signal per symbol
- [ ] `GET /api/signals/{symbol}/history` - Historical signals

**Market Data:**

- [ ] `GET /api/market-data/{symbol}/ohlcv` - Fetch from `market_data` table
- [ ] `GET /api/market-data/{symbol}/indicators` - Fetch from `indicators` table

**Subscriptions:**

- [ ] `POST /api/subscribe/` - Create subscriber with double opt-in
- [ ] `POST /api/subscribe/unsubscribe/{token}` - Mark as unsubscribed

### Database Integration

**SQLAlchemy Models** (`api/models.py`):

```python
class Signal(Base):
    __tablename__ = "signals"
    id = Column(UUID, primary_key=True)
    symbol = Column(String)
    timestamp = Column(DateTime)
    signal_type = Column(String)  # BUY, SELL, HOLD
    strength = Column(Float)
    reasoning = Column(ARRAY(String))
    price_at_signal = Column(Float)
```

**Pydantic Schemas** (`api/schemas.py`):

```python
class SignalResponse(BaseModel):
    id: str
    symbol: str
    timestamp: datetime
    signal_type: str
    strength: float
    reasoning: List[str]
    price_at_signal: float
    
    class Config:
        from_attributes = True  # For SQLAlchemy compatibility
```

### Query Examples

**Get all signals with filters:**

```python
@router.get("/", response_model=SignalListResponse)
async def get_all_signals(
    limit: int = 20,
    min_strength: float = None,
    db: Session = Depends(get_db)
):
    query = db.query(Signal)
    
    if min_strength:
        query = query.filter(Signal.strength >= min_strength)
    
    signals = query.order_by(Signal.timestamp.desc()).limit(limit).all()
    return {"signals": signals, "total": len(signals)}
```

**Get latest signal per symbol:**

```python
@router.get("/{symbol}")
async def get_signal_by_symbol(symbol: str, db: Session = Depends(get_db)):
    signal = db.query(Signal)\
        .filter(Signal.symbol == symbol)\
        .order_by(Signal.timestamp.desc())\
        .first()
    
    if not signal:
        raise HTTPException(status_code=404, detail=f"No signals found for {symbol}")
    
    return signal
```

## Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/trading_signals

# Email (Resend)
RESEND_API_KEY=re_...

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app

# Optional
DEBUG=True
LOG_LEVEL=INFO
```

## Testing

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio httpx

# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=api tests/
```

### Example Test

```python
# tests/test_signals.py
from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

def test_get_all_signals():
    response = client.get("/api/signals/")
    assert response.status_code == 200
    assert "signals" in response.json()

def test_get_signal_by_symbol():
    response = client.get("/api/signals/BTC-USD")
    assert response.status_code in [200, 404]  # 404 if no signals yet
```

## Deployment

### Vercel (Serverless)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
cd backend
vercel deploy

# Set environment variables in Vercel dashboard
```

`vercel.json` already configured for serverless deployment.

### Docker (Alternative)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml .
COPY api/ ./api/

# Install dependencies
RUN uv sync --frozen

CMD ["uv", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t signals-api .
docker run -p 8000:8000 --env-file .env signals-api
```

## Error Handling

### Standard Error Responses

```python
# 400 - Bad Request
{"detail": "Invalid parameter: min_strength must be between 0 and 100"}

# 404 - Not Found
{"detail": "Signal not found for symbol: BTC-USD"}

# 422 - Validation Error
{"detail": [{"loc": ["body", "email"], "msg": "invalid email format"}]}

# 500 - Internal Server Error
{"detail": "Database connection failed"}

# 501 - Not Implemented
{"detail": "Not yet implemented"}
```

### Custom Exception Handling

```python
from fastapi import HTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )
```

## CORS Configuration

In production, restrict CORS to your frontend domain:

```python
# api/config.py
class Settings(BaseSettings):
    CORS_ORIGINS: list = ["https://your-frontend.vercel.app"]
```

For development, allow localhost:

```python
CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:3001"]
```

## Logging

Use Python's logging module:

```python
import logging

logger = logging.getLogger(__name__)

@router.get("/api/signals/{symbol}")
async def get_signal(symbol: str):
    logger.info(f"Fetching signal for {symbol}")
    # ... implementation
```

Configure in `main.py`:

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

## Troubleshooting

**"uvicorn: command not found":**

```bash
uv add uvicorn
# or
uv run uvicorn api.main:app --reload
```

**Database connection error:**

```bash
# Check DATABASE_URL format
postgresql://user:password@host:port/database

# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

**CORS errors in browser:**

```python
# Add your frontend URL to CORS_ORIGINS in .env
CORS_ORIGINS=http://localhost:3000
```

**Import errors:**

```bash
# Make sure you're in the backend directory
cd backend
uv run uvicorn api.main:app --reload
```

## Next Steps

1. Implement signal endpoints (connect to `signals` table)
2. Implement market data endpoints (connect to `market_data`, `indicators` tables)
3. Implement subscription endpoints (double opt-in flow with Resend)
4. Add request validation and error handling
5. Write tests for all endpoints
6. Deploy to Vercel or Docker

**See also:**

- `db/README.md` for database schema
- `pipe/README.md` for data pipeline (populates the DB)
- `docs/DATA-SCIENCE.md` for indicator calculations

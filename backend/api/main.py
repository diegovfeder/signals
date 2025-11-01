"""
Trading Signals API

FastAPI application for serving trading signals, market data, and email subscriptions.
"""

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from .config import settings
from .database import get_db
from .routers import signals, market_data, subscribe, backtests

# Create FastAPI app
app = FastAPI(
    title="Signals API — Market insights made human",
    description=(
        "The Signals API delivers automated trading insights derived from RSI and EMA indicators. "
        "Currently supports AAPL and BTC-USD, with plans to expand into ETFs and forex. "
        "Signals refresh daily at 10 PM UTC, each including both a confidence score (0–100) "
        "and a plain-English summary of the market condition.\n\n"
        "Designed for professionals who value clarity and transparency in data—no hype, no noise."
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware - allow localhost + all Vercel deployments
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Match all Vercel deployments
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market-data"])
app.include_router(subscribe.router, prefix="/api/subscribe", tags=["subscribe"])
app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Trading Signals API",
        "version": "0.1.0"
    }


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Serve favicon from public directory."""
    # Vercel automatically serves files from public/** via CDN
    return RedirectResponse("/favicon.ico", status_code=307)


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Detailed health check including database connection."""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": str(e)
        }

"""
Trading Signals API

FastAPI application for serving trading signals, market data, and email subscriptions.
"""

import logging
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from .config import settings
from .database import get_db
from .routers import signals, market_data, subscribe, backtests

# Configure logging
logger = logging.getLogger(__name__)

# Initialize rate limiter (per IP)
limiter = Limiter(key_func=get_remote_address)

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

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - allow localhost + all Vercel deployments (production-ready security)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Match all Vercel deployments
    allow_credentials=False,  # API is stateless (no cookies/sessions)
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],  # OPTIONS required for CORS preflight
    allow_headers=[
        "Content-Type",
        "Authorization",
        "Accept",
        "Accept-Language",
        "Content-Language",
    ],  # Standard headers browsers may send
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


# Include routers
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market-data"])
app.include_router(subscribe.router, prefix="/api/subscribe", tags=["subscribe"])
app.include_router(backtests.router, prefix="/api/backtests", tags=["backtests"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "message": "Trading Signals API", "version": "0.1.0"}


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
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        # Log full error internally
        logger.error(f"Health check failed: {e}", exc_info=True)
        # Return generic error to API (don't leak connection details)
        return {
            "status": "degraded",
            "database": "disconnected",
            "error": "Database connection failed",
        }

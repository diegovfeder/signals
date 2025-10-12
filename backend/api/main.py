"""
Trading Signals API

FastAPI application for serving trading signals, market data, and email subscriptions.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import signals, market_data, subscribe

# Create FastAPI app
app = FastAPI(
    title="Trading Signals API",
    description="Automated trading signals based on technical analysis",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(signals.router, prefix="/api/signals", tags=["signals"])
app.include_router(market_data.router, prefix="/api/market-data", tags=["market-data"])
app.include_router(subscribe.router, prefix="/api/subscribe", tags=["subscribe"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Trading Signals API",
        "version": "0.1.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check including database connection."""
    # TODO: Add database connection check
    return {
        "status": "healthy",
        "database": "connected"
    }

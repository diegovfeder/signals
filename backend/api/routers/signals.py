"""
Signals Router

Endpoints for fetching trading signals.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
from ..database import get_db
from ..models import Signal
from ..schemas import SignalResponse, SignalListResponse

router = APIRouter()


@router.get("/", response_model=SignalListResponse)
async def get_all_signals(
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    signal_type: Optional[str] = Query(default=None, regex="^(BUY|SELL|HOLD)$"),
    min_strength: Optional[float] = Query(default=None, ge=0, le=100),
    db: Session = Depends(get_db)
):
    """
    Get all signals with optional filtering.

    Query Parameters:
        - limit: Maximum number of signals to return (default: 20, max: 100)
        - offset: Number of signals to skip (for pagination)
        - signal_type: Filter by signal type (BUY, SELL, HOLD)
        - min_strength: Minimum signal strength (0-100)

    Returns:
        List of signals with total count
    """
    # Build query with filters
    query = db.query(Signal)
    
    if signal_type:
        query = query.filter(Signal.signal_type == signal_type)
    
    if min_strength is not None:
        query = query.filter(Signal.strength >= min_strength)
    
    # Get total count before pagination
    total = query.count()
    
    # Apply ordering and pagination
    signals = query.order_by(Signal.timestamp.desc()).limit(limit).offset(offset).all()

    # Convert ORM models to Pydantic schemas
    signal_responses = [SignalResponse.model_validate(signal) for signal in signals]

    return SignalListResponse(signals=signal_responses, total=total)


@router.get("/{symbol}", response_model=SignalResponse)
async def get_signal_by_symbol(
    symbol: str,
    db: Session = Depends(get_db)
):
    """
    Get the latest signal for a specific symbol.

    Path Parameters:
        - symbol: Asset symbol (e.g., 'BTC-USD', 'ETH-USD', 'TSLA')

    Returns:
        Most recent signal for the symbol
    """
    # Query signals table for symbol
    signal = db.query(Signal)\
        .filter(Signal.symbol == symbol)\
        .order_by(Signal.timestamp.desc())\
        .first()

    if not signal:
        raise HTTPException(
            status_code=404,
            detail=f"No signals found for symbol: {symbol}"
        )
    
    return signal


@router.get("/{symbol}/history", response_model=SignalListResponse)
async def get_signal_history(
    symbol: str,
    days: int = Query(default=30, le=90),
    db: Session = Depends(get_db)
):
    """
    Get signal history for a specific symbol.

    Path Parameters:
        - symbol: Asset symbol

    Query Parameters:
        - days: Number of days of history (default: 30, max: 90)

    Returns:
        Historical signals for the symbol
    """
    # Calculate cutoff date
    cutoff = datetime.now() - timedelta(days=days)
    
    # Query signals for symbol within date range
    signals = db.query(Signal)\
        .filter(Signal.symbol == symbol, Signal.timestamp >= cutoff)\
        .order_by(Signal.timestamp.desc())\
        .all()

    # Convert ORM models to Pydantic schemas
    signal_responses = [SignalResponse.model_validate(signal) for signal in signals]

    return SignalListResponse(signals=signal_responses, total=len(signals))

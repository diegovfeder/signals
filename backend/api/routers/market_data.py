"""
Market Data Router

Endpoints for fetching OHLCV market data and indicators.
"""

from datetime import datetime, timedelta, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Indicator, MarketData
from ..schemas import IndicatorResponse, MarketDataResponse

router = APIRouter()

RANGE_TO_DAYS = {
    "1d": 1,
    "1w": 7,
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
    "2y": 365 * 2,
}


def _resolve_range_days(range_label: Optional[str]) -> Optional[int]:
    if not range_label:
        return None
    normalized = range_label.lower()
    days = RANGE_TO_DAYS.get(normalized)
    if not days:
        valid = ", ".join(RANGE_TO_DAYS.keys())
        raise HTTPException(status_code=400, detail=f"Invalid range '{range_label}'. Valid options: {valid}")
    return days


@router.get("/{symbol}/ohlcv", response_model=List[MarketDataResponse])
async def get_market_data(
    symbol: str,
    limit: int = Query(default=100, ge=1, le=5000),
    range: Optional[str] = Query(
        default=None,
        description="Optional time range (1d, 1w, 1m, 3m, 6m, 1y, 2y). When provided, results are filtered to this window.",
    ),
    db: Session = Depends(get_db),
):
    """
    Get OHLCV market data for a symbol.

    Path Parameters:
        - symbol: Asset symbol (e.g., 'BTC-USD')

    Query Parameters:
        - limit: Maximum number of candles to return (default: 100)
        - range: Optional named range to filter by recency

    Returns:
        List of OHLCV data points (most recent first)
    """
    range_days = _resolve_range_days(range)
    capped_limit = min(limit, 5000 if range_days else 500)

    query = db.query(MarketData).filter(MarketData.symbol == symbol)
    if range_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=range_days)
        query = query.filter(MarketData.timestamp >= cutoff)

    data = (
        query.order_by(MarketData.timestamp.desc())
        .limit(capped_limit)
        .all()
    )

    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No market data found for symbol: {symbol}",
        )

    return data


@router.get("/{symbol}/indicators", response_model=List[IndicatorResponse])
async def get_indicators(
    symbol: str,
    limit: int = Query(default=100, ge=1, le=5000),
    range: Optional[str] = Query(
        default=None,
        description="Optional time range (1d, 1w, 1m, 3m, 6m, 1y, 2y).",
    ),
    db: Session = Depends(get_db),
):
    """
    Get calculated indicators for a symbol.

    Path Parameters:
        - symbol: Asset symbol

    Query Parameters:
        - limit: Maximum number of indicator data points to return
        - range: Optional named range filter

    Returns:
        List of indicator values (RSI, EMA, MACD) over time
    """
    range_days = _resolve_range_days(range)
    capped_limit = min(limit, 5000 if range_days else 500)

    query = db.query(Indicator).filter(Indicator.symbol == symbol)
    if range_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=range_days)
        query = query.filter(Indicator.timestamp >= cutoff)

    indicators = (
        query.order_by(Indicator.timestamp.desc())
        .limit(capped_limit)
        .all()
    )

    if not indicators:
        raise HTTPException(
            status_code=404,
            detail=f"No indicators found for symbol: {symbol}",
        )

    return indicators

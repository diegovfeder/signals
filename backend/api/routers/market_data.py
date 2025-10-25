"""
Market Data Router

Endpoints for fetching OHLCV market data and indicators.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..models import MarketData, Indicator
from ..schemas import MarketDataResponse, IndicatorResponse

router = APIRouter()


@router.get("/{symbol}/ohlcv", response_model=List[MarketDataResponse])
async def get_market_data(
    symbol: str,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """
    Get OHLCV market data for a symbol.

    Path Parameters:
        - symbol: Asset symbol (e.g., 'BTC-USD')

    Query Parameters:
        - limit: Number of candles to return (default: 100, max: 500)

    Returns:
        List of OHLCV data points (most recent first)
    """
    # Query market_data table
    data = db.query(MarketData)\
        .filter(MarketData.symbol == symbol)\
        .order_by(MarketData.timestamp.desc())\
        .limit(limit)\
        .all()
    
    if not data:
        raise HTTPException(
            status_code=404,
            detail=f"No market data found for symbol: {symbol}"
        )
    
    return data


@router.get("/{symbol}/indicators", response_model=List[IndicatorResponse])
async def get_indicators(
    symbol: str,
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """
    Get calculated indicators for a symbol.

    Path Parameters:
        - symbol: Asset symbol

    Query Parameters:
        - limit: Number of indicator data points to return

    Returns:
        List of indicator values (RSI, EMA, MACD) over time
    """
    # Query indicators table
    indicators = db.query(Indicator)\
        .filter(Indicator.symbol == symbol)\
        .order_by(Indicator.timestamp.desc())\
        .limit(limit)\
        .all()
    
    if not indicators:
        raise HTTPException(
            status_code=404,
            detail=f"No indicators found for symbol: {symbol}"
        )
    
    return indicators

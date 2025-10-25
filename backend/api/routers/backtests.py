"""
Backtests Router

Temporary stub endpoints for backtest summaries until the pipeline computes real stats.
"""

from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Signal
from ..schemas import BacktestSummaryResponse

router = APIRouter()

BACKTEST_RANGE_CHOICES = {"1m", "3m", "6m", "1y", "3y", "5y"}


def _normalize_range(range_label: str) -> str:
    normalized = range_label.lower()
    if normalized not in BACKTEST_RANGE_CHOICES:
        valid = ", ".join(sorted(BACKTEST_RANGE_CHOICES))
        raise HTTPException(status_code=400, detail=f"Invalid range '{range_label}'. Valid options: {valid}")
    return normalized


@router.get("/{symbol}", response_model=BacktestSummaryResponse)
async def get_backtest_summary(
    symbol: str,
    range: str = Query(default="1y", description="Historical range evaluated for the backtest summary."),
    db: Session = Depends(get_db),
):
    """
    Return a placeholder backtest summary so the frontend can render the section before the full
    backtesting engine ships.
    """
    normalized_range = _normalize_range(range)
    latest_signal = (
        db.query(Signal)
        .filter(Signal.symbol == symbol)
        .order_by(Signal.timestamp.desc())
        .first()
    )

    return BacktestSummaryResponse(
        symbol=symbol,
        range=normalized_range,
        trades=0,
        win_rate=0.0,
        avg_return=0.0,
        total_return=0.0,
        last_trained_at=latest_signal.timestamp if latest_signal else None,
        notes="Backtest engine coming soon – rerun Prefect flows to populate more data.",
    )

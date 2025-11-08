"""Market data tasks: provider orchestration, normalization, and persistence."""

from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta

import polars as pl
from prefect import task

try:
    from ..lib.api import yahoo
except ImportError:
    from lib.api import yahoo

from .db import get_db_conn

# Default symbols for signal generation
DEFAULT_SYMBOLS = ["AAPL", "BTC-USD"]

HISTORICAL_RANGE_MAP: dict[str, int] = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
    "2y": 365 * 2,
    "3y": 365 * 3,
    "5y": 365 * 5,
    "10y": 365 * 10,
    "max": 365 * 20,
}
MAX_BACKFILL_DAYS = HISTORICAL_RANGE_MAP["max"]


def resolve_symbols(explicit: list[str] | None = None) -> list[str]:
    if explicit:
        return explicit
    env_value = os.getenv("SIGNAL_SYMBOLS")
    if env_value:
        candidates = [sym.strip() for sym in env_value.split(",") if sym.strip()]
        if candidates:
            return candidates
    return DEFAULT_SYMBOLS


def resolve_history_days(
    explicit_days: int | None = None, range_label: str | None = None
) -> int | None:
    if explicit_days is not None:
        return max(1, min(explicit_days, MAX_BACKFILL_DAYS))
    if range_label:
        normalized = range_label.lower()
        if normalized not in HISTORICAL_RANGE_MAP:
            raise ValueError(
                f"Unsupported backfill range '{range_label}'. "
                f"Valid options: {', '.join(HISTORICAL_RANGE_MAP.keys())}"
            )
        return HISTORICAL_RANGE_MAP[normalized]

    env_days = os.getenv("BACKFILL_DAYS")
    if env_days:
        try:
            return max(1, min(int(env_days), MAX_BACKFILL_DAYS))
        except ValueError as exc:
            raise ValueError(f"Invalid BACKFILL_DAYS value: {env_days}") from exc

    env_range = os.getenv("BACKFILL_RANGE")
    if env_range:
        normalized = env_range.lower()
        if normalized not in HISTORICAL_RANGE_MAP:
            raise ValueError(
                f"Unsupported BACKFILL_RANGE '{env_range}'. "
                f"Valid options: {', '.join(HISTORICAL_RANGE_MAP.keys())}"
            )
        return HISTORICAL_RANGE_MAP[normalized]
    return None


def _limit_df_to_days(df: pl.DataFrame, range_days: int | None = None) -> pl.DataFrame:
    if not range_days or range_days <= 0 or df.height == 0:
        return df
    cutoff = datetime.now(timezone.utc) - timedelta(days=range_days)
    filtered = df.filter(pl.col("timestamp") >= cutoff)
    return filtered


# Removed _should_fallback_to_yahoo - no longer needed (Yahoo-only approach)


@task(name="fetch-intraday-ohlcv", retries=3, retry_delay_seconds=10)
def fetch_intraday_ohlcv(symbol: str, interval: str = "15m") -> pl.DataFrame:
    # Yahoo Finance doesn't support intraday intervals well, use daily instead
    # For MVP, we use daily data only (fetched at 10 PM UTC)
    return yahoo.fetch_daily(symbol, range_days=1)


@task(name="fetch-historical-ohlcv", retries=3, retry_delay_seconds=30)
def fetch_historical_ohlcv(symbol: str, range_days: int | None = None) -> pl.DataFrame:
    # Use Yahoo Finance directly (Alpha Vantage removed for MVP simplicity)
    df = yahoo.fetch_daily(symbol, range_days)
    limited = _limit_df_to_days(df, range_days)

    # Validate we have sufficient data
    if range_days:
        cutoff = datetime.now(timezone.utc) - timedelta(days=range_days)
        earliest = limited["timestamp"].min() if limited.height > 0 else None
        if earliest is None or earliest > cutoff + timedelta(days=14):
            raise RuntimeError(
                f"Yahoo Finance history incomplete for {symbol}; earliest {earliest} but cutoff {cutoff}"
            )
    return limited


@task(name="upsert-market-data")
def upsert_market_data(df: pl.DataFrame) -> int:
    if df.height == 0:
        return 0

    # Convert polars DataFrame to list of tuples for database insertion
    rows: list[tuple] = [
        (
            str(row["symbol"]),
            row["timestamp"]
            if isinstance(row["timestamp"], datetime)
            else row["timestamp"],
            float(row["open"]),
            float(row["high"]),
            float(row["low"]),
            float(row["close"]),
            int(row["volume"]),
        )
        for row in df.iter_rows(named=True)
    ]

    query = (
        "INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (symbol, timestamp) DO NOTHING"
    )
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.executemany(query, rows)
        conn.commit()
        return len(rows)

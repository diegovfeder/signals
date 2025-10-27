"""Market data tasks: provider orchestration, normalization, and persistence."""

from __future__ import annotations

import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple

import pandas as pd
from prefect import task

from data.sources import alpha_vantage, yahoo
from tasks.db import get_db_conn

HISTORICAL_RANGE_MAP: Dict[str, int] = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
    "2y": 365 * 2,
    "3y": 365 * 3,
    "5y": 365 * 5,
    "max": 365 * 20,
}
MAX_BACKFILL_DAYS = HISTORICAL_RANGE_MAP["max"]


def resolve_symbols(explicit: Optional[List[str]] = None) -> List[str]:
    if explicit:
        return explicit
    env_value = os.getenv("SIGNAL_SYMBOLS")
    if env_value:
        candidates = [sym.strip() for sym in env_value.split(",") if sym.strip()]
        if candidates:
            return candidates
    return alpha_vantage.DEFAULT_SYMBOLS


def resolve_history_days(explicit_days: Optional[int], range_label: Optional[str]) -> Optional[int]:
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


def _limit_df_to_days(df: pd.DataFrame, range_days: Optional[int]) -> pd.DataFrame:
    if not range_days or range_days <= 0 or df.empty:
        return df
    cutoff = pd.Timestamp.now(tz=timezone.utc) - pd.Timedelta(days=range_days)
    filtered = df[df["timestamp"] >= cutoff]
    return filtered.reset_index(drop=True)


def _should_fallback_to_yahoo(exc: Exception) -> bool:
    message = str(exc).lower()
    keywords = [
        "premium endpoint",
        "thank you for using alpha vantage",
        "please visit https://www.alphavantage.co/premium",
        "api call frequency",
        "rate limit",
        "history incomplete",
    ]
    return any(keyword in message for keyword in keywords)


@task(name="fetch-intraday-ohlcv", retries=3, retry_delay_seconds=10)
def fetch_intraday_ohlcv(symbol: str, interval: str = "15m") -> pd.DataFrame:
    return alpha_vantage.fetch_intraday(symbol, interval)


@task(name="fetch-historical-ohlcv", retries=3, retry_delay_seconds=30)
def fetch_historical_ohlcv(symbol: str, range_days: Optional[int] = None) -> pd.DataFrame:
    try:
        df = alpha_vantage.fetch_daily(symbol, range_days)
        limited = _limit_df_to_days(df, range_days)
        if range_days:
            cutoff = pd.Timestamp.now(tz=timezone.utc) - pd.Timedelta(days=range_days)
            earliest = limited["timestamp"].min() if not limited.empty else None
            if earliest is None or earliest > cutoff + pd.Timedelta(days=14):
                raise RuntimeError(
                    f"Alpha Vantage history incomplete for {symbol}; earliest {earliest} but cutoff {cutoff}"
                )
        return limited
    except Exception as exc:
        if _should_fallback_to_yahoo(exc):
            fallback = yahoo.fetch_daily(symbol, range_days)
            return _limit_df_to_days(fallback, range_days)
        raise


@task(name="upsert-market-data")
def upsert_market_data(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    rows: List[Tuple] = []
    for _, row in df.iterrows():
        rows.append(
            (
                str(row["symbol"]),
                pd.Timestamp(row["timestamp"]).to_pydatetime(),
                float(row["open"]),
                float(row["high"]),
                float(row["low"]),
                float(row["close"]),
                int(row["volume"]),
            )
        )
    query = (
        "INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (symbol, timestamp) DO NOTHING"
    )
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.executemany(query, rows)
        conn.commit()
        return len(rows)

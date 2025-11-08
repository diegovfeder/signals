"""
Indicator calculation tasks shared across flows.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import polars as pl
import numpy as np
from prefect import task

try:
    from ..lib.indicators.rsi import calculate_rsi
    from ..lib.indicators.macd import calculate_macd
    from ..lib.indicators.ema import calculate_ema
except ImportError:
    from lib.indicators.rsi import calculate_rsi
    from lib.indicators.macd import calculate_macd
    from lib.indicators.ema import calculate_ema

from .db import get_db_conn


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _safe_float(value):
    if value is None:
        return None
    if isinstance(value, float) and np.isnan(value):
        return None
    return float(value)


def _load_price_history(symbol: str, window: int | None) -> pl.DataFrame:
    if window is not None and window <= 0:
        raise ValueError("window must be positive when provided")
    with get_db_conn() as conn, conn.cursor() as cur:
        if window:
            cur.execute(
                """
                SELECT timestamp, close FROM (
                    SELECT timestamp, close
                    FROM market_data
                    WHERE symbol=%s
                    ORDER BY timestamp DESC
                    LIMIT %s
                ) recent
                ORDER BY timestamp ASC
                """,
                (symbol, window),
            )
        else:
            cur.execute(
                "SELECT timestamp, close FROM market_data WHERE symbol=%s ORDER BY timestamp ASC",
                (symbol,),
            )
        rows = cur.fetchall()
    if not rows:
        return pl.DataFrame(schema={"timestamp": pl.Datetime, "close": pl.Float64})
    return pl.DataFrame(
        rows, schema={"timestamp": pl.Datetime, "close": pl.Float64}, orient="row"
    )


def _build_indicator_frame(symbol: str, price_df: pl.DataFrame) -> pl.DataFrame:
    if price_df.height == 0:
        return pl.DataFrame(
            schema={
                "symbol": pl.Utf8,
                "timestamp": pl.Datetime,
                "rsi": pl.Float64,
                "ema_12": pl.Float64,
                "ema_26": pl.Float64,
                "macd": pl.Float64,
                "macd_signal": pl.Float64,
                "macd_histogram": pl.Float64,
            }
        )

    # Create a simple DataFrame with just close prices for indicator calculations
    closes = price_df["close"].cast(pl.Float64)
    price_only_df = pl.DataFrame({"close": closes})

    # Calculate indicators
    rsi_series = calculate_rsi(price_only_df, period=14, price_column="close")
    ema12 = calculate_ema(closes, span=12)
    ema26 = calculate_ema(closes, span=26)
    macd_line, macd_signal_series, macd_hist = calculate_macd(price_only_df)

    # Ensure timestamps are UTC
    timestamps = [
        _ensure_utc(ts) if isinstance(ts, datetime) else _ensure_utc(ts.to_pydatetime())
        for ts in price_df["timestamp"].to_list()
    ]

    return pl.DataFrame(
        {
            "symbol": [symbol] * len(timestamps),
            "timestamp": timestamps,
            "rsi": rsi_series,
            "ema_12": ema12,
            "ema_26": ema26,
            "macd": macd_line,
            "macd_signal": macd_signal_series,
            "macd_histogram": macd_hist,
        }
    )


def _get_last_row(df: pl.DataFrame) -> dict[str, Any]:
    if df.height == 0:
        raise ValueError("Cannot fetch the last row of an empty DataFrame")
    return df.row(df.height - 1, named=True)


def _bulk_upsert_indicator_rows(indicator_df: pl.DataFrame) -> int:
    if indicator_df.height == 0:
        return 0

    rows = [
        (
            row["symbol"],
            row["timestamp"],
            _safe_float(row.get("rsi")),
            _safe_float(row.get("ema_12")),
            _safe_float(row.get("ema_26")),
            _safe_float(row.get("macd")),
            _safe_float(row.get("macd_signal")),
            _safe_float(row.get("macd_histogram")),
        )
        for row in indicator_df.iter_rows(named=True)
    ]

    query = """
        INSERT INTO indicators (symbol, timestamp, rsi, ema_12, ema_26, macd, macd_signal, macd_histogram)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, timestamp) DO UPDATE SET
            rsi = EXCLUDED.rsi,
            ema_12 = EXCLUDED.ema_12,
            ema_26 = EXCLUDED.ema_26,
            macd = EXCLUDED.macd,
            macd_signal = EXCLUDED.macd_signal,
            macd_histogram = EXCLUDED.macd_histogram
    """
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.executemany(query, rows)
        conn.commit()
    return len(rows)


@task(name="calculate-and-upsert-indicators")
def calculate_and_upsert_indicators(
    symbol: str,
    window: int | None = 600,
) -> tuple[float, float, float, float, float, datetime]:
    """Compute RSI/EMA/MACD for the requested window and upsert indicator rows."""
    price_history = _load_price_history(symbol, window)
    if price_history.height == 0:
        raise RuntimeError(f"No market_data for {symbol}")

    indicator_frame = _build_indicator_frame(symbol, price_history)
    _bulk_upsert_indicator_rows(indicator_frame)

    # Get the last row from each DataFrame
    latest_price_row = _get_last_row(price_history)
    latest_indicator_row = _get_last_row(indicator_frame)

    latest_close = float(latest_price_row["close"])
    latest_ts_raw = latest_price_row["timestamp"]
    latest_ts = (
        _ensure_utc(latest_ts_raw)
        if isinstance(latest_ts_raw, datetime)
        else _ensure_utc(latest_ts_raw.to_pydatetime())
    )

    # Extract indicator values with null handling
    def get_value(row, col, default):
        val = row[col]
        return float(val) if val is not None and not np.isnan(val) else default

    latest_rsi = get_value(latest_indicator_row, "rsi", 50.0)
    latest_ema12 = get_value(latest_indicator_row, "ema_12", latest_close)
    latest_ema26 = get_value(latest_indicator_row, "ema_26", latest_close)
    latest_macd_hist = get_value(latest_indicator_row, "macd_histogram", 0.0)

    return (
        latest_rsi,
        latest_ema12,
        latest_ema26,
        latest_macd_hist,
        latest_close,
        latest_ts,
    )

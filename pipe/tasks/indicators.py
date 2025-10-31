"""
Indicator calculation tasks shared across flows.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional, Tuple

import pandas as pd
from prefect import task

try:
    from ..lib.indicators.rsi import calculate_rsi
    from ..lib.indicators.macd import calculate_macd
    from ..lib.indicators import calculate_ema
except ImportError:
    from lib.indicators.rsi import calculate_rsi
    from lib.indicators.macd import calculate_macd
    from lib.indicators import calculate_ema

from .db import get_db_conn


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _safe_float(value):
    if value is None:
        return None
    if isinstance(value, float) and pd.isna(value):
        return None
    return float(value)


def _load_price_history(symbol: str, window: Optional[int]) -> pd.DataFrame:
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
        return pd.DataFrame(columns=["timestamp", "close"])
    return pd.DataFrame(rows, columns=["timestamp", "close"])


def _build_indicator_frame(symbol: str, price_df: pd.DataFrame) -> pd.DataFrame:
    if price_df.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "timestamp",
                "rsi",
                "ema_12",
                "ema_26",
                "macd",
                "macd_signal",
                "macd_histogram",
            ]
        )

    closes = price_df["close"].astype(float).reset_index(drop=True)
    price_only_df = pd.DataFrame({"close": closes})
    rsi_series = calculate_rsi(price_only_df, period=14, price_column="close").reset_index(drop=True)
    ema12 = calculate_ema(closes, span=12).reset_index(drop=True)
    ema26 = calculate_ema(closes, span=26).reset_index(drop=True)
    macd_line, macd_signal, macd_hist = calculate_macd(price_only_df)

    timestamps = [
        _ensure_utc(pd.Timestamp(ts).to_pydatetime())  # type: ignore[arg-type]
        for ts in price_df["timestamp"]
    ]

    return pd.DataFrame(
        {
            "symbol": symbol,
            "timestamp": timestamps,
            "rsi": rsi_series,
            "ema_12": ema12,
            "ema_26": ema26,
            "macd": macd_line,
            "macd_signal": macd_signal,
            "macd_histogram": macd_hist,
        }
    )


def _bulk_upsert_indicator_rows(indicator_df: pd.DataFrame) -> int:
    if indicator_df.empty:
        return 0
    rows = []
    for _, row in indicator_df.iterrows():
        rows.append(
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
        )

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
    window: Optional[int] = 600,
) -> Tuple[float, float, float, float, float, datetime]:
    """Compute RSI/EMA/MACD for the requested window and upsert indicator rows."""
    price_history = _load_price_history(symbol, window)
    if price_history.empty:
        raise RuntimeError(f"No market_data for {symbol}")

    indicator_frame = _build_indicator_frame(symbol, price_history)
    _bulk_upsert_indicator_rows(indicator_frame)

    latest_price_row = price_history.iloc[-1]
    latest_indicator_row = indicator_frame.iloc[-1]

    latest_close = float(latest_price_row["close"])
    latest_ts = _ensure_utc(pd.Timestamp(latest_price_row["timestamp"]).to_pydatetime())  # type: ignore[arg-type]

    latest_rsi = (
        float(latest_indicator_row["rsi"]) if pd.notna(latest_indicator_row["rsi"]) else 50.0
    )
    latest_ema12 = (
        float(latest_indicator_row["ema_12"]) if pd.notna(latest_indicator_row["ema_12"]) else latest_close
    )
    latest_ema26 = (
        float(latest_indicator_row["ema_26"]) if pd.notna(latest_indicator_row["ema_26"]) else latest_close
    )
    latest_macd_hist = (
        float(latest_indicator_row["macd_histogram"])
        if pd.notna(latest_indicator_row["macd_histogram"])
        else 0.0
    )

    return latest_rsi, latest_ema12, latest_ema26, latest_macd_hist, latest_close, latest_ts

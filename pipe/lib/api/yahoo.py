"""Yahoo Finance data source helpers."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import Optional

import polars as pl
import requests

YAHOO_CHART_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"


def fetch_daily(symbol: str, range_days: Optional[int]) -> pl.DataFrame:
    days = max(range_days or 365, 5)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days + 5)

    params = {
        "period1": str(int(start.timestamp())),
        "period2": str(int(end.timestamp())),
        "interval": "1d",
        "includePrePost": "false",
        "events": "div,split",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; SignalsBackfill/1.0)",
        "Accept": "application/json",
    }
    response = requests.get(
        YAHOO_CHART_BASE_URL.format(symbol=symbol),
        params=params,
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    result = payload.get("chart", {}).get("result")
    if not result:
        error_info = payload.get("chart", {}).get("error")
        raise RuntimeError(f"Yahoo Finance chart API error for {symbol}: {error_info}")

    chart_data = result[0]
    timestamps = chart_data.get("timestamp") or []
    indicators = chart_data.get("indicators", {}).get("quote", [{}])[0]
    if not timestamps or not indicators:
        raise RuntimeError(f"Yahoo Finance chart API returned empty data for {symbol}")

    # Convert Unix timestamps to datetime with UTC timezone
    dt_timestamps = [datetime.fromtimestamp(ts, tz=timezone.utc) for ts in timestamps]

    df = pl.DataFrame(
        {
            "timestamp": dt_timestamps,
            "open": indicators.get("open"),
            "high": indicators.get("high"),
            "low": indicators.get("low"),
            "close": indicators.get("close"),
            "volume": indicators.get("volume"),
        }
    )

    # Drop rows with null OHLC values
    df = df.filter(
        pl.col("open").is_not_null()
        & pl.col("high").is_not_null()
        & pl.col("low").is_not_null()
        & pl.col("close").is_not_null()
    )

    if df.height == 0:
        raise RuntimeError(f"Yahoo Finance chart API returned NaN data for {symbol}")

    # Add symbol column and fill null volumes with 0
    df = df.with_columns([
        pl.lit(symbol).alias("symbol"),
        pl.col("volume").fill_null(0).cast(pl.Int64)
    ])

    # Sort by timestamp
    df = df.sort("timestamp")

    return df


__all__ = ["fetch_daily"]

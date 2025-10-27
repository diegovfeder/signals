"""Alpha Vantage data source helpers."""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone, timedelta
from threading import Lock
from typing import Dict, List, Optional

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"

DEFAULT_SYMBOLS = ["BTC-USD", "AAPL", "IVV", "BRL=X"]

ALPHA_VANTAGE_CONFIG: Dict[str, Dict] = {
    "BTC-USD": {
        "function": "CRYPTO_INTRADAY",
        "params": {"symbol": "BTC", "market": "USD"},
        "series_key": lambda interval: f"Time Series Crypto ({interval})",
        "request_interval": "5min",
        "resample_to": "15min",
    },
    "AAPL": {
        "function": "TIME_SERIES_INTRADAY",
        "params": {"symbol": "AAPL"},
        "series_key": lambda interval: f"Time Series ({interval})",
    },
    "IVV": {
        "function": "TIME_SERIES_INTRADAY",
        "params": {"symbol": "IVV"},
        "series_key": lambda interval: f"Time Series ({interval})",
    },
    "BRL=X": {
        "function": "FX_INTRADAY",
        "params": {"from_symbol": "BRL", "to_symbol": "USD"},
        "series_key": lambda interval: f"Time Series FX ({interval})",
    },
}

ALPHA_VANTAGE_HISTORICAL_CONFIG: Dict[str, Dict] = {
    "BTC-USD": {
        "function": "DIGITAL_CURRENCY_DAILY",
        "params": {"symbol": "BTC", "market": "USD"},
        "series_key": lambda _interval: "Time Series (Digital Currency Daily)",
        "value_overrides": {
            "open": ["1a. open (USD)", "1. open"],
            "high": ["2a. high (USD)", "2. high"],
            "low": ["3a. low (USD)", "3. low"],
            "close": ["4a. close (USD)", "4. close"],
            "volume": ["5. volume", "5. Volume"],
        },
    },
    "AAPL": {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "params": {"symbol": "AAPL"},
        "series_key": lambda _interval: "Time Series (Daily)",
    },
    "IVV": {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "params": {"symbol": "IVV"},
        "series_key": lambda _interval: "Time Series (Daily)",
    },
    "BRL=X": {
        "function": "FX_DAILY",
        "params": {"from_symbol": "BRL", "to_symbol": "USD"},
        "series_key": lambda _interval: "Time Series FX (Daily)",
    },
}

_ALPHA_RATE_LOCK = Lock()
_LAST_ALPHA_CALL = 0.0
_ALPHA_CALL_INTERVAL_SECONDS = 13.0


def _normalize_interval_for_api(interval: str) -> str:
    interval = interval.lower()
    mapping = {
        "1m": "1min",
        "5m": "5min",
        "15m": "15min",
        "30m": "30min",
        "60m": "60min",
        "1h": "60min",
    }
    if interval in mapping:
        return mapping[interval]
    if interval.endswith("min"):
        return interval
    raise RuntimeError(f"Unsupported interval '{interval}' for Alpha Vantage")


def _interval_to_pandas_freq(api_interval: str) -> str:
    freq_map = {
        "1min": "1T",
        "5min": "5T",
        "15min": "15T",
        "30min": "30T",
        "60min": "60T",
    }
    if api_interval not in freq_map:
        raise RuntimeError(f"Unsupported resample interval '{api_interval}' for pandas")
    return freq_map[api_interval]


def _parse_time_series(
    symbol: str,
    interval_label: str,
    payload: Dict,
    series_key_fn,
    value_overrides: Optional[Dict[str, List[str]]] = None,
) -> pd.DataFrame:
    series_key = series_key_fn(interval_label)
    series = payload.get(series_key)
    if not series:
        available = ", ".join(payload.keys())
        raise RuntimeError(
            f"No time series '{series_key}' for {symbol}; received keys: {available or 'none'}"
        )

    default_field_keys = {
        "open": ["1. open"],
        "high": ["2. high"],
        "low": ["3. low"],
        "close": ["4. close"],
        "volume": ["5. volume", "5. Volume"],
    }

    records = []
    for ts_str, values in series.items():
        def _select_value(field: str) -> Optional[str]:
            keys: List[str] = []
            if value_overrides and field in value_overrides:
                keys.extend(value_overrides[field])
            keys.extend(default_field_keys.get(field, []))
            for key in keys:
                candidate = values.get(key)
                if candidate is not None:
                    return candidate
            return None

        open_raw = _select_value("open")
        high_raw = _select_value("high")
        low_raw = _select_value("low")
        close_raw = _select_value("close")
        volume_raw = _select_value("volume") or "0"
        if None in (open_raw, high_raw, low_raw, close_raw):
            raise RuntimeError(f"Incomplete data for {symbol} at {ts_str}: {values}")
        try:
            open_price = float(open_raw)
            high_price = float(high_raw)
            low_price = float(low_raw)
            close_price = float(close_raw)
        except ValueError as exc:
            raise RuntimeError(f"Non-numeric OHLC for {symbol} at {ts_str}: {values}") from exc
        try:
            volume = int(float(volume_raw))
        except (TypeError, ValueError):
            volume = 0
        records.append(
            {
                "timestamp": ts_str,
                "open": open_price,
                "high": high_price,
                "low": low_price,
                "close": close_price,
                "volume": volume,
            }
        )

    df = pd.DataFrame(records)
    timezone_label = next((v for k, v in payload.get("Meta Data", {}).items() if "Time Zone" in k), "UTC")
    timestamps = pd.to_datetime(df["timestamp"])
    timestamp_index = pd.DatetimeIndex(timestamps)
    if timestamp_index.tz is None:
        try:
            timestamp_index = timestamp_index.tz_localize(timezone_label or "UTC")
        except (ValueError, TypeError):
            timestamp_index = timestamp_index.tz_localize("UTC")
    df["timestamp"] = timestamp_index.tz_convert("UTC")
    df["symbol"] = symbol
    df["volume"] = df["volume"].astype(int)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return df[["open", "high", "low", "close", "volume", "symbol", "timestamp"]]


def _throttle_call():
    global _LAST_ALPHA_CALL
    with _ALPHA_RATE_LOCK:
        now = time.monotonic()
        wait_for = _ALPHA_CALL_INTERVAL_SECONDS - (now - _LAST_ALPHA_CALL)
        if wait_for > 0:
            time.sleep(wait_for)
        _LAST_ALPHA_CALL = time.monotonic()


def fetch_intraday(symbol: str, interval: str = "15m") -> pd.DataFrame:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY not set; obtain a free key at https://www.alphavantage.co/")

    config = ALPHA_VANTAGE_CONFIG.get(symbol)
    if not config:
        raise RuntimeError(f"No Alpha Vantage configuration defined for symbol '{symbol}'")

    request_interval = config.get("request_interval", interval)
    api_interval = _normalize_interval_for_api(request_interval)
    target_api_interval = _normalize_interval_for_api(config.get("resample_to", interval))
    target_freq = _interval_to_pandas_freq(target_api_interval)

    _throttle_call()
    params = {
        "apikey": api_key,
        "function": config["function"],
        "interval": api_interval,
        "outputsize": "compact",
        **config["params"],
    }

    response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if payload.get("Information"):
        raise RuntimeError(f"Alpha Vantage informational response for {symbol}: {payload['Information']}")
    if "Note" in payload:
        raise RuntimeError(f"Alpha Vantage rate limit hit for {symbol}: {payload['Note']}")
    if "Error Message" in payload:
        raise RuntimeError(f"Alpha Vantage error for {symbol}: {payload['Error Message']}")

    df = _parse_time_series(symbol, api_interval, payload, config["series_key"])
    if target_api_interval != api_interval:
        df = _resample(df, target_freq)
    return df


def fetch_daily(symbol: str, range_days: Optional[int]) -> pd.DataFrame:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY not set; obtain a free key at https://www.alphavantage.co/")

    config = ALPHA_VANTAGE_HISTORICAL_CONFIG.get(symbol)
    if not config:
        raise RuntimeError(f"No Alpha Vantage historical configuration defined for symbol '{symbol}'")

    _throttle_call()
    params = {"apikey": api_key, "function": config["function"], "outputsize": "full", **config["params"]}
    response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if payload.get("Information"):
        raise RuntimeError(f"Alpha Vantage informational response for {symbol}: {payload['Information']}")
    if "Note" in payload:
        raise RuntimeError(f"Alpha Vantage rate limit/premium note for {symbol}: {payload['Note']}")
    if "Error Message" in payload:
        raise RuntimeError(f"Alpha Vantage error for {symbol}: {payload['Error Message']}")

    df = _parse_time_series(
        symbol,
        "daily",
        payload,
        config["series_key"],
        value_overrides=config.get("value_overrides"),
    )
    return df


def _resample(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
    if df.empty:
        return df
    symbol = df["symbol"].iloc[0]
    working = df.copy()
    working["timestamp"] = pd.to_datetime(working["timestamp"], utc=True)
    working = working.set_index("timestamp")
    resampled = (
        working.resample(target_freq)
        .agg({"open": "first", "high": "max", "low": "min", "close": "last", "volume": "sum"})
        .dropna(subset=["open", "high", "low", "close"])
        .reset_index()
    )
    resampled["symbol"] = symbol
    resampled["volume"] = resampled["volume"].fillna(0).astype(int)
    return resampled[["open", "high", "low", "close", "volume", "symbol", "timestamp"]]


__all__ = [
    "DEFAULT_SYMBOLS",
    "fetch_intraday",
    "fetch_daily",
]

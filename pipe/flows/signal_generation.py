"""
Signal Generation Flow (Single-Flow MVP)

Every 15 minutes per symbol:
1) Fetch recent OHLCV from Alpha Vantage and upsert into market_data
2) Calculate RSI-14, EMA-12, EMA-26 and upsert into indicators
3) Generate BUY/HOLD signal with simple rules and store idempotently
4) Notify (MVP: log only if strength >= 70)
"""

import argparse
import os
import time
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Tuple, Optional
from threading import Lock

import pandas as pd
import requests
import psycopg
from prefect import flow, task
from dotenv import load_dotenv

from data.indicators.rsi import calculate_rsi
from data.indicators.macd import calculate_macd
from data.utils import calculate_ema
from data.signals.signal_generator import generate_signal as generate_signal_mvp
from data.signals.signal_scorer import calculate_signal_strength

ALPHA_VANTAGE_BASE_URL = "https://www.alphavantage.co/query"
YAHOO_CHART_BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
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

HISTORICAL_RANGE_MAP: Dict[str, int] = {
    "1m": 30,
    "3m": 90,
    "6m": 180,
    "1y": 365,
    "3y": 365 * 3,
    "5y": 365 * 5,
    "max": 365 * 20,
}

MAX_BACKFILL_DAYS = HISTORICAL_RANGE_MAP["max"]


load_dotenv()

_ALPHA_RATE_LOCK = Lock()
_LAST_ALPHA_CALL = 0.0
_ALPHA_CALL_INTERVAL_SECONDS = 13.0  # Free tier allows 5 calls per minute


def _resolve_symbols(explicit: List[str] | None = None) -> List[str]:
    if explicit:
        return explicit
    env_value = os.getenv("SIGNAL_SYMBOLS")
    if env_value:
        candidates = [sym.strip() for sym in env_value.split(",") if sym.strip()]
        if candidates:
            return candidates
    return DEFAULT_SYMBOLS


def _resolve_history_days(explicit_days: Optional[int], range_label: Optional[str]) -> Optional[int]:
    if explicit_days is not None:
        return max(1, min(explicit_days, MAX_BACKFILL_DAYS))
    if range_label:
        normalized = range_label.lower()
        if normalized not in HISTORICAL_RANGE_MAP:
            raise ValueError(
                f"Unsupported backfill range '{range_label}'. Valid options: {', '.join(HISTORICAL_RANGE_MAP.keys())}"
            )
        return HISTORICAL_RANGE_MAP[normalized]

    env_days = os.getenv("BACKFILL_DAYS")
    if env_days:
        try:
            return max(1, min(int(env_days), MAX_BACKFILL_DAYS))
        except ValueError:
            raise ValueError(f"Invalid BACKFILL_DAYS value: {env_days}")

    env_range = os.getenv("BACKFILL_RANGE")
    if env_range:
        normalized = env_range.lower()
        if normalized not in HISTORICAL_RANGE_MAP:
            raise ValueError(
                f"Unsupported BACKFILL_RANGE '{env_range}'. Valid options: {', '.join(HISTORICAL_RANGE_MAP.keys())}"
            )
        return HISTORICAL_RANGE_MAP[normalized]
    return None


def _get_db_conn():
    db_url = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")
    if "+psycopg" in db_url:
        # Allow SQLAlchemy-style URLs (postgresql+psycopg://) by stripping the dialect suffix.
        scheme, remainder = db_url.split("://", 1)
        scheme = scheme.split("+", 1)[0]
        db_url = f"{scheme}://{remainder}"
    return psycopg.connect(db_url)


def _parse_alpha_vantage_time_series(
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
        raise RuntimeError(f"No time series '{series_key}' for {symbol}; received keys: {available or 'none'}")

    records = []
    default_field_keys = {
        "open": ["1. open"],
        "high": ["2. high"],
        "low": ["3. low"],
        "close": ["4. close"],
        "volume": ["5. volume", "5. Volume"],
    }

    for ts_str, values in series.items():
        def _select_value(field: str) -> Optional[str]:
            keys = []
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

    if not records:
        raise RuntimeError(f"Alpha Vantage returned empty series for {symbol}")

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


def _resample_ohlcv(df: pd.DataFrame, target_freq: str) -> pd.DataFrame:
    """Resample OHLCV data to a target interval using standard OHLC rules."""
    if df.empty:
        return df
    symbol = df["symbol"].iloc[0]
    timestamps = pd.to_datetime(df["timestamp"], utc=True)
    working = df.copy()
    working["timestamp"] = timestamps
    working = working.set_index("timestamp")
    working.index = pd.DatetimeIndex(working.index)
    resampled = (
        working.resample(target_freq)
        .agg(
            {
                "open": "first",
                "high": "max",
                "low": "min",
                "close": "last",
                "volume": "sum",
            }
        )
        .dropna(subset=["open", "high", "low", "close"])
        .reset_index()
    )
    resampled["symbol"] = symbol
    resampled["volume"] = resampled["volume"].fillna(0).astype(int)
    return resampled[["open", "high", "low", "close", "volume", "symbol", "timestamp"]]


def _limit_df_to_days(df: pd.DataFrame, range_days: Optional[int]) -> pd.DataFrame:
    if not range_days or range_days <= 0 or df.empty:
        return df
    cutoff = pd.Timestamp.now(tz=timezone.utc) - pd.Timedelta(days=range_days)
    filtered = df[df["timestamp"] >= cutoff]
    return filtered.reset_index(drop=True)


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _safe_float(value: Optional[float]) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, float) and (pd.isna(value)):
        return None
    return float(value)


def _load_price_history(symbol: str, window: Optional[int] = 600) -> pd.DataFrame:
    if window is not None and window <= 0:
        raise ValueError("window must be positive when provided")
    with _get_db_conn() as conn, conn.cursor() as cur:
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
    with _get_db_conn() as conn, conn.cursor() as cur:
        cur.executemany(query, rows)
        conn.commit()
    return len(rows)


def _should_fallback_to_yfinance(exc: Exception) -> bool:
    message = str(exc).lower()
    keywords = [
        "premium endpoint",
        "thank you for using alpha vantage",
        "please visit https://www.alphavantage.co/premium",
        "api call frequency",
        "rate limit",
    ]
    return any(keyword in message for keyword in keywords)


def _fetch_alpha_vantage_history(symbol: str, range_days: Optional[int]) -> pd.DataFrame:
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("ALPHA_VANTAGE_API_KEY not set; obtain a free key at https://www.alphavantage.co/")

    config = ALPHA_VANTAGE_HISTORICAL_CONFIG.get(symbol)
    if not config:
        raise RuntimeError(f"No Alpha Vantage historical configuration defined for symbol '{symbol}'")

    with _ALPHA_RATE_LOCK:
        global _LAST_ALPHA_CALL
        now = time.monotonic()
        wait_for = _ALPHA_CALL_INTERVAL_SECONDS - (now - _LAST_ALPHA_CALL)
        if wait_for > 0:
            time.sleep(wait_for)
        _LAST_ALPHA_CALL = time.monotonic()

    params = {
        "apikey": api_key,
        "function": config["function"],
        "outputsize": "full",
        **config["params"],
    }

    response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
    response.raise_for_status()
    payload = response.json()

    info_note = payload.get("Information")
    if info_note:
        raise RuntimeError(f"Alpha Vantage informational response for {symbol}: {info_note}")
    if "Note" in payload:
        raise RuntimeError(f"Alpha Vantage rate limit/premium note for {symbol}: {payload['Note']}")
    if "Error Message" in payload:
        raise RuntimeError(f"Alpha Vantage error for {symbol}: {payload['Error Message']}")

    df = _parse_alpha_vantage_time_series(
        symbol,
        "daily",
        payload,
        config["series_key"],
        value_overrides=config.get("value_overrides"),
    )
    return _limit_df_to_days(df, range_days)


def _fetch_yahoo_chart_history(symbol: str, range_days: Optional[int]) -> pd.DataFrame:
    days = max(range_days or 365, 5)
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=days + 5)  # add padding to ensure enough data

    params = {
        "period1": str(int(start.timestamp())),
        "period2": str(int(end.timestamp())),
        "interval": "1d",
        "includePrePost": "false",
        "events": "div,split",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; PrefectBackfill/1.0)",
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

    df = pd.DataFrame(
        {
            "timestamp": pd.to_datetime(timestamps, unit="s", utc=True),
            "open": indicators.get("open"),
            "high": indicators.get("high"),
            "low": indicators.get("low"),
            "close": indicators.get("close"),
            "volume": indicators.get("volume"),
        }
    )
    df = df.dropna(subset=["open", "high", "low", "close"])
    if df.empty:
        raise RuntimeError(f"Yahoo Finance chart API returned NaN-only rows for {symbol}")

    df["symbol"] = symbol
    df["volume"] = df["volume"].fillna(0).astype(int)
    df = df.sort_values("timestamp").reset_index(drop=True)
    return _limit_df_to_days(df, range_days)


@task(name="fetch-ohlcv", retries=3, retry_delay_seconds=10)
def fetch_ohlcv(symbol: str, interval: str = "15m", lookback: str = "2d") -> pd.DataFrame:
    """Fetch recent OHLCV from Alpha Vantage."""
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

    with _ALPHA_RATE_LOCK:
        global _LAST_ALPHA_CALL
        now = time.monotonic()
        wait_for = _ALPHA_CALL_INTERVAL_SECONDS - (now - _LAST_ALPHA_CALL)
        if wait_for > 0:
            time.sleep(wait_for)
        _LAST_ALPHA_CALL = time.monotonic()

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

    info_note = payload.get("Information")
    if info_note:
        raise RuntimeError(f"Alpha Vantage informational response for {symbol}: {info_note}")
    if "Note" in payload:
        raise RuntimeError(f"Alpha Vantage rate limit hit for {symbol}: {payload['Note']}")
    if "Error Message" in payload:
        raise RuntimeError(f"Alpha Vantage error for {symbol}: {payload['Error Message']}")

    df = _parse_alpha_vantage_time_series(symbol, api_interval, payload, config["series_key"])
    if target_api_interval != api_interval:
        df = _resample_ohlcv(df, target_freq)
    return df


@task(name="fetch-historical-ohlcv", retries=3, retry_delay_seconds=30)
def fetch_historical_ohlcv(symbol: str, range_days: Optional[int] = None) -> pd.DataFrame:
    """Fetch historical OHLCV (daily) data for larger backfills, falling back to Yahoo Finance when needed."""
    try:
        df = _fetch_alpha_vantage_history(symbol, range_days)
        if df.empty:
            raise RuntimeError("Alpha Vantage returned no historical data")
        return df
    except Exception as exc:
        if _should_fallback_to_yfinance(exc):
            print(f"[backfill] Alpha Vantage unavailable for {symbol} ({exc}); falling back to Yahoo Finance.")
            yahoo_df = _fetch_yahoo_chart_history(symbol, range_days)
            if yahoo_df.empty:
                raise RuntimeError(f"Yahoo Finance returned no data for {symbol}") from exc
            return yahoo_df
        raise


@task(name="upsert-market-data")
def upsert_market_data(df: pd.DataFrame) -> int:
    """Upsert OHLCV rows into market_data; returns count."""
    if df.empty:
        return 0
    rows = []
    for _, row in df.iterrows():
        rows.append((
            str(row['symbol']),
            pd.Timestamp(row['timestamp']).to_pydatetime(),
            float(row['open']),
            float(row['high']),
            float(row['low']),
            float(row['close']),
            int(row['volume']),
        ))
    query = (
        "INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (symbol, timestamp) DO NOTHING"
    )
    with _get_db_conn() as conn, conn.cursor() as cur:
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


@task(name="generate-and-store-signal")
def generate_and_store_signal(
    symbol: str,
    rsi: float,
    ema12: float,
    ema26: float,
    macd_hist: float,
    price: float,
    ts: datetime,
) -> Dict:
    """Generate signal per MVP rules and store idempotently; returns stored signal dict."""
    # Generate signal
    sig = generate_signal_mvp(rsi=rsi, ema_12=ema12, ema_26=ema26, price=price)
    macd_histogram = macd_hist if macd_hist is not None else None
    strength = calculate_signal_strength(sig["signal_type"], rsi, macd_histogram, ema12, ema26)
    rule_version = "rsi_ema_v1"
    idempotency_key = f"{symbol}:{rule_version}:{ts.isoformat()}"

    # Store
    reasoning_array = sig.get("reasoning", [])
    with _get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            (
                "INSERT INTO signals (symbol, timestamp, signal_type, strength, reasoning, price_at_signal, idempotency_key, rule_version) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (idempotency_key) DO NOTHING"
            ),
            (symbol, ts, sig["signal_type"], float(strength), reasoning_array, float(price), idempotency_key, rule_version),
        )
        conn.commit()
    return {"symbol": symbol, "signal_type": sig["signal_type"], "strength": float(strength), "price": float(price), "at": ts.isoformat()}


@task(name="notify-if-strong")
def notify_if_strong(result: Dict) -> None:
    if result["strength"] >= 70.0:
        print(f"[notify] Strong signal {result['symbol']} {result['signal_type']} {result['strength']}/100 at {result['at']}")


@flow(name="signal-generation", log_prints=True)
def signal_generation_flow(
    symbols: List[str] | None = None,
    backfill_days: Optional[int] = None,
    mode: str = "intraday",
    indicator_window: Optional[int] = 600,
):
    symbols_to_run = _resolve_symbols(symbols)
    effective_backfill_days = backfill_days if backfill_days is not None else _resolve_history_days(None, None)
    normalized_mode = (mode or "intraday").lower()
    if normalized_mode not in {"intraday", "backfill", "both"}:
        raise ValueError("mode must be one of: intraday, backfill, both")
    if normalized_mode == "backfill" and effective_backfill_days is None:
        raise ValueError("Backfill mode requires --backfill-days or BACKFILL_RANGE/BACKFILL_DAYS env vars.")

    indicator_window_value = indicator_window if (indicator_window is None or indicator_window > 0) else None

    run_backfill = effective_backfill_days is not None
    run_intraday = normalized_mode in {"intraday", "both"}
    if normalized_mode == "backfill":
        run_intraday = False

    run_label = []
    if run_backfill:
        run_label.append(f"backfill={effective_backfill_days}d")
    if run_intraday:
        run_label.append("intraday")
    summary = ", ".join(run_label) if run_label else "no-op"

    print(f"Starting signal generation for {len(symbols_to_run)} symbols ({summary})...")

    for symbol in symbols_to_run:
        try:
            if run_backfill:
                print(f"[backfill] Fetching {effective_backfill_days}d history for {symbol}...")
                historical_df = fetch_historical_ohlcv(symbol, effective_backfill_days)
                inserted_hist = 0
                if not historical_df.empty:
                    inserted_hist = upsert_market_data(historical_df)
                calculate_and_upsert_indicators(symbol, window=None)
                print(f"[backfill] Upserted {inserted_hist} historical rows for {symbol}")
                if not run_intraday:
                    continue

            if run_intraday:
                print(f"[intraday] Processing {symbol}...")
                ohlcv = fetch_ohlcv(symbol)
                upserted = upsert_market_data(ohlcv)
                print(f"[intraday] Upserted {upserted} market_data rows for {symbol}")
                rsi, ema12, ema26, macd_hist, price, ts = calculate_and_upsert_indicators(
                    symbol, window=indicator_window_value
                )
                result = generate_and_store_signal(symbol, rsi, ema12, ema26, macd_hist, price, ts)
                notify_if_strong(result)
                print(f"✓ {symbol}: {result['signal_type']} ({result['strength']}/100)")
        except Exception as e:
            print(f"✗ Error for {symbol}: {e}")
            continue
    print("Signal generation complete!")


def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Run the signal generation Prefect flow.")
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of symbols to process (defaults to env SIGNAL_SYMBOLS or built-in list).",
    )
    parser.add_argument(
        "--backfill-days",
        type=int,
        help="Number of days of historical data to backfill before running intraday mode.",
    )
    parser.add_argument(
        "--backfill-range",
        type=str,
        choices=sorted(HISTORICAL_RANGE_MAP.keys()),
        help="Named range (e.g., 1y, 5y) for historical backfill. Ignored if --backfill-days is provided.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default="intraday",
        choices=["intraday", "backfill", "both"],
        help="Whether to run intraday updates, historical backfill only, or both.",
    )
    parser.add_argument(
        "--indicator-window",
        type=int,
        default=600,
        help="Number of recent rows to use when recalculating indicators (set to 0 to use entire history).",
    )
    args = parser.parse_args()

    resolved_symbols = (
        [sym.strip() for sym in args.symbols.split(",") if sym.strip()] if args.symbols else None
    )
    resolved_backfill_days = _resolve_history_days(args.backfill_days, args.backfill_range)

    return resolved_symbols, resolved_backfill_days, args.mode, args.indicator_window


if __name__ == "__main__":
    cli_symbols, cli_backfill_days, cli_mode, cli_indicator_window = _parse_cli_args()
    signal_generation_flow(
        symbols=cli_symbols,
        backfill_days=cli_backfill_days,
        mode=cli_mode,
        indicator_window=cli_indicator_window,
    )

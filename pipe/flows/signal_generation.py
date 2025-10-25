"""
Signal Generation Flow (Single-Flow MVP)

Every 15 minutes per symbol:
1) Fetch recent OHLCV from Alpha Vantage and upsert into market_data
2) Calculate RSI-14, EMA-12, EMA-26 and upsert into indicators
3) Generate BUY/HOLD signal with simple rules and store idempotently
4) Notify (MVP: log only if strength >= 70)
"""

import os
import time
from datetime import datetime, timezone
from typing import List, Dict, Tuple
from threading import Lock

import pandas as pd
import requests
import psycopg
from prefect import flow, task
from dotenv import load_dotenv

from data.indicators.rsi import calculate_rsi
from data.utils import calculate_ema
from data.signals.signal_generator import generate_signal as generate_signal_mvp
from data.signals.signal_scorer import calculate_signal_strength

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


def _get_db_conn():
    db_url = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")
    if "+psycopg" in db_url:
        # Allow SQLAlchemy-style URLs (postgresql+psycopg://) by stripping the dialect suffix.
        scheme, remainder = db_url.split("://", 1)
        scheme = scheme.split("+", 1)[0]
        db_url = f"{scheme}://{remainder}"
    return psycopg.connect(db_url)


def _parse_alpha_vantage_time_series(symbol: str, interval_label: str, payload: Dict, series_key_fn) -> pd.DataFrame:
    series_key = series_key_fn(interval_label)
    series = payload.get(series_key)
    if not series:
        available = ", ".join(payload.keys())
        raise RuntimeError(f"No time series '{series_key}' for {symbol}; received keys: {available or 'none'}")

    records = []
    for ts_str, values in series.items():
        open_raw = values.get("1. open")
        high_raw = values.get("2. high")
        low_raw = values.get("3. low")
        close_raw = values.get("4. close")
        volume_raw = values.get("5. volume") or values.get("5. Volume") or "0"
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
def calculate_and_upsert_indicators(symbol: str) -> Tuple[float, float, float, float, datetime]:
    """Compute RSI and EMAs for latest bar and upsert indicators; returns (rsi, ema12, ema26, close, ts)."""
    with _get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT timestamp, close FROM market_data WHERE symbol=%s ORDER BY timestamp DESC LIMIT 50",
            (symbol,),
        )
        rows = cur.fetchall()
        if not rows:
            raise RuntimeError(f"No market_data for {symbol}")
        # Build ascending DataFrame
        data = pd.DataFrame(rows, columns=["timestamp", "close"]).sort_values("timestamp").reset_index(drop=True)
        df = pd.DataFrame({"close": data["close"].astype(float)})
        rsi_series = calculate_rsi(df, period=14, price_column="close")
        ema12 = calculate_ema(df["close"], span=12)
        ema26 = calculate_ema(df["close"], span=26)
        latest_idx = len(df) - 1
        latest_ts = data["timestamp"].iloc[latest_idx].replace(tzinfo=timezone.utc)
        latest_close = float(df["close"].iloc[latest_idx])
        latest_rsi = float(rsi_series.iloc[latest_idx]) if pd.notna(rsi_series.iloc[latest_idx]) else 50.0
        latest_ema12 = float(ema12.iloc[latest_idx]) if pd.notna(ema12.iloc[latest_idx]) else latest_close
        latest_ema26 = float(ema26.iloc[latest_idx]) if pd.notna(ema26.iloc[latest_idx]) else latest_close

        cur.execute(
            (
                "INSERT INTO indicators (symbol, timestamp, rsi, ema_12, ema_26) "
                "VALUES (%s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, timestamp) DO UPDATE SET rsi=EXCLUDED.rsi, ema_12=EXCLUDED.ema_12, ema_26=EXCLUDED.ema_26"
            ),
            (symbol, latest_ts, latest_rsi, latest_ema12, latest_ema26),
        )
        conn.commit()
        return latest_rsi, latest_ema12, latest_ema26, latest_close, latest_ts


@task(name="generate-and-store-signal")
def generate_and_store_signal(symbol: str, rsi: float, ema12: float, ema26: float, price: float, ts: datetime) -> Dict:
    """Generate signal per MVP rules and store idempotently; returns stored signal dict."""
    # Generate signal
    sig = generate_signal_mvp(rsi=rsi, ema_12=ema12, ema_26=ema26, price=price)
    strength = calculate_signal_strength(sig["signal_type"], rsi, None, ema12, ema26)
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
def signal_generation_flow(symbols: List[str] | None = None):
    symbols_to_run = _resolve_symbols(symbols)
    print(f"Starting signal generation for {len(symbols_to_run)} symbols...")
    for symbol in symbols_to_run:
        try:
            print(f"Processing {symbol}...")
            ohlcv = fetch_ohlcv(symbol)
            upserted = upsert_market_data(ohlcv)
            print(f"Upserted {upserted} market_data rows for {symbol}")
            rsi, ema12, ema26, price, ts = calculate_and_upsert_indicators(symbol)
            result = generate_and_store_signal(symbol, rsi, ema12, ema26, price, ts)
            notify_if_strong(result)
            print(f"✓ {symbol}: {result['signal_type']} ({result['strength']}/100)")
        except Exception as e:
            print(f"✗ Error for {symbol}: {e}")
            continue
    print("Signal generation complete!")


if __name__ == "__main__":
    signal_generation_flow()

"""
Signal generation and notification tasks.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from prefect import task

try:
    from ..lib.strategies import StrategyInputs, get_strategy
except ImportError:
    from lib.strategies import StrategyInputs, get_strategy

from .db import get_db_conn

try:
    from ..settings import signal_notify_threshold
except ImportError:
    from settings import signal_notify_threshold


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
    """Generate signal via the configured strategy and store it idempotently."""
    strategy = get_strategy(symbol)
    inputs = StrategyInputs(
        symbol=symbol,
        timestamp=ts,
        price=price,
        rsi=rsi,
        ema_fast=ema12,
        ema_slow=ema26,
        macd_hist=macd_hist,
    )
    result = strategy.generate(inputs)
    idempotency_key = f"{symbol}:{strategy.name}:{ts.isoformat()}"

    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            (
                "INSERT INTO signals (symbol, timestamp, signal_type, strength, reasoning, price_at_signal, idempotency_key, rule_version) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                "ON CONFLICT (symbol, timestamp) DO UPDATE SET "
                "signal_type = EXCLUDED.signal_type, "
                "strength = EXCLUDED.strength, "
                "reasoning = EXCLUDED.reasoning, "
                "price_at_signal = EXCLUDED.price_at_signal, "
                "idempotency_key = EXCLUDED.idempotency_key, "
                "rule_version = EXCLUDED.rule_version"
            ),
            (
                symbol,
                ts,
                result.signal_type,
                float(result.strength),
                result.reasoning,
                float(price),
                idempotency_key,
                strategy.name,
            ),
        )
        conn.commit()
    return {
        "symbol": symbol,
        "signal_type": result.signal_type,
        "strength": float(result.strength),
        "reasoning": result.reasoning,
        "price": float(price),
        "at": ts.isoformat(),
    }


@task(name="notify-if-strong")
def notify_if_strong(result: Dict) -> None:
    threshold = signal_notify_threshold()
    if result["strength"] >= threshold:
        print(
            f"[notify] Strong signal {result['symbol']} {result['signal_type']} "
            f"{result['strength']}/100 at {result['at']}"
        )

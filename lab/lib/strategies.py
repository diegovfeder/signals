"""Adapters around the shared strategy registry for the lab."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Sequence

import polars as pl

from pipe.lib.strategies import (
    Strategy,
    StrategyInputs,
    StrategyResult,
    SignalType,
    get_strategy as _pipeline_get_strategy,
)
from pipe.lib.strategies.crypto_momentum import CryptoMomentumStrategy
from pipe.lib.strategies.default_hold import HoldStrategy
from pipe.lib.strategies.stock_mean_reversion import StockMeanReversionStrategy


@dataclass(frozen=True)
class StrategyParameter:
    name: str
    label: str
    default: float
    min: float
    max: float
    step: float


_STRATEGY_FACTORIES: dict[str, type[Strategy]] = {
    "stock_mean_reversion": StockMeanReversionStrategy,
    "crypto_momentum": CryptoMomentumStrategy,
    "hold": HoldStrategy,
}

_STRATEGY_PARAMETERS: dict[str, Sequence[StrategyParameter]] = {
    "stock_mean_reversion": (
        StrategyParameter("buy_rsi", "Buy RSI threshold", 35.0, 0.0, 100.0, 1.0),
        StrategyParameter("sell_rsi", "Sell RSI threshold", 70.0, 0.0, 100.0, 1.0),
    ),
    "crypto_momentum": (
        StrategyParameter("macd_buy", "MACD buy trigger", 0.5, -5.0, 5.0, 0.1),
        StrategyParameter("macd_sell", "MACD sell trigger", -0.5, -5.0, 5.0, 0.1),
    ),
    "hold": (),
}


def available_strategy_keys() -> list[str]:
    """Return available strategy identifiers."""

    return sorted(_STRATEGY_FACTORIES.keys())


def default_strategy_key_for_symbol(symbol: str) -> str:
    """Return the configured pipeline strategy key for a symbol."""

    strategy = _pipeline_get_strategy(symbol)
    return strategy.name


def get_strategy(
    *,
    symbol: str | None = None,
    strategy_key: str | None = None,
    overrides: Mapping[str, Any] | None = None,
) -> Strategy:
    """Return a configured strategy instance for the lab."""

    base_strategy: Strategy | None = None
    if strategy_key is None:
        if symbol is None:
            raise ValueError("Either symbol or strategy_key must be provided")
        base_strategy = _pipeline_get_strategy(symbol)
        strategy_key = base_strategy.name
        if not overrides:
            return base_strategy
    factory = _STRATEGY_FACTORIES.get(strategy_key)
    if factory is None:
        raise KeyError(f"Unknown strategy '{strategy_key}'")
    if overrides:
        return factory(**overrides)
    if base_strategy is not None:
        return base_strategy
    return factory()


def parameters_for(strategy_key: str) -> Sequence[StrategyParameter]:
    """Return parameter metadata for a strategy key."""

    return _STRATEGY_PARAMETERS.get(strategy_key, ())


def _coerce_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def strategy_inputs_from_row(row: Mapping[str, Any]) -> StrategyInputs:
    """Build StrategyInputs from a row with indicator data."""

    timestamp = row.get("timestamp")
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp)
    if timestamp is None:
        raise ValueError("Row is missing a timestamp")
    price = row.get("close")
    if price is None:
        raise ValueError("Row is missing a closing price")
    return StrategyInputs(
        symbol=str(row.get("symbol", "")),
        timestamp=timestamp,
        price=float(price) if price is not None else 0.0,
        rsi=_coerce_float(row.get("rsi")),
        ema_fast=_coerce_float(row.get("ema_fast")),
        ema_slow=_coerce_float(row.get("ema_slow")),
        macd_hist=_coerce_float(row.get("macd_hist")),
    )


def evaluate_strategy(strategy: Strategy, data: pl.DataFrame) -> pl.DataFrame:
    """Run a strategy across each row of indicator data."""

    if data.is_empty():
        return pl.DataFrame(
            schema={
                "symbol": pl.Utf8,
                "timestamp": pl.Datetime,
                "price": pl.Float64,
                "signal_type": pl.Utf8,
                "strength": pl.Float64,
                "reasoning": pl.List(pl.Utf8),
            }
        )

    results: list[dict[str, Any]] = []
    for row in data.iter_rows(named=True):
        inputs = strategy_inputs_from_row(row)
        result = strategy.generate(inputs)
        results.append(
            {
                "symbol": inputs.symbol,
                "timestamp": inputs.timestamp,
                "price": inputs.price,
                "signal_type": result.signal_type,
                "strength": float(result.strength),
                "reasoning": result.reasoning,
            }
        )
    return pl.DataFrame(results)


__all__ = [
    "Strategy",
    "StrategyInputs",
    "StrategyResult",
    "SignalType",
    "StrategyParameter",
    "available_strategy_keys",
    "default_strategy_key_for_symbol",
    "get_strategy",
    "parameters_for",
    "strategy_inputs_from_row",
    "evaluate_strategy",
]

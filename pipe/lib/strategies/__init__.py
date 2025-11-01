"""Strategy registry and helpers."""

from __future__ import annotations

import os
from typing import Dict

from .base import Strategy, StrategyInputs, StrategyResult, SignalType
from .crypto_momentum import CryptoMomentumStrategy
from .default_hold import HoldStrategy
from .stock_mean_reversion import StockMeanReversionStrategy

_STRATEGY_FACTORIES: Dict[str, type[Strategy]] = {
    "stock_mean_reversion": StockMeanReversionStrategy,
    "crypto_momentum": CryptoMomentumStrategy,
    "hold": HoldStrategy,
}

_DEFAULT_SYMBOL_MAPPING: Dict[str, str] = {
    "BTC-USD": "crypto_momentum",
    "AAPL": "stock_mean_reversion",
}

_ENV_PREFIX = "SIGNAL_MODEL_"


def _env_symbol_key(key: str) -> str:
    symbol_key = key[len(_ENV_PREFIX) :]
    return symbol_key.replace("__", "/").replace("_", "-")


def _build_registry() -> Dict[str, Strategy]:
    registry: Dict[str, Strategy] = {}
    for symbol, strategy_key in _DEFAULT_SYMBOL_MAPPING.items():
        factory = _STRATEGY_FACTORIES.get(strategy_key, HoldStrategy)
        registry[symbol] = factory()

    for env_key, env_value in os.environ.items():
        if not env_key.startswith(_ENV_PREFIX):
            continue
        symbol = _env_symbol_key(env_key)
        strategy_key = env_value.strip().lower()
        factory = _STRATEGY_FACTORIES.get(strategy_key)
        if not factory:
            continue
        registry[symbol] = factory()
    return registry


STRATEGY_REGISTRY = _build_registry()


def get_strategy(symbol: str) -> Strategy:
    return STRATEGY_REGISTRY.get(symbol, HoldStrategy())


__all__ = [
    "Strategy",
    "StrategyInputs",
    "StrategyResult",
    "SignalType",
    "get_strategy",
]

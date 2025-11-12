"""Base strategy interfaces for signal generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Literal, Protocol

SignalType = Literal["BUY", "SELL", "HOLD"]


@dataclass(frozen=True)
class StrategyInputs:
    symbol: str
    timestamp: datetime
    price: float
    rsi: float | None
    ema_fast: float | None
    ema_slow: float | None
    macd_hist: float | None


@dataclass(frozen=True)
class StrategyResult:
    signal_type: SignalType
    reasoning: List[str]
    strength: float
    explanation: str | None = (
        None  # Optional LLM-generated natural language explanation
    )


class Strategy(Protocol):
    """Strategy interface."""

    name: str

    def generate(self, inputs: StrategyInputs) -> StrategyResult: ...

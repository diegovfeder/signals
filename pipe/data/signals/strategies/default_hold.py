"""Default fallback strategy that always holds."""

from __future__ import annotations

from .base import Strategy, StrategyInputs, StrategyResult


class HoldStrategy(Strategy):
    name = "hold"

    def generate(self, inputs: StrategyInputs) -> StrategyResult:
        return StrategyResult(
            signal_type="HOLD",
            reasoning=["No strategy assigned; defaulting to HOLD."],
            strength=0.0,
        )

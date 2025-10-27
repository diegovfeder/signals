"""Stock mean reversion strategy (RSI/EMA focused)."""

from __future__ import annotations

from typing import List

from .base import Strategy, StrategyInputs, StrategyResult


class StockMeanReversionStrategy(Strategy):
    name = "stock_mean_reversion"

    def __init__(self, buy_rsi: float = 35.0, sell_rsi: float = 70.0):
        self.buy_rsi = buy_rsi
        self.sell_rsi = sell_rsi

    def generate(self, inputs: StrategyInputs) -> StrategyResult:
        rsi = inputs.rsi if inputs.rsi is not None else 50.0
        ema_fast = inputs.ema_fast if inputs.ema_fast is not None else inputs.price
        ema_slow = inputs.ema_slow if inputs.ema_slow is not None else inputs.price

        reasoning: List[str] = []
        signal_type = "HOLD"

        ema_spread = ema_fast - ema_slow
        strength = 0.0

        if rsi <= self.buy_rsi and ema_spread >= 0:
            signal_type = "BUY"
            reasoning.append(f"RSI {rsi:.1f} <= {self.buy_rsi}")
            reasoning.append("EMA fast above EMA slow (bullish crossover)")
            strength = min(100.0, (self.buy_rsi - rsi) * 2 + abs(ema_spread) / inputs.price * 1500)
        elif rsi >= self.sell_rsi and ema_spread < 0:
            signal_type = "SELL"
            reasoning.append(f"RSI {rsi:.1f} >= {self.sell_rsi}")
            reasoning.append("EMA fast below EMA slow (bearish crossover)")
            strength = min(100.0, (rsi - self.sell_rsi) * 2 + abs(ema_spread) / inputs.price * 1500)
        else:
            reasoning.append("RSI and EMA spread neutral; holding position")
            strength = max(0.0, 50.0 - abs(rsi - 50.0)) / 2

        return StrategyResult(signal_type=signal_type, reasoning=reasoning, strength=round(strength, 2))

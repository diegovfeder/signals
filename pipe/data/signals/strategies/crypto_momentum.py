"""Crypto momentum strategy emphasizing MACD/EMA."""

from __future__ import annotations

from typing import List

from .base import Strategy, StrategyInputs, StrategyResult


class CryptoMomentumStrategy(Strategy):
    name = "crypto_momentum"

    def __init__(self, macd_buy: float = 0.5, macd_sell: float = -0.5):
        self.macd_buy = macd_buy
        self.macd_sell = macd_sell

    def generate(self, inputs: StrategyInputs) -> StrategyResult:
        macd_hist = inputs.macd_hist if inputs.macd_hist is not None else 0.0
        ema_fast = inputs.ema_fast if inputs.ema_fast is not None else inputs.price
        ema_slow = inputs.ema_slow if inputs.ema_slow is not None else inputs.price
        rsi = inputs.rsi if inputs.rsi is not None else 50.0

        reasoning: List[str] = []
        signal_type = "HOLD"
        strength = 0.0

        ema_spread = ema_fast - ema_slow

        if macd_hist >= self.macd_buy and ema_spread >= 0:
            signal_type = "BUY"
            reasoning.append(f"MACD histogram {macd_hist:.2f} >= {self.macd_buy}")
            reasoning.append("EMA fast above EMA slow (bullish momentum)")
            if rsi < 40:
                reasoning.append(f"RSI {rsi:.1f} still below 40 (room to run)")
            strength = min(100.0, macd_hist * 80 + max(0.0, ema_spread) / inputs.price * 800 + (50 - abs(rsi - 50)))
        elif macd_hist <= self.macd_sell and ema_spread < 0:
            signal_type = "SELL"
            reasoning.append(f"MACD histogram {macd_hist:.2f} <= {self.macd_sell}")
            reasoning.append("EMA fast below EMA slow (bearish momentum)")
            if rsi > 60:
                reasoning.append(f"RSI {rsi:.1f} elevated (selling pressure likely)")
            strength = min(100.0, abs(macd_hist) * 80 + abs(min(0.0, ema_spread)) / inputs.price * 800 + abs(rsi - 40))
        else:
            reasoning.append("Momentum neutral; holding position")
            strength = max(0.0, 40.0 - abs(macd_hist * 40))

        return StrategyResult(signal_type=signal_type, reasoning=reasoning, strength=round(strength, 2))

"""
Trading Signal Generator

Rule-based logic to generate BUY/SELL/HOLD signals from technical indicators.

Rules (MVP):
    BUY:
        - RSI < 30 (oversold) AND MACD bullish crossover
        - RSI < 40 AND MACD > Signal AND Histogram increasing

    SELL:
        - RSI > 70 (overbought) AND MACD bearish crossover
        - RSI > 60 AND MACD < Signal AND Histogram decreasing

    HOLD:
        - None of the above conditions met
"""

from typing import Dict, List, Literal, Any
import pandas as pd

SignalType = Literal["BUY", "SELL", "HOLD"]


def generate_signal(
    *,
    rsi: float | None = None,
    ema_12: float | None = None,
    ema_26: float | None = None,
    macd: float | None = None,
    macd_signal: float | None = None,
    macd_histogram: float | None = None,
    price: float | None = None
) -> Dict[str, Any]:
    """
    Generate trading signal from technical indicators.

    Args:
        rsi: RSI value (0-100)
        macd: MACD line value
        macd_signal: MACD signal line value
        macd_histogram: MACD histogram value
        price: Current asset price

    Returns:
        dict: {
            'signal_type': 'BUY' | 'SELL' | 'HOLD',
            'reasoning': List[str],  # Human-readable reasons
            'price': float
        }

    Example:
        >>> generate_signal(rsi=25, macd=0.5, macd_signal=-0.2, macd_histogram=0.7, price=100)
        {
            'signal_type': 'BUY',
            'reasoning': ['RSI oversold (25)', 'MACD bullish crossover'],
            'price': 100
        }
    """
    reasons: List[str] = []

    # MVP BUY rules: RSI < 30 OR EMA-12 > EMA-26
    if rsi is not None and rsi < 30:
        reasons.append(f"RSI oversold ({rsi:.1f})")
    if (ema_12 is not None and ema_26 is not None) and (ema_12 > ema_26):
        reasons.append("EMA-12 above EMA-26 (bullish momentum)")

    if reasons:
        return {
            "signal_type": "BUY",
            "reasoning": reasons,
            "price": price,
        }

    return {
        "signal_type": "HOLD",
        "reasoning": ["No rule matched (MVP)"],
        "price": price,
    }


def _check_buy_conditions(rsi: float, macd: float, macd_signal: float, macd_histogram: float) -> List[str]:
    """
    Check if BUY conditions are met.

    Returns:
        List of reasons if BUY, empty list otherwise
    """
    reasons = []

    # Rule 1: RSI oversold
    if rsi < 30:
        reasons.append(f"RSI oversold ({rsi:.1f})")

    # Rule 2: MACD bullish crossover
    if macd > macd_signal and macd_histogram > 0:
        reasons.append("MACD bullish crossover")

    return reasons


def _check_sell_conditions(rsi: float, macd: float, macd_signal: float, macd_histogram: float) -> List[str]:
    """
    Check if SELL conditions are met.

    Returns:
        List of reasons if SELL, empty list otherwise
    """
    reasons = []

    # Rule 1: RSI overbought
    if rsi > 70:
        reasons.append(f"RSI overbought ({rsi:.1f})")

    # Rule 2: MACD bearish crossover
    if macd < macd_signal and macd_histogram < 0:
        reasons.append("MACD bearish crossover")

    return reasons

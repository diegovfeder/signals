"""
Signal Strength Scorer

Calculate confidence score (0-100) for trading signals based on:
- Strength of RSI deviation from neutral (50)
- Magnitude of MACD histogram
- Alignment of multiple indicators
"""

from typing import Literal
import numpy as np

SignalType = Literal["BUY", "SELL", "HOLD"]


def calculate_signal_strength(
    signal_type: SignalType,
    rsi: float,
    macd_histogram: float
) -> float:
    """
    Calculate signal strength score (0-100).

    Higher score = higher confidence in the signal.

    Scoring Logic:
        - RSI contribution: 0-50 points
          - Distance from 50 (neutral) = higher score
          - BUY: RSI closer to 0 = higher score
          - SELL: RSI closer to 100 = higher score

        - MACD contribution: 0-50 points
          - Larger histogram magnitude = higher score

    Args:
        signal_type: 'BUY', 'SELL', or 'HOLD'
        rsi: RSI value (0-100)
        macd_histogram: MACD histogram value

    Returns:
        float: Strength score (0-100)

    Example:
        >>> calculate_signal_strength('BUY', rsi=20, macd_histogram=1.5)
        82.5  # Strong BUY signal
    """
    # TODO: Implement signal strength calculation
    # 1. Calculate RSI score (50 points max)
    # 2. Calculate MACD histogram score (50 points max)
    # 3. Sum scores
    # 4. Cap at 100

    if signal_type == "HOLD":
        return 0.0

    raise NotImplementedError("Signal strength calculation not yet implemented")


def _calculate_rsi_score(signal_type: SignalType, rsi: float) -> float:
    """
    Calculate RSI contribution to signal strength (0-50).

    For BUY signals: Lower RSI = higher score
    For SELL signals: Higher RSI = higher score
    """
    if signal_type == "BUY":
        # RSI 0-30 = strong, 30-50 = weak
        return max(0, 50 - rsi)
    elif signal_type == "SELL":
        # RSI 70-100 = strong, 50-70 = weak
        return max(0, rsi - 50)
    else:
        return 0.0


def _calculate_macd_score(signal_type: SignalType, histogram: float) -> float:
    """
    Calculate MACD histogram contribution to signal strength (0-50).

    Larger magnitude = higher score (capped at 50)
    """
    if signal_type == "BUY" and histogram > 0:
        return min(50, abs(histogram) * 10)
    elif signal_type == "SELL" and histogram < 0:
        return min(50, abs(histogram) * 10)
    else:
        return 0.0

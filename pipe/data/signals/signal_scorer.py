"""
Signal Strength Scorer

Calculate confidence score (0-100) for trading signals based on:
- Strength of RSI deviation from neutral (50)
- EMA separation / trend alignment
- Optional MACD histogram contribution when provided
"""

from typing import Literal

SignalType = Literal["BUY", "SELL", "HOLD"]


def calculate_signal_strength(
    signal_type: SignalType,
    rsi: float | None,
    macd_histogram: float | None,
    ema_12: float | None = None,
    ema_26: float | None = None,
) -> float:
    """
    Calculate signal strength score (0-100).

    Higher score = higher confidence in the signal.

    Scoring Logic:
        - RSI contribution: up to 60 points (distance from neutral)
        - EMA trend contribution: up to 40 points (separation + alignment)
        - MACD contribution: up to 20 points (optional, if provided)

    Args:
        signal_type: 'BUY', 'SELL', or 'HOLD'
        rsi: RSI value (0-100)
        macd_histogram: MACD histogram value

    Returns:
        float: Strength score (0-100)

    Example:
        >>> calculate_signal_strength('BUY', rsi=20, macd_histogram=1.5)
        72.0  # Strong BUY signal (without EMA inputs)
    """
    if signal_type == "HOLD":
        return 0.0

    rsi_score = _calculate_rsi_score(signal_type, rsi) if rsi is not None else 0.0
    macd_score = (
        _calculate_macd_score(signal_type, macd_histogram)
        if macd_histogram is not None
        else 0.0
    )
    trend_score = _calculate_trend_score(signal_type, ema_12, ema_26)

    strength = rsi_score + macd_score + trend_score
    strength = max(0.0, min(100.0, strength))
    return float(round(strength, 2))


def _calculate_rsi_score(signal_type: SignalType, rsi: float | None) -> float:
    """
    Calculate RSI contribution to signal strength (0-60).

    For BUY signals: Lower RSI = higher score
    For SELL signals: Higher RSI = higher score
    """
    if rsi is None:
        return 0.0

    rsi_value = float(rsi)
    if signal_type == "BUY":
        distance = max(0.0, 50.0 - rsi_value)
    elif signal_type == "SELL":
        distance = max(0.0, rsi_value - 50.0)
    else:
        distance = 0.0

    normalized = min(1.0, distance / 25.0)  # 25 points from neutral = full score
    return normalized * 60.0


def _calculate_macd_score(signal_type: SignalType, histogram: float | None) -> float:
    """
    Calculate MACD histogram contribution to signal strength (0-20).

    Larger magnitude = higher score (capped at 20) and only when aligned with the signal direction.
    """
    if histogram is None:
        return 0.0

    hist_value = float(histogram)
    if signal_type == "BUY" and hist_value > 0:
        return float(min(20.0, abs(hist_value) * 8.0))
    if signal_type == "SELL" and hist_value < 0:
        return float(min(20.0, abs(hist_value) * 8.0))
    return 0.0


def _calculate_trend_score(
    signal_type: SignalType, ema_12: float | None, ema_26: float | None
) -> float:
    """
    Evaluate EMA separation and alignment to add up to 40 points.
    """
    if ema_12 is None or ema_26 is None:
        return 0.0

    short = float(ema_12)
    long = float(ema_26)
    if long == 0:
        return 0.0

    gap_pct = abs(short - long) / abs(long)
    magnitude_score = min(30.0, (gap_pct / 0.015) * 30.0)  # ~1.5% gap = full mag score

    direction_aligned = (signal_type == "BUY" and short >= long) or (
        signal_type == "SELL" and short <= long
    )
    alignment_score = 10.0 if direction_aligned else 0.0

    return magnitude_score + alignment_score

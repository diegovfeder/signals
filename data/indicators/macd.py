"""
MACD (Moving Average Convergence Divergence) Calculation

Formula:
    MACD Line = 12-period EMA - 26-period EMA
    Signal Line = 9-period EMA of MACD Line
    Histogram = MACD Line - Signal Line

Interpretation:
    MACD crosses above Signal: Bullish (BUY signal)
    MACD crosses below Signal: Bearish (SELL signal)
    Histogram > 0: Bullish momentum
    Histogram < 0: Bearish momentum
"""

import pandas as pd
import numpy as np
from typing import Tuple


def calculate_macd(
    df: pd.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_column: str = "close"
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD indicator.

    Args:
        df: DataFrame with OHLCV data
        fast_period: Fast EMA period (default: 12)
        slow_period: Slow EMA period (default: 26)
        signal_period: Signal line EMA period (default: 9)
        price_column: Name of the price column to use (default: 'close')

    Returns:
        Tuple of (macd_line, signal_line, histogram)

    Example:
        >>> df = pd.DataFrame({'close': [100, 102, 101, 105, 107, 103, 108]})
        >>> macd, signal, histogram = calculate_macd(df)
        >>> histogram.iloc[-1]  # Most recent histogram value
        0.52
    """
    # TODO: Implement MACD calculation
    # 1. Calculate fast EMA (12-period)
    # 2. Calculate slow EMA (26-period)
    # 3. MACD line = fast EMA - slow EMA
    # 4. Signal line = 9-period EMA of MACD line
    # 5. Histogram = MACD line - Signal line

    raise NotImplementedError("MACD calculation not yet implemented")


def detect_macd_crossover(macd: pd.Series, signal: pd.Series) -> str:
    """
    Detect MACD crossover events.

    Args:
        macd: MACD line series
        signal: Signal line series

    Returns:
        str: 'bullish_crossover', 'bearish_crossover', or 'no_crossover'

    Example:
        >>> macd = pd.Series([0.5, 0.3, -0.1, 0.2])
        >>> signal = pd.Series([0.2, 0.4, 0.1, -0.1])
        >>> detect_macd_crossover(macd, signal)
        'bullish_crossover'
    """
    if len(macd) < 2 or len(signal) < 2:
        return "no_crossover"

    # Current and previous values
    macd_curr, macd_prev = macd.iloc[-1], macd.iloc[-2]
    signal_curr, signal_prev = signal.iloc[-1], signal.iloc[-2]

    # Check for crossover
    if macd_prev <= signal_prev and macd_curr > signal_curr:
        return "bullish_crossover"
    elif macd_prev >= signal_prev and macd_curr < signal_curr:
        return "bearish_crossover"

    return "no_crossover"


def interpret_macd(macd: float, signal: float, histogram: float) -> str:
    """
    Interpret MACD values into plain English.

    Args:
        macd: MACD line value
        signal: Signal line value
        histogram: Histogram value

    Returns:
        str: Human-readable interpretation
    """
    if pd.isna(macd) or pd.isna(signal):
        return "Insufficient data"

    if histogram > 0:
        strength = "strong" if abs(histogram) > 1 else "weak"
        return f"Bullish momentum ({strength})"
    elif histogram < 0:
        strength = "strong" if abs(histogram) > 1 else "weak"
        return f"Bearish momentum ({strength})"
    else:
        return "Neutral - no clear momentum"

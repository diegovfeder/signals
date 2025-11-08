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

import polars as pl
import numpy as np
from typing import Tuple
from .ema import calculate_ema

def calculate_macd(
    df: pl.DataFrame,
    fast_period: int = 12,
    slow_period: int = 26,
    signal_period: int = 9,
    price_column: str = "close"
) -> Tuple[pl.Series, pl.Series, pl.Series]:
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
        >>> df = pl.DataFrame({'close': [100, 102, 101, 105, 107, 103, 108]})
        >>> macd, signal, histogram = calculate_macd(df)
        >>> histogram[-1]  # Most recent histogram value
        0.52
    """
    prices = df[price_column].cast(pl.Float64)

    ema_fast = calculate_ema(prices, span=fast_period)
    ema_slow = calculate_ema(prices, span=slow_period)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, span=signal_period)
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram


def detect_macd_crossover(macd: pl.Series, signal: pl.Series) -> str:
    """
    Detect MACD crossover events.

    Args:
        macd: MACD line series
        signal: Signal line series

    Returns:
        str: 'bullish_crossover', 'bearish_crossover', or 'no_crossover'

    Example:
        >>> macd = pl.Series([0.5, 0.3, -0.1, 0.2])
        >>> signal = pl.Series([0.2, 0.4, 0.1, -0.1])
        >>> detect_macd_crossover(macd, signal)
        'bullish_crossover'
    """
    if len(macd) < 2 or len(signal) < 2:
        return "no_crossover"

    # Current and previous values
    macd_curr, macd_prev = macd[-1], macd[-2]
    signal_curr, signal_prev = signal[-1], signal[-2]

    # Check for crossover
    if macd_prev <= signal_prev and macd_curr > signal_curr:
        return "bullish_crossover"
    elif macd_prev >= signal_prev and macd_curr < signal_curr:
        return "bearish_crossover"

    return "no_crossover"


def interpret_macd(macd: float | None, signal: float | None, histogram: float | None) -> str:
    """
    Interpret MACD values into plain English.

    Args:
        macd: MACD line value or None
        signal: Signal line value or None
        histogram: Histogram value or None

    Returns:
        str: Human-readable interpretation
    """
    if macd is None or signal is None or np.isnan(macd) or np.isnan(signal):
        return "Insufficient data"

    if histogram is None:
        histogram = macd - signal

    if histogram > 0:
        strength = "strong" if abs(histogram) > 1 else "weak"
        return f"Bullish momentum ({strength})"
    elif histogram < 0:
        strength = "strong" if abs(histogram) > 1 else "weak"
        return f"Bearish momentum ({strength})"
    else:
        return "Neutral - no clear momentum"

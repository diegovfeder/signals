"""
RSI (Relative Strength Index) Calculation

Formula:
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over period (typically 14)

Interpretation:
    RSI > 70: Overbought (potential SELL signal)
    RSI < 30: Oversold (potential BUY signal)
"""

import pandas as pd
import numpy as np


def calculate_rsi(df: pd.DataFrame, period: int = 14, price_column: str = "close") -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        df: DataFrame with OHLCV data, must have a 'close' column (or specified price_column)
        period: Lookback period for RSI calculation (default: 14)
        price_column: Name of the price column to use (default: 'close')

    Returns:
        pd.Series: RSI values (0-100), NaN for insufficient data

    Example:
        >>> df = pd.DataFrame({'close': [100, 102, 101, 105, 107, 103, 108]})
        >>> rsi = calculate_rsi(df, period=6)
        >>> rsi.iloc[-1]  # Most recent RSI value
        65.43
    """
    # TODO: Implement RSI calculation
    # 1. Calculate price changes (delta)
    # 2. Separate gains (positive changes) and losses (negative changes)
    # 3. Calculate average gain and average loss using EMA or SMA
    # 4. Calculate RS = avg_gain / avg_loss
    # 5. Calculate RSI = 100 - (100 / (1 + RS))

    raise NotImplementedError("RSI calculation not yet implemented")


def interpret_rsi(rsi_value: float) -> str:
    """
    Interpret RSI value into plain English.

    Args:
        rsi_value: RSI value (0-100)

    Returns:
        str: Human-readable interpretation

    Example:
        >>> interpret_rsi(25)
        "Oversold - potential buying opportunity"
    """
    if pd.isna(rsi_value):
        return "Insufficient data"

    if rsi_value > 70:
        return "Overbought - potential selling opportunity"
    elif rsi_value < 30:
        return "Oversold - potential buying opportunity"
    else:
        return "Neutral - no strong signal"

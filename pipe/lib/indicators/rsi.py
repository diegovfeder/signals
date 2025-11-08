"""
RSI (Relative Strength Index) Calculation

Formula:
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss over period (typically 14)

Interpretation:
    RSI > 70: Overbought (potential SELL signal)
    RSI < 30: Oversold (potential BUY signal)
"""

import polars as pl
import numpy as np


def calculate_rsi(df: pl.DataFrame, period: int = 14, price_column: str = "close") -> pl.Series:
    """
    Calculate Relative Strength Index (RSI).

    Args:
        df: DataFrame with OHLCV data, must have a 'close' column (or specified price_column)
        period: Lookback period for RSI calculation (default: 14)
        price_column: Name of the price column to use (default: 'close')

    Returns:
        pl.Series: RSI values (0-100), null for insufficient data

    Example:
        >>> df = pl.DataFrame({'close': [100, 102, 101, 105, 107, 103, 108]})
        >>> rsi = calculate_rsi(df, period=6)
        >>> rsi[-1]  # Most recent RSI value
        65.43
    """
    prices = df[price_column].cast(pl.Float64)

    # Calculate price changes
    delta = prices.diff()

    # Separate gains and losses
    gains = delta.clip(lower_bound=0.0)
    losses = (-delta).clip(lower_bound=0.0)

    # Calculate EMA for gains and losses using Wilder's smoothing
    alpha = 1.0 / period

    # Convert to numpy for EMA calculation
    gains_np = gains.to_numpy()
    losses_np = losses.to_numpy()

    avg_gain = np.zeros_like(gains_np, dtype=float)
    avg_loss = np.zeros_like(losses_np, dtype=float)

    # Initialize with first valid values
    avg_gain[:period] = np.nan
    avg_loss[:period] = np.nan

    if len(gains_np) >= period:
        # Use simple average for first period
        avg_gain[period - 1] = np.nanmean(gains_np[:period])
        avg_loss[period - 1] = np.nanmean(losses_np[:period])

        # Apply EMA for subsequent values
        for i in range(period, len(gains_np)):
            if not np.isnan(gains_np[i]):
                avg_gain[i] = alpha * gains_np[i] + (1 - alpha) * avg_gain[i - 1]
                avg_loss[i] = alpha * losses_np[i] + (1 - alpha) * avg_loss[i - 1]
            else:
                avg_gain[i] = avg_gain[i - 1]
                avg_loss[i] = avg_loss[i - 1]

    # Calculate RS and RSI
    rs = np.where(avg_loss == 0, np.nan, avg_gain / avg_loss)
    rsi = 100 - (100 / (1 + rs))

    return pl.Series(rsi)


def interpret_rsi(rsi_value: float | None) -> str:
    """
    Interpret RSI value into plain English.

    Args:
        rsi_value: RSI value (0-100) or None

    Returns:
        str: Human-readable interpretation

    Example:
        >>> interpret_rsi(25)
        "Oversold - potential buying opportunity"
    """
    if rsi_value is None or np.isnan(rsi_value):
        return "Insufficient data"

    if rsi_value > 70:
        return "Overbought - potential selling opportunity"
    elif rsi_value < 30:
        return "Oversold - potential buying opportunity"
    else:
        return "Neutral - no strong signal"

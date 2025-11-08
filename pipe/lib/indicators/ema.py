import polars as pl
import numpy as np


def calculate_ema(series: pl.Series | list | np.ndarray, span: int) -> pl.Series:
    """Calculate Exponential Moving Average (EMA).

    Args:
        series: Price series (typically close prices) - can be pl.Series, list, or np.ndarray
        span: EMA span (e.g., 12, 26)

    Returns:
        pl.Series: EMA values aligned to the input
    """
    # Convert to polars Series if needed
    if isinstance(series, (list, np.ndarray)):
        series = pl.Series(series)

    if series is None or len(series) == 0:
        return series

    # Calculate alpha (smoothing factor)
    alpha = 2.0 / (span + 1)

    # Convert to numpy for efficient calculation
    values = series.to_numpy()
    ema = np.zeros_like(values, dtype=float)
    ema[0] = values[0]

    # Calculate EMA iteratively
    for i in range(1, len(values)):
        if np.isnan(values[i]):
            ema[i] = ema[i - 1]
        else:
            ema[i] = alpha * values[i] + (1 - alpha) * ema[i - 1]

    return pl.Series(ema)

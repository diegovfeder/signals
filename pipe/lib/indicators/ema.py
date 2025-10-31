import pandas as pd

def calculate_ema(series: pd.Series, span: int) -> pd.Series:
    """Calculate Exponential Moving Average (EMA) using pandas ewm.

    Args:
        series: Price series (typically close prices)
        span: EMA span (e.g., 12, 26)

    Returns:
        pd.Series: EMA values aligned to the input index
    """
    if series is None or len(series) == 0:
        return series
    return series.ewm(span=span, adjust=False).mean()

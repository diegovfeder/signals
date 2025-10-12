"""
Indicator Calculation Flow

Calculate RSI and MACD indicators from market data.
"""

from prefect import flow, task
from typing import List
import pandas as pd


@task(name="fetch-historical-data")
def fetch_historical_data(symbol: str, days: int = 30) -> pd.DataFrame:
    """
    Fetch historical market data for indicator calculation.

    Args:
        symbol: Asset symbol
        days: Number of days of historical data needed

    Returns:
        DataFrame with OHLCV data
    """
    # TODO: Implement database query
    # 1. Connect to database
    # 2. Query market_data table for last N days
    # 3. Return as DataFrame

    raise NotImplementedError("Historical data fetching not yet implemented")


@task(name="calculate-rsi")
def calculate_rsi_indicator(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate RSI indicator.

    Args:
        df: Market data DataFrame
        period: RSI period (default: 14)

    Returns:
        Series with RSI values
    """
    # TODO: Implement RSI calculation
    # 1. Import from data_science.indicators
    # 2. Calculate RSI using close prices
    # 3. Return series

    raise NotImplementedError("RSI calculation not yet implemented")


@task(name="calculate-macd")
def calculate_macd_indicator(df: pd.DataFrame) -> tuple:
    """
    Calculate MACD indicator.

    Args:
        df: Market data DataFrame

    Returns:
        Tuple of (macd, signal, histogram)
    """
    # TODO: Implement MACD calculation
    # 1. Import from data_science.indicators
    # 2. Calculate MACD using close prices
    # 3. Return tuple of series

    raise NotImplementedError("MACD calculation not yet implemented")


@task(name="store-indicators")
def store_indicators(symbol: str, df: pd.DataFrame):
    """
    Store calculated indicators in database.

    Args:
        symbol: Asset symbol
        df: DataFrame with indicators (timestamp, rsi, macd, macd_signal, macd_histogram)
    """
    # TODO: Implement database storage
    # 1. Connect to database
    # 2. Insert data into indicators table
    # 3. Handle duplicates (UPSERT)

    raise NotImplementedError("Indicator storage not yet implemented")


@flow(name="indicator-calculation", log_prints=True)
def indicator_calculation_flow(symbols: List[str] = ["BTC-USD", "ETH-USD", "TSLA"]):
    """
    Main flow: Calculate indicators for all symbols.

    Args:
        symbols: List of symbols to process
    """
    print(f"Starting indicator calculation for {len(symbols)} symbols...")

    for symbol in symbols:
        print(f"Calculating indicators for {symbol}...")

        # Fetch historical data
        historical_data = fetch_historical_data(symbol)

        # Calculate RSI
        rsi = calculate_rsi_indicator(historical_data)

        # Calculate MACD
        macd, macd_signal, macd_histogram = calculate_macd_indicator(historical_data)

        # Combine into DataFrame
        indicators_df = pd.DataFrame({
            'timestamp': historical_data['timestamp'],
            'rsi': rsi,
            'macd': macd,
            'macd_signal': macd_signal,
            'macd_histogram': macd_histogram
        })

        # Store in database
        store_indicators(symbol, indicators_df)

        print(f"✓ Completed {symbol}")

    print("Indicator calculation complete!")


if __name__ == "__main__":
    indicator_calculation_flow()

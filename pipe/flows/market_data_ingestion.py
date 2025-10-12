"""
Market Data Ingestion Flow

Fetch OHLCV data from Yahoo Finance and store in database.
"""

from prefect import flow, task
from typing import List
import pandas as pd


@task(name="fetch-yahoo-finance-data", retries=3, retry_delay_seconds=60)
def fetch_market_data(symbol: str, period: str = "1d", interval: str = "1h") -> pd.DataFrame:
    """
    Fetch market data from Yahoo Finance.

    Args:
        symbol: Asset symbol (e.g., 'BTC-USD')
        period: Time period to fetch (e.g., '1d', '7d')
        interval: Data interval (e.g., '1h', '1d')

    Returns:
        DataFrame with OHLCV data
    """
    # TODO: Implement Yahoo Finance data fetching
    # 1. Use yfinance library to fetch data
    # 2. Return DataFrame with columns: timestamp, open, high, low, close, volume

    raise NotImplementedError("Market data fetching not yet implemented")


@task(name="validate-market-data")
def validate_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate market data quality.

    Args:
        df: Raw market data

    Returns:
        Validated DataFrame

    Raises:
        ValueError: If data quality checks fail
    """
    # TODO: Implement data validation
    # 1. Check for missing values
    # 2. Validate OHLC relationships
    # 3. Check volume is non-negative
    # 4. Raise error if validation fails

    raise NotImplementedError("Data validation not yet implemented")


@task(name="store-market-data")
def store_to_database(symbol: str, df: pd.DataFrame):
    """
    Store market data in PostgreSQL database.

    Args:
        symbol: Asset symbol
        df: Validated market data
    """
    # TODO: Implement database storage
    # 1. Connect to database
    # 2. Insert data into market_data table
    # 3. Handle duplicates (UPSERT)
    # 4. Close connection

    raise NotImplementedError("Database storage not yet implemented")


@flow(name="market-data-ingestion", log_prints=True)
def market_data_ingestion_flow(symbols: List[str] = ["BTC-USD", "ETH-USD", "TSLA"]):
    """
    Main flow: Ingest market data for all symbols.

    Args:
        symbols: List of symbols to fetch (default: MVP 3 symbols)
    """
    print(f"Starting market data ingestion for {len(symbols)} symbols...")

    for symbol in symbols:
        print(f"Fetching data for {symbol}...")

        # Fetch data from Yahoo Finance
        raw_data = fetch_market_data(symbol)

        # Validate data quality
        validated_data = validate_data(raw_data)

        # Store in database
        store_to_database(symbol, validated_data)

        print(f"✓ Completed {symbol}")

    print("Market data ingestion complete!")


if __name__ == "__main__":
    # For manual testing
    market_data_ingestion_flow()

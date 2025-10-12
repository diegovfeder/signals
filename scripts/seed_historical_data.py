"""
Seed Historical Data Script

Backfill 30 days of historical market data for all symbols.
"""

import os
import sys
from datetime import datetime, timedelta
import yfinance as yf
import psycopg2
from psycopg2.extras import execute_values


def get_database_url():
    """Get database URL from environment."""
    return os.getenv('DATABASE_URL', 'postgresql://signals_user:signals_password@localhost:5432/trading_signals')


def fetch_historical_data(symbol: str, days: int = 30):
    """
    Fetch historical data from Yahoo Finance.

    Args:
        symbol: Asset symbol (e.g., 'BTC-USD')
        days: Number of days to backfill

    Returns:
        DataFrame with OHLCV data
    """
    print(f"Fetching {days} days of data for {symbol}...")

    ticker = yf.Ticker(symbol)
    df = ticker.history(period=f"{days}d", interval="1h")

    if df.empty:
        raise ValueError(f"No data returned for {symbol}")

    print(f"✓ Fetched {len(df)} candles")
    return df


def insert_market_data(cursor, symbol: str, df):
    """Insert market data into database."""
    print(f"Inserting data into database...")

    # Prepare data for insertion
    data = [
        (
            symbol,
            row.Index,
            float(row.Open),
            float(row.High),
            float(row.Low),
            float(row.Close),
            int(row.Volume)
        )
        for row in df.itertuples()
    ]

    # Insert with ON CONFLICT to handle duplicates
    query = """
        INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume)
        VALUES %s
        ON CONFLICT (symbol, timestamp) DO NOTHING
    """

    execute_values(cursor, query, data)
    print(f"✓ Inserted {len(data)} records")


def seed_historical_data():
    """Seed historical data for all symbols."""
    print("=" * 60)
    print("Trading Signals - Seed Historical Data")
    print("=" * 60)

    symbols = ['BTC-USD', 'ETH-USD', 'TSLA']
    days = 30

    try:
        # Connect to database
        db_url = get_database_url()
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        print("✓ Connected to database\n")

        # Fetch and insert data for each symbol
        for symbol in symbols:
            print(f"\nProcessing {symbol}...")
            print("-" * 60)

            try:
                df = fetch_historical_data(symbol, days)
                insert_market_data(cursor, symbol, df)
                conn.commit()
                print(f"✓ Completed {symbol}")
            except Exception as e:
                print(f"✗ Error processing {symbol}: {e}")
                conn.rollback()

        # Close connection
        cursor.close()
        conn.close()

        print("\n" + "=" * 60)
        print("✓ Historical data seeding complete!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import yfinance
        import psycopg2
    except ImportError as e:
        print("Missing required package. Install with:")
        print("  pip install yfinance psycopg2-binary")
        sys.exit(1)

    seed_historical_data()

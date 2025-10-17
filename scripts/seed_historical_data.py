"""
Seed Historical Data Script

Backfill historical market data for all MVP symbols.
Yahoo Finance limits 15m data to ~60 days, so we fetch maximum available.
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


def fetch_historical_data(symbol: str):
    """
    Fetch maximum available 15-minute historical data from Yahoo Finance.

    Note: Yahoo Finance limits 15m interval data to approximately 60 days.
    For longer historical periods, use daily data separately.

    Args:
        symbol: Asset symbol (e.g., 'BTC-USD', 'AAPL', 'IVV', 'BRL=X')

    Returns:
        DataFrame with OHLCV data (15-minute bars)
    """
    print(f"Fetching 15m data for {symbol}...")

    ticker = yf.Ticker(symbol)

    # Fetch maximum available 15-minute data
    # Yahoo Finance typically provides ~60 days for 15m interval
    df = ticker.history(period="60d", interval="15m")

    if df.empty:
        print(f"⚠ No 15m data available for {symbol}, trying 1h interval...")
        # Fallback to hourly data if 15m not available (e.g., some forex pairs)
        df = ticker.history(period="60d", interval="1h")

        if df.empty:
            raise ValueError(f"No data returned for {symbol}")

    # Get actual date range
    start_date = df.index.min()
    end_date = df.index.max()
    days = (end_date - start_date).days

    print(f"✓ Fetched {len(df)} candles ({days} days: {start_date.date()} to {end_date.date()})")
    return df


def insert_market_data(cursor, symbol: str, df):
    """Insert market data into database."""
    print(f"Inserting data into database...")

    # Ensure index is timezone-aware (convert to UTC if needed)
    if df.index.tz is None:
        # If timezone-naive, assume UTC
        df.index = df.index.tz_localize('UTC')
    else:
        # Convert to UTC if in a different timezone
        df.index = df.index.tz_convert('UTC')

    # Prepare data for insertion
    data = [
        (
            symbol,
            timestamp,  # Use timestamp directly from index
            float(row.Open),
            float(row.High),
            float(row.Low),
            float(row.Close),
            int(row.Volume)
        )
        for timestamp, row in df.iterrows()  # Use iterrows() to get index explicitly
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
    """Seed historical data for all MVP symbols."""
    print("=" * 60)
    print("Trading Signals - Seed Historical Data")
    print("=" * 60)

    # MVP: 4 assets across different classes
    symbols = ['BTC-USD', 'AAPL', 'IVV', 'BRL=X']

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
                df = fetch_historical_data(symbol)
                insert_market_data(cursor, symbol, df)
                conn.commit()
                print(f"✓ Completed {symbol}")
            except Exception as e:
                print(f"✗ Error processing {symbol}: {e}")
                conn.rollback()
                continue  # Continue with next symbol

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

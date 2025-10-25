"""
Seed MVP data directly into database using mock OHLCV data.
This bypasses Yahoo Finance API issues and lets us test the full stack.
"""
import os
import psycopg
from datetime import datetime, timedelta, timezone
import random

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quantmaster:buysthedip@localhost:5432/signals")

# Mock OHLCV data generator
def generate_mock_ohlcv(symbol: str, num_bars: int = 50):
    """Generate realistic-looking OHLCV data"""
    base_prices = {
        "BTC-USD": 45000,
        "AAPL": 180,
        "IVV": 450,
        "BRL=X": 5.0
    }

    base_price = base_prices.get(symbol, 100)
    now = datetime.now(timezone.utc)

    bars = []
    price = base_price

    for i in range(num_bars):
        ts = now - timedelta(minutes=15 * (num_bars - i))

        # Random walk with slight trend
        change_pct = random.uniform(-0.02, 0.025)  # -2% to +2.5%
        price = price * (1 + change_pct)

        # Generate OHLC from price
        high = price * random.uniform(1.001, 1.01)
        low = price * random.uniform(0.99, 0.999)
        open_price = random.uniform(low, high)
        close = random.uniform(low, high)
        volume = random.randint(1000000, 10000000)

        bars.append({
            "symbol": symbol,
            "timestamp": ts,
            "open": round(open_price, 2),
            "high": round(high, 2),
            "low": round(low, 2),
            "close": round(close, 2),
            "volume": volume
        })

    return bars

def seed_market_data():
    """Insert mock market data for all 4 symbols"""
    symbols = ["BTC-USD", "AAPL", "IVV", "BRL=X"]

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            total_inserted = 0

            for symbol in symbols:
                print(f"Generating data for {symbol}...")
                bars = generate_mock_ohlcv(symbol, num_bars=50)

                for bar in bars:
                    try:
                        cur.execute(
                            """
                            INSERT INTO market_data (symbol, timestamp, open, high, low, close, volume)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (symbol, timestamp) DO NOTHING
                            """,
                            (bar["symbol"], bar["timestamp"], bar["open"], bar["high"],
                             bar["low"], bar["close"], bar["volume"])
                        )
                        total_inserted += cur.rowcount
                    except Exception as e:
                        print(f"Error inserting {symbol} at {bar['timestamp']}: {e}")

                conn.commit()
                print(f"✓ {symbol}: {len(bars)} bars generated")

            print(f"\nTotal market_data rows inserted: {total_inserted}")

            # Verify
            cur.execute("SELECT symbol, COUNT(*) as cnt FROM market_data GROUP BY symbol ORDER BY symbol")
            results = cur.fetchall()
            print("\nMarket data counts:")
            for row in results:
                print(f"  {row[0]}: {row[1]} bars")

if __name__ == "__main__":
    print("Seeding MVP database with mock OHLCV data...\n")
    seed_market_data()
    print("\n✓ Database seeded successfully!")
    print("Next: Run calculate indicators and generate signals")

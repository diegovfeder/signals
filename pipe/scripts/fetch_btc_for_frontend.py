#!/usr/bin/env python3
"""
Fetch 2 years of BTC-USD data from Yahoo Finance for frontend chart.
No database required - outputs TypeScript file directly.
"""
import sys
from pathlib import Path

# Add pipe to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lib.api.yahoo import fetch_daily
from datetime import datetime


def main():
    print("Fetching 2 years of BTC-USD data from Yahoo Finance...")

    # Fetch data
    df = fetch_daily("BTC-USD", range_days=730)

    print(f"✓ Fetched {len(df)} rows")
    print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Latest price: ${df['close'].tail(1).item():,.2f}")

    # Convert to list of dicts
    data = df.select(["timestamp", "close", "volume"]).to_dicts()

    # Generate TypeScript file
    output_path = (
        Path(__file__).parent.parent.parent
        / "frontend"
        / "src"
        / "lib"
        / "data"
        / "btc-market-data.ts"
    )

    with open(output_path, "w") as f:
        f.write("export interface MarketDataPoint {\n")
        f.write("  date: string;\n")
        f.write("  close: number;\n")
        f.write("  volume: number;\n")
        f.write("}\n\n")
        f.write("/**\n")
        f.write(" * Real BTC-USD market data from Yahoo Finance\n")
        f.write(
            f' * Date range: {df["timestamp"].min()} to {df["timestamp"].max()}\n'
        )
        f.write(f" * Data points: {len(df)}\n")
        f.write(f' * Generated: {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}\n')
        f.write(" */\n")
        f.write("export const BTC_TWO_YEAR_DATA: MarketDataPoint[] = [\n")

        for i, row in enumerate(data):
            # Format timestamp as YYYY-MM-DD
            date_str = row["timestamp"].strftime("%Y-%m-%d")
            close = row["close"]
            volume = int(row["volume"])
            comma = "," if i < len(data) - 1 else ""
            f.write(
                f'  {{ date: "{date_str}", close: {close}, volume: {volume} }}{comma}\n'
            )

        f.write("];\n")

    print(f"\n✓ Generated {output_path}")
    print(f"✓ Latest price in data: ${df['close'].tail(1).item():,.2f}")


if __name__ == "__main__":
    main()

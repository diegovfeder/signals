"""
Signal Generation Flow

Generate BUY/SELL/HOLD signals from technical indicators.
"""

from prefect import flow, task
from typing import List, Dict


@task(name="fetch-latest-indicators")
def fetch_latest_indicators(symbol: str) -> Dict:
    """
    Fetch the most recent indicators for a symbol.

    Args:
        symbol: Asset symbol

    Returns:
        dict with latest RSI, MACD values and current price
    """
    # TODO: Implement database query
    # 1. Query indicators table for latest values
    # 2. Query market_data for latest price
    # 3. Return combined dict

    raise NotImplementedError("Indicator fetching not yet implemented")


@task(name="generate-trading-signal")
def generate_signal(symbol: str, indicators: Dict) -> Dict:
    """
    Generate trading signal from indicators.

    Args:
        symbol: Asset symbol
        indicators: Latest indicator values

    Returns:
        dict with signal_type, strength, reasoning, price
    """
    # TODO: Implement signal generation
    # 1. Import from data_science.signals
    # 2. Generate signal using indicators
    # 3. Calculate signal strength
    # 4. Return signal dict

    raise NotImplementedError("Signal generation not yet implemented")


@task(name="store-signal")
def store_signal(symbol: str, signal: Dict):
    """
    Store generated signal in database.

    Args:
        symbol: Asset symbol
        signal: Generated signal dict
    """
    # TODO: Implement database storage
    # 1. Connect to database
    # 2. Insert into signals table
    # 3. Include timestamp, signal_type, strength, reasoning, price

    raise NotImplementedError("Signal storage not yet implemented")


@flow(name="signal-generation", log_prints=True)
def signal_generation_flow(symbols: List[str] = ["BTC-USD", "ETH-USD", "TSLA"]):
    """
    Main flow: Generate trading signals for all symbols.

    Args:
        symbols: List of symbols to process
    """
    print(f"Starting signal generation for {len(symbols)} symbols...")

    for symbol in symbols:
        print(f"Generating signal for {symbol}...")

        # Fetch latest indicators
        indicators = fetch_latest_indicators(symbol)

        # Generate trading signal
        signal = generate_signal(symbol, indicators)

        # Store signal in database
        store_signal(symbol, signal)

        print(f"✓ {symbol}: {signal['signal_type']} (strength: {signal['strength']}/100)")

    print("Signal generation complete!")


if __name__ == "__main__":
    signal_generation_flow()

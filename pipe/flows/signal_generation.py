"""
Intraday signal generation flow.

Fetches the latest intraday data, updates indicators, and generates BUY/SELL/HOLD
signals for the configured symbols.
"""

from __future__ import annotations

import argparse
from typing import List, Optional

from prefect import flow

from tasks.market_data import fetch_intraday_ohlcv, resolve_symbols, upsert_market_data
from tasks.indicators import calculate_and_upsert_indicators
from tasks.signals import generate_and_store_signal, notify_if_strong


@flow(name="signal-generation", log_prints=True)
def signal_generation_flow(
    symbols: Optional[List[str]] = None,
    indicator_window: Optional[int] = 600,
    intraday_interval: str = "15m",
):
    target_symbols = resolve_symbols(symbols)

    indicator_window_value = indicator_window if (indicator_window is None or indicator_window > 0) else None

    print(f"Starting intraday signal generation for {len(target_symbols)} symbols...")

    for symbol in target_symbols:
        try:
            print(f"[intraday] Processing {symbol} ({intraday_interval})...")
            ohlcv = fetch_intraday_ohlcv(symbol, interval=intraday_interval)
            upserted = upsert_market_data(ohlcv)
            print(f"[intraday] Upserted {upserted} intraday rows for {symbol}")
            rsi, ema12, ema26, macd_hist, price, ts = calculate_and_upsert_indicators(
                symbol, window=indicator_window_value
            )
            result = generate_and_store_signal(symbol, rsi, ema12, ema26, macd_hist, price, ts)
            notify_if_strong(result)
            print(f"✓ {symbol}: {result['signal_type']} ({result['strength']}/100)")
        except Exception as exc:
            print(f"✗ Error for {symbol}: {exc}")

    print("Signal generation complete!")


def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Run the intraday signal generation Prefect flow.")
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of symbols to process (defaults to env SIGNAL_SYMBOLS or built-in list).",
    )
    parser.add_argument(
        "--indicator-window",
        type=int,
        default=600,
        help="Number of rows to use when recalculating indicators (set to 0 to use entire history).",
    )
    parser.add_argument(
        "--intraday-interval",
        type=str,
        default="15m",
        help="Alpha Vantage intraday interval (e.g., 5m, 15m).",
    )
    args = parser.parse_args()
    resolved_symbols = (
        [sym.strip() for sym in args.symbols.split(",") if sym.strip()] if args.symbols else None
    )
    return resolved_symbols, args.indicator_window, args.intraday_interval


if __name__ == "__main__":
    cli_symbols, cli_indicator_window, cli_interval = _parse_cli_args()
    signal_generation_flow(
        symbols=cli_symbols,
        indicator_window=cli_indicator_window,
        intraday_interval=cli_interval,
    )

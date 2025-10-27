"""
Historical backfill flow.

Fetches multi-year daily OHLCV data for each symbol and recomputes indicators.
"""

from __future__ import annotations

import argparse
from typing import List, Optional

from prefect import flow

from tasks.market_data import (
    fetch_historical_ohlcv,
    resolve_history_days,
    resolve_symbols,
    upsert_market_data,
    HISTORICAL_RANGE_MAP,
)
from tasks.indicators import calculate_and_upsert_indicators


@flow(name="historical-backfill", log_prints=True)
def historical_backfill_flow(
    symbols: Optional[List[str]] = None,
    backfill_days: Optional[int] = None,
    backfill_range: str = "2y",
):
    target_symbols = resolve_symbols(symbols)
    days = backfill_days if backfill_days is not None else resolve_history_days(None, backfill_range)
    if days is None:
        raise ValueError("Backfill requires --backfill-days or --backfill-range/BACKFILL_RANGE env var.")

    print(f"Starting historical backfill for {len(target_symbols)} symbols (~{days} days)...")
    for symbol in target_symbols:
        try:
            history = fetch_historical_ohlcv(symbol, days)
            inserted = upsert_market_data(history) if not history.empty else 0
            calculate_and_upsert_indicators(symbol, window=None)
            print(f"✓ {symbol}: stored {inserted} rows and refreshed indicators.")
        except Exception as exc:
            print(f"✗ Error backfilling {symbol}: {exc}")

    print("Historical backfill complete!")


def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Run the historical backfill Prefect flow.")
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of symbols to backfill (defaults to env SIGNAL_SYMBOLS or built-in list).",
    )
    parser.add_argument(
        "--backfill-days",
        type=int,
        help="Number of days of historical data to fetch.",
    )
    parser.add_argument(
        "--backfill-range",
        type=str,
        default="2y",
        choices=sorted(HISTORICAL_RANGE_MAP.keys()),
        help="Named range (e.g., 1y, 2y) to fetch when --backfill-days is not provided.",
    )
    args = parser.parse_args()
    resolved_symbols = (
        [sym.strip() for sym in args.symbols.split(",") if sym.strip()] if args.symbols else None
    )
    resolved_days = resolve_history_days(args.backfill_days, args.backfill_range)
    return resolved_symbols, resolved_days, args.backfill_range


if __name__ == "__main__":
    cli_symbols, cli_days, cli_range = _parse_cli_args()
    historical_backfill_flow(symbols=cli_symbols, backfill_days=cli_days, backfill_range=cli_range)

"""
Market Data Sync Flow.

Fetches the latest daily OHLCV bar for all tracked symbols.
Runs nightly at 10 PM UTC to capture end-of-day data.
"""

from __future__ import annotations

import argparse

from prefect import flow, get_run_logger

try:
    from tasks.market_data import (
        fetch_historical_ohlcv,
        resolve_symbols,
        upsert_market_data,
    )
    from tasks.indicators import calculate_and_upsert_indicators
except ImportError:
    from pipe.tasks.market_data import (
        fetch_historical_ohlcv,
        resolve_symbols,
        upsert_market_data,
    )
    from pipe.tasks.indicators import calculate_and_upsert_indicators


@flow(name="market-data-sync", log_prints=True)
def market_data_sync_flow(
    symbols: list[str] | None = None,
):
    """Fetch the latest daily bar for each symbol and update indicators."""
    logger = get_run_logger()
    target_symbols = resolve_symbols(symbols)

    logger.info("Starting daily market data sync for %d symbol(s).", len(target_symbols))

    for symbol in target_symbols:
        try:
            logger.info("Syncing recent bars for %s.", symbol)
            # Fetch last 5 days to ensure we get the latest bar
            # (in case of weekends/holidays)
            history = fetch_historical_ohlcv(symbol, range_days=5)

            if history.empty:
                logger.warning("%s: No data returned during sync.", symbol)
                continue

            inserted = upsert_market_data(history)

            # Recalculate indicators with latest data
            calculate_and_upsert_indicators(symbol, window=None)

            latest_date = history["timestamp"].max() if not history.empty else None
            logger.info("%s sync complete: inserted=%d rows, latest_timestamp=%s.", symbol, inserted, latest_date)

        except Exception as exc:
            logger.exception("Error syncing %s: %s", symbol, exc)

    logger.info("Daily market data sync complete.")


def _parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Sync the latest daily OHLCV data for tracked symbols."
    )
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of symbols (defaults to env SIGNAL_SYMBOLS or built-in list).",
    )
    args = parser.parse_args()
    resolved_symbols = (
        [sym.strip() for sym in args.symbols.split(",") if sym.strip()] if args.symbols else None
    )
    return resolved_symbols


if __name__ == "__main__":
    cli_symbols = _parse_cli_args()
    market_data_sync_flow(symbols=cli_symbols)

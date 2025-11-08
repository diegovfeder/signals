"""
Market Data Backfill Flow.

Fetches multi-year daily OHLCV history for new symbols.
Used when onboarding new assets to populate initial historical data.
"""

from __future__ import annotations

import argparse

from prefect import flow, get_run_logger

try:
    from tasks.market_data import (
        fetch_historical_ohlcv,
        resolve_history_days,
        resolve_symbols,
        upsert_market_data,
        HISTORICAL_RANGE_MAP,
    )
    from tasks.indicators import calculate_and_upsert_indicators
except ImportError:
    from pipe.tasks.market_data import (
        fetch_historical_ohlcv,
        resolve_history_days,
        resolve_symbols,
        upsert_market_data,
        HISTORICAL_RANGE_MAP,
    )
    from pipe.tasks.indicators import calculate_and_upsert_indicators


@flow(name="market-data-backfill", log_prints=True)
def market_data_backfill_flow(
    symbols: list[str] | None = None,
    backfill_days: int | None = None,
    backfill_range: str = "5y",
):
    logger = get_run_logger()

    target_symbols = resolve_symbols(symbols)
    days = backfill_days if backfill_days is not None else resolve_history_days(None, backfill_range)
    if days is None:
        raise ValueError("Backfill requires --backfill-days or --backfill-range/BACKFILL_RANGE env var.")

    logger.info(
        "Starting historical backfill for %d symbol(s) over ~%d day window (range=%s).",
        len(target_symbols),
        days,
        backfill_range,
    )
    for symbol in target_symbols:
        try:
            logger.info("Fetching historical OHLCV for %s.", symbol)
            history = fetch_historical_ohlcv(symbol, days)
            has_rows = history.height > 0
            inserted = upsert_market_data(history) if has_rows else 0
            calculate_and_upsert_indicators(symbol, window=None)
            logger.info("Completed backfill for %s: inserted=%d rows, indicators refreshed.", symbol, inserted)
        except Exception as exc:
            logger.exception("Error backfilling %s: %s", symbol, exc)

    logger.info("Historical backfill complete.")


def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Backfill multi-year market data for new symbols.")
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
        default="5y",
        choices=sorted(HISTORICAL_RANGE_MAP.keys()),
        help=(
            "Named range (e.g., 1y, 5y, 10y) to fetch when --backfill-days is not provided. "
            "Matches HISTORICAL_RANGE_MAP entries."
        ),
    )
    args = parser.parse_args()
    resolved_symbols = (
        [sym.strip() for sym in args.symbols.split(",") if sym.strip()] if args.symbols else None
    )
    resolved_days = resolve_history_days(args.backfill_days, args.backfill_range)
    return resolved_symbols, resolved_days, args.backfill_range


if __name__ == "__main__":
    cli_symbols, cli_days, cli_range = _parse_cli_args()
    market_data_backfill_flow(symbols=cli_symbols, backfill_days=cli_days, backfill_range=cli_range)

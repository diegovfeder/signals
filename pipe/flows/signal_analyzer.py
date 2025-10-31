"""
Signal Analyzer Flow.

Analyzes existing daily OHLCV data and generates BUY/SELL/HOLD signals.
Does NOT fetch new data - assumes market_data_sync has already run.
"""

from __future__ import annotations

import argparse

from prefect import flow, get_run_logger

try:
    from tasks.market_data import resolve_symbols
    from tasks.indicators import calculate_and_upsert_indicators
    from tasks.signals import generate_and_store_signal
except ImportError:
    from pipe.tasks.market_data import resolve_symbols
    from pipe.tasks.indicators import calculate_and_upsert_indicators
    from pipe.tasks.signals import generate_and_store_signal


@flow(name="signal-analyzer", log_prints=True)
def signal_analyzer_flow(
    symbols: list[str] | None = None,
    indicator_window: int | None = 600,
):
    """
    Generate trading signals from existing market data.

    This flow assumes market_data_sync has already populated the database
    with the latest daily OHLCV bars.
    """
    logger = get_run_logger()
    target_symbols = resolve_symbols(symbols)
    indicator_window_value = indicator_window if (indicator_window is None or indicator_window > 0) else None

    logger.info(
        "Starting signal analysis for %d symbol(s) using window=%s.",
        len(target_symbols),
        indicator_window_value if indicator_window_value is not None else "full-history",
    )

    for symbol in target_symbols:
        try:
            logger.info("Analyzing %s.", symbol)

            # Calculate indicators from existing DB data
            rsi, ema12, ema26, macd_hist, price, ts = calculate_and_upsert_indicators(
                symbol, window=indicator_window_value
            )

            # Generate and store signal
            result = generate_and_store_signal(symbol, rsi, ema12, ema26, macd_hist, price, ts)

            signal_emoji = "🟢" if result['signal_type'] == "BUY" else "🔵" if result['signal_type'] == "HOLD" else "🔴"
            price_at_signal = result.get("price")
            logger.info(
                "%s %s signal generated: type=%s strength=%s/100 price=%.2f timestamp=%s",
                signal_emoji,
                symbol,
                result["signal_type"],
                result["strength"],
                float(price_at_signal) if price_at_signal is not None else float("nan"),
                result["at"],
            )

        except Exception as exc:
            logger.exception("Error analyzing %s: %s", symbol, exc)

    logger.info("Signal analysis complete.")


def _parse_cli_args():
    parser = argparse.ArgumentParser(
        description="Analyze market data and generate trading signals."
    )
    parser.add_argument(
        "--symbols",
        type=str,
        help="Comma-separated list of symbols to analyze (defaults to env SIGNAL_SYMBOLS or built-in list).",
    )
    parser.add_argument(
        "--indicator-window",
        type=int,
        default=600,
        help="Number of rows to use when recalculating indicators (set to 0 to use entire history).",
    )
    args = parser.parse_args()
    resolved_symbols = (
        [sym.strip() for sym in args.symbols.split(",") if sym.strip()] if args.symbols else None
    )
    return resolved_symbols, args.indicator_window


if __name__ == "__main__":
    cli_symbols, cli_indicator_window = _parse_cli_args()
    signal_analyzer_flow(
        symbols=cli_symbols,
        indicator_window=cli_indicator_window,
    )

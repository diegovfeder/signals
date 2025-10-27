"""
Historical signal replay & backtest flow.

Iterates over stored indicator + price history, regenerates signals for each bar,
stores them (idempotently) and computes simple performance metrics for the backtest UI.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Sequence

import pandas as pd
from prefect import flow

from tasks.market_data import resolve_symbols
from tasks.signals import generate_and_store_signal
from tasks.db import get_db_conn


def _parse_date(value: Optional[str], default: datetime) -> datetime:
    if not value:
        return default
    clean = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(clean)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def _fetch_indicator_history(symbol: str, start: datetime, end: datetime) -> pd.DataFrame:
    query = """
        SELECT m.timestamp, m.close, i.rsi, i.ema_12, i.ema_26, i.macd_histogram
        FROM indicators i
        JOIN market_data m
          ON i.symbol = m.symbol
         AND i.timestamp = m.timestamp
        WHERE i.symbol = %s
          AND i.timestamp BETWEEN %s AND %s
        ORDER BY i.timestamp ASC
    """
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(query, (symbol, start, end))
        rows = cur.fetchall()
    if not rows:
        return pd.DataFrame(
            columns=["timestamp", "close", "rsi", "ema_12", "ema_26", "macd_histogram"]
        )
    df = pd.DataFrame(rows, columns=["timestamp", "close", "rsi", "ema_12", "ema_26", "macd_histogram"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
    df["close"] = df["close"].astype(float)
    return df


def _compute_backtest_metrics(rows: Sequence[dict], signal_types: Sequence[str]) -> dict:
    returns: List[float] = []
    position_entry: Optional[float] = None
    entry_index: Optional[int] = None

    for idx, signal in enumerate(signal_types):
        price = rows[idx]["close"]
        if signal == "BUY":
            if position_entry is None and price is not None:
                position_entry = price
                entry_index = idx
        elif signal == "SELL" and position_entry is not None:
            if position_entry != 0:
                returns.append((price - position_entry) / position_entry * 100.0)
            position_entry = None
            entry_index = None

    if position_entry is not None and rows and entry_index is not None:
        fallback_index = entry_index + 1
        if fallback_index >= len(rows):
            fallback_index = len(rows) - 1
        exit_price = rows[fallback_index]["close"]
        if position_entry != 0 and exit_price is not None:
            returns.append((exit_price - position_entry) / position_entry * 100.0)
        position_entry = None
        entry_index = None

    trades = len(returns)
    if trades == 0:
        return {"trades": 0, "win_rate": 0.0, "avg_return": 0.0, "total_return": 0.0}

    wins = len([ret for ret in returns if ret > 0])
    win_rate = (wins / trades) * 100.0
    avg_return = sum(returns) / trades
    total_return = sum(returns)
    return {
        "trades": trades,
        "win_rate": win_rate,
        "avg_return": avg_return,
        "total_return": total_return,
    }


def _upsert_backtest_summary(
    symbol: str,
    range_label: str,
    start_ts: datetime,
    end_ts: datetime,
    metrics: dict,
    rule_version: str,
) -> None:
    query = """
        INSERT INTO backtests
            (symbol, range_label, start_timestamp, end_timestamp, trades, win_rate, avg_return, total_return, rule_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (symbol, range_label, rule_version)
        DO UPDATE SET
            start_timestamp = EXCLUDED.start_timestamp,
            end_timestamp = EXCLUDED.end_timestamp,
            trades = EXCLUDED.trades,
            win_rate = EXCLUDED.win_rate,
            avg_return = EXCLUDED.avg_return,
            total_return = EXCLUDED.total_return,
            generated_at = NOW()
    """
    with get_db_conn() as conn, conn.cursor() as cur:
        cur.execute(
            query,
            (
                symbol,
                range_label,
                start_ts,
                end_ts,
                metrics["trades"],
                metrics["win_rate"],
                metrics["avg_return"],
                metrics["total_return"],
                rule_version,
            ),
        )
        conn.commit()


@flow(name="historical-signal-replay", log_prints=True)
def signal_replay_flow(
    symbols: Optional[List[str]] = None,
    start: Optional[str] = None,
    end: Optional[str] = None,
    range_label: str = "1y",
    rule_version: str = "strategy_registry_v1",
):
    now = datetime.now(timezone.utc)
    default_start = now - timedelta(days=365)
    start_ts = _parse_date(start, default_start)
    end_ts = _parse_date(end, now)
    target_symbols = resolve_symbols(symbols)

    print(
        f"Starting signal replay for {len(target_symbols)} symbols "
        f"({start_ts.isoformat()} → {end_ts.isoformat()}, range={range_label})"
    )

    for symbol in target_symbols:
        history = _fetch_indicator_history(symbol, start_ts, end_ts)
        if history.empty:
            print(f"✗ No indicator history for {symbol} in the selected window.")
            continue

        signal_types: List[str] = []
        for _, row in history.iterrows():
            result = generate_and_store_signal.fn(
                symbol=symbol,
                rsi=float(row["rsi"]) if row["rsi"] is not None else 50.0,
                ema12=float(row["ema_12"]) if row["ema_12"] is not None else float(row["close"]),
                ema26=float(row["ema_26"]) if row["ema_26"] is not None else float(row["close"]),
                macd_hist=float(row["macd_histogram"]) if row["macd_histogram"] is not None else 0.0,
                price=float(row["close"]),
                ts=row["timestamp"].to_pydatetime(),
            )
            signal_types.append(result["signal_type"])

        metrics = _compute_backtest_metrics(history.to_dict("records"), signal_types)
        _upsert_backtest_summary(
            symbol,
            range_label,
            history["timestamp"].iloc[0].to_pydatetime(),
            history["timestamp"].iloc[-1].to_pydatetime(),
            metrics,
            rule_version,
        )
        print(
            f"✓ {symbol}: trades={metrics['trades']} win_rate={metrics['win_rate']:.2f}% "
            f"avg_return={metrics['avg_return']:.2f}% total_return={metrics['total_return']:.2f}%"
        )

    print("Signal replay complete!")


def _parse_cli_args():
    parser = argparse.ArgumentParser(description="Replay historical signals and compute backtest summaries.")
    parser.add_argument("--symbols", type=str, help="Comma-separated list of symbols to process.")
    parser.add_argument("--start", type=str, help="ISO timestamp for the start of the window (default: 1 year ago).")
    parser.add_argument("--end", type=str, help="ISO timestamp for the end of the window (default: now).")
    parser.add_argument(
        "--range-label",
        type=str,
        default="1y",
        help="Label stored with the backtest summary (e.g., 1y, 2y, custom).",
    )
    parser.add_argument(
        "--rule-version",
        type=str,
        default="strategy_registry_v1",
        help="Rule version stored with the backtest summary.",
    )
    args = parser.parse_args()
    resolved_symbols = (
        [sym.strip() for sym in args.symbols.split(",") if sym.strip()] if args.symbols else None
    )
    return resolved_symbols, args.start, args.end, args.range_label, args.rule_version


if __name__ == "__main__":
    cli_symbols, cli_start, cli_end, cli_range, cli_rule = _parse_cli_args()
    signal_replay_flow(
        symbols=cli_symbols,
        start=cli_start,
        end=cli_end,
        range_label=cli_range,
        rule_version=cli_rule,
    )

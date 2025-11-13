"""Interactive strategy lab powered by Marimo."""

from __future__ import annotations

import marimo as mo

__generated_with = "0.7.9"

app = mo.App(width="full")


@app.cell
def __():
    import marimo as mo

    return mo


@app.cell
def __():
    from datetime import datetime, timedelta, timezone

    import polars as pl
    import plotly.graph_objects as go

    from notebook_helpers.db import fetch_price_history, list_symbols
    from notebook_helpers.strategies import (
        available_strategy_keys,
        default_strategy_key_for_symbol,
        evaluate_strategy,
        get_strategy,
        parameters_for,
    )

    return (
        available_strategy_keys,
        datetime,
        evaluate_strategy,
        fetch_price_history,
        get_strategy,
        list_symbols,
        parameters_for,
        pl,
        go,
        timedelta,
        timezone,
        default_strategy_key_for_symbol,
    )


@app.cell
def __(list_symbols):
    symbols = list_symbols()
    if not symbols:
        raise RuntimeError(
            "No symbols available. Ensure the database is seeded and accessible."
        )
    return symbols


@app.cell
def __(mo, symbols, available_strategy_keys, default_strategy_key_for_symbol):
    symbol_picker = mo.ui.dropdown(symbols, label="Symbol", value=symbols[0])
    strategy_options = available_strategy_keys()
    default_strategy = default_strategy_key_for_symbol(symbols[0])
    strategy_picker = mo.ui.dropdown(
        strategy_options,
        label="Strategy",
        value=default_strategy if default_strategy in strategy_options else strategy_options[0],
    )
    lookback = mo.ui.slider(30, 365, label="Lookback (days)", value=90)
    return symbol_picker, strategy_picker, lookback


@app.cell
def __(mo, parameters_for, strategy_picker):
    parameter_widgets: dict[str, object] = {}
    for parameter in parameters_for(strategy_picker.value):
        parameter_widgets[parameter.name] = mo.ui.slider(
            parameter.min,
            parameter.max,
            step=parameter.step,
            value=parameter.default,
            label=parameter.label,
        )
    return parameter_widgets


@app.cell
def __(parameter_widgets):
    overrides = {
        name: widget.value for name, widget in parameter_widgets.items()
    }
    return overrides or None


@app.cell
def __(default_strategy_key_for_symbol, mo, symbol_picker):
    mo.md(
        f"**Pipeline default strategy:** `{default_strategy_key_for_symbol(symbol_picker.value)}`"
    )


@app.cell
def __(datetime, lookback, symbol_picker, timezone, fetch_price_history, timedelta):
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback.value)
    data = fetch_price_history(symbol_picker.value, start=start, end=end)
    return data, start, end


@app.cell
def __(end, mo, start):
    mo.md(
        f"**Analysis window:** {start.strftime('%Y-%m-%d')} → {end.strftime('%Y-%m-%d')}"
    )


@app.cell
def __(data, mo):
    if data.is_empty():
        mo.md(
            "⚠️ No market data found for the selected range. Try a wider lookback or confirm the database has been seeded."
        )
    else:
        data


@app.cell
def __(data, go):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=data["timestamp"],
            y=data["close"],
            name="Close",
            mode="lines",
        )
    )
    if "ema_fast" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data["timestamp"],
                y=data["ema_fast"],
                name="EMA Fast",
                mode="lines",
                line=dict(dash="dot"),
            )
        )
    if "ema_slow" in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data["timestamp"],
                y=data["ema_slow"],
                name="EMA Slow",
                mode="lines",
                line=dict(dash="dot"),
            )
        )
    fig.update_layout(title="Price & EMA Overview", xaxis_title="Timestamp", yaxis_title="Price")
    fig


@app.cell
def __(data, mo):
    if "rsi" in data.columns:
        mo.md("### RSI Overview")
        data.select(["timestamp", "rsi"]).tail(30)


@app.cell
def __(get_strategy, overrides, strategy_picker, symbol_picker):
    strategy = get_strategy(
        symbol=symbol_picker.value,
        strategy_key=strategy_picker.value,
        overrides=overrides,
    )
    return strategy


@app.cell
def __(data, evaluate_strategy, strategy):
    signals = evaluate_strategy(strategy, data)
    return signals


@app.cell
def __(signals):
    signals.tail(20)


@app.cell
def __(signals, mo):
    latest = signals.sort("timestamp").tail(1)
    if latest.is_empty():
        mo.md("⚠️ No signals generated for the selected window.")
    else:
        row = latest.to_dicts()[0]
        lines = [
            f"## Latest Signal: {row['signal_type']} ({row['strength']}/100)",
            f"**Symbol:** {row['symbol']}",
            f"**Timestamp:** {row['timestamp']}",
            "**Reasoning:**",
        ]
        lines.extend(f"- {reason}" for reason in row["reasoning"])
        mo.md("\n".join(lines))


if __name__ == "__main__":
    app.run()

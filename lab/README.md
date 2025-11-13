# Signals Strategy Lab

Interactive Marimo notebooks for prototyping trading strategies without touching production flows.

## Setup

```bash
cd lab
uv sync
```

Configure `DATABASE_URL` in your shell (reuse the same value as the pipeline) and ensure Postgres is running (`docker-compose up -d`).

## Usage

Run the main lab notebook:

```bash
uv run marimo run notebooks/strategy_lab.py
```

This launches an interactive UI where you can:

- Select a symbol from the `symbols` table (BTC-USD, AAPL, etc.).
- Adjust the lookback window and strategy parameters (RSI thresholds, MACD triggers).
- Fetch OHLCV + indicator history from Postgres using Polars.
- Run the existing strategy registry from `pipe/lib/strategies` to compare signals.
- Visualize price/EMA trends and inspect recent BUY/SELL/HOLD calls.

## Export

Share your experiment by exporting a static HTML snapshot:

```bash
uv run marimo export notebooks/strategy_lab.py --out outputs/strategy_lab.html
```

The export is self-contained and safe to upload or attach to issues/PRs.

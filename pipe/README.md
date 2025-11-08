# Prefect Data Pipeline

Nightly automation that fetches Yahoo Finance daily bars, recomputes indicators, generates signals, and (optionally) emails subscribers.

## Flows

| Flow | File | Default Trigger | Purpose |
| --- | --- | --- | --- |
| `market-data-backfill` | `flows/market_data_backfill.py` | Manual | Load up to 10 years of history for each symbol. Run when onboarding a new asset. |
| `market-data-sync` | `flows/market_data_sync.py` | 22:00 UTC daily | Fetch the latest daily OHLCV bars (last ~5 trading days) and insert into `market_data`. |
| `signal-analyzer` | `flows/signal_analyzer.py` | 22:15 UTC daily | Read stored OHLCV, compute RSI/EMA/MACD via Polars, and populate `indicators` + `signals`. |
| `notification-dispatcher` | `flows/notification_dispatcher.py` | 22:30 UTC daily | Select strong signals (≥ `SIGNAL_NOTIFY_THRESHOLD`) and log/send them via Resend (live once domain work completes). |

All reusable logic lives in `tasks/` (database helpers, indicator math, strategies, email sending).

## Quick Start

```bash
# Install deps once
uv sync --directory pipe

# Copy env vars (or rely on root .env)
cp pipe/.env.example pipe/.env

# Run a flow locally from repo root
uv run --directory pipe python -m pipe.flows.market_data_sync --symbols AAPL,BTC-USD
```

### Useful commands

```bash
# Backfill 10 years for default symbols
uv run --directory pipe python -m pipe.flows.market_data_backfill --backfill-range 10y

# Recompute indicators + signals only
uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD

# Dry run dispatcher with lower threshold
SIGNAL_NOTIFY_THRESHOLD=50 \
uv run --directory pipe python -m pipe.flows.notification_dispatcher
```

## Deploying to Prefect Cloud

```bash
prefect cloud login
uv run --directory pipe python -m deployments.register --work-pool <prefect-pool>
```

The helper registers all four flows with their default schedules and loads `pipe/.env` so `DATABASE_URL`, `RESEND_*`, etc. are wired correctly.

## Environment Variables

Add these to `pipe/.env` (or inherit from the root `.env`):

| Variable | Description |
| --- | --- |
| `DATABASE_URL` | Supabase connection string (`postgresql+psycopg://…`). |
| `RESEND_API_KEY` / `RESEND_FROM_EMAIL` | Used by `notification_dispatcher` (safe to omit until email goes live). |
| `SIGNAL_SYMBOLS` | Comma-separated overrides (defaults: `BTC-USD,AAPL`). |
| `SIGNAL_NOTIFY_THRESHOLD` | Minimum strength for notifying subscribers (default 60). |

## Project Structure

```
pipe/
├── flows/
│   ├── market_data_backfill.py
│   ├── market_data_sync.py
│   ├── signal_analyzer.py
│   └── notification_dispatcher.py
├── tasks/
│   ├── market_data.py        # Yahoo fetch + inserts
│   ├── indicators.py         # Polars RSI/EMA/MACD calculations
│   ├── signals.py            # Strategy invocation + DB writes
│   └── email_sending.py      # Resend helper (used by dispatcher)
├── lib/                      # Strategies, indicators, API clients
├── deployments/register.py   # Prefect deployment helper
├── schedules.py (legacy)     # Safe to ignore; use deployments/register.py
└── README.md
```

## Manual Validation Checklist

1. Run `uv run --directory pipe python -m pipe.flows.market_data_sync --symbols AAPL,BTC-USD`.
2. Check database counts:
   ```sql
   SELECT symbol, COUNT(*), MAX(timestamp) FROM market_data GROUP BY symbol;
   ```
3. Run `signal_analyzer` and verify new rows in `signals`:
   ```sql
   SELECT symbol, signal_type, strength, timestamp FROM signals ORDER BY timestamp DESC LIMIT 5;
   ```
4. Optionally run `notification_dispatcher` with a low threshold and watch Resend logs.

## Future Work

- Historical replay tool for strategy experiments (see `docs/TASK_SEEDS.md`).
- Provider fallback metrics + alerting (Prefect notification policies).
- Background queue for notification emails once deliverability is production-ready.

Keep this file updated whenever flow cadence or command syntax changes.

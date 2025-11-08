# System Architecture

> **Last Updated**: 2025-11-06  
> **Applies to**: Production MVP (Yahoo-only daily pipeline)

Signals ingests Yahoo Finance daily candles, stores them in Postgres, scores strategies in Prefect, and exposes read-only APIs that power the public dashboard and daily email digests. This document is the canonical picture of how data and responsibilities are split across the stack.

**Related**: [MVP](MVP.md) · [Operations Guide](resources/OPERATIONS.md) · [Technical Analysis](resources/TECHNICAL-ANALYSIS.md)

---

## 1. Layer Overview

| Layer | Tech | Responsibilities |
| --- | --- | --- |
| Pipeline (`pipe/`) | Prefect 2 · polars · psycopg | Fetch Yahoo Finance daily OHLCV, backfill up to 10 years, derive indicators (RSI/EMA/MACD), run symbol strategies, persist signals, trigger notifications. |
| Backend (`backend/`) | FastAPI · SQLAlchemy · psycopg | Read-only API for market data, indicators, signals, backtests, and subscriber flows (subscribe, confirm, unsubscribe). Applies rate limits + security headers. |
| Frontend (`frontend/`) | Next.js 16 · React Query · Chart.js | Marketing site + dashboard. Consumes backend APIs (`NEXT_PUBLIC_API_URL`) for signals, indicators, and market data, and exposes the shared subscribe form. |
| Database (`db/`) | PostgreSQL (Docker locally, Supabase prod) | Durable storage for `market_data`, `indicators`, `signals`, `backtests`, and `email_subscribers`. Unique constraints keep writes idempotent. |
| Messaging | Resend API | Sends confirmation/reactivation emails today and signal alerts when Prefect raises strong signals. |

**Data path**: Yahoo Finance → Prefect flows → Postgres → FastAPI → Next.js → Users (UI + email).

---

## 2. Data Lifecycle (Daily @ 22:00 UTC)

1. **Historical backfill** (manual): `market_data_backfill` fetches up to 10 years per symbol so we always have enough context for indicator windows and backtests.
2. **Daily sync (22:00 UTC)**: `market_data_sync` pulls the most recent 5 trading days to cover weekends or missed runs.
3. **Indicator refresh (22:15 UTC)**: `signal_analyzer` loads market data from Postgres, recomputes RSI/EMA/MACD, and stores indicator rows per candle.
4. **Strategy evaluation**: Prefect tasks call `pipe/lib/strategies/*` per symbol, generate BUY/SELL/HOLD + strength (0-100), and store results in `signals` with an idempotency key.
5. **Notification gating (22:30 UTC)**: `notification_dispatcher` selects signals ≥ `SIGNAL_NOTIFY_THRESHOLD` and hands them to Resend (today it logs + Resend send). Email templates live in `backend/api/email.py`.
6. **Frontend consumption**: Next.js uses React Query hooks (`frontend/src/lib/hooks`) to hit `/api/signals`, `/api/market-data`, and `/api/indicators`. Five-minute stale timers avoid hammering the API while keeping dashboards fresh.

---

## 3. Prefect Flows & Scheduling

All orchestration shells live in `pipe/flows/` and only import reusable tasks from `pipe/tasks/`.

| Flow | Module | Default trigger | Purpose |
| --- | --- | --- | --- |
| `market-data-backfill` | `pipe/flows/market_data_backfill.py` | Manual run | One-off fetch of multi-year history for new symbols. Supports named ranges from 1m → 10y (`HISTORICAL_RANGE_MAP`). Always recalculates indicators afterward. |
| `market-data-sync` | `pipe/flows/market_data_sync.py` | Daily 22:00 UTC | Grabs the latest daily bars (default last 5 days) so gaps/weekends are filled. |
| `signal-analyzer` | `pipe/flows/signal_analyzer.py` | Daily 22:15 UTC | Pulls cached OHLCV from Postgres, recomputes indicators, and generates signals via the strategy registry. |
| `notification-dispatcher` | `pipe/flows/notification_dispatcher.py` | Daily 22:30 UTC | Emits emails (or logs) when signal strength meets threshold. |

Register deployments via `uv run --directory pipe python -m deployments.register --work-pool <prefect-pool>`; schedules live in Prefect Cloud and can be paused/resumed from there (see [Operations Guide](resources/OPERATIONS.md)).

### Manual 10-year Backfill

Fetch the deepest history we support whenever we onboard a symbol:

```bash
uv run --directory pipe python -m pipe.flows.market_data_backfill --symbols BTC-USD,AAPL --backfill-range 10y
```

Behind the scenes `resolve_history_days()` caps the request at ~3,650 days and `_limit_df_to_days()` enforces the bound before writing to `market_data`.

---

## 4. Data Providers & Processing

- **Provider**: Yahoo Finance only. Alpha Vantage dependencies were removed to simplify quotas and legal review. All fetches go through `pipe/lib/api/yahoo.py`.
- **Format**: polars DataFrames with UTC timestamps. Prefect tasks convert them to tuples and upsert with `ON CONFLICT` so reruns remain idempotent.
- **Normalization**:
  - `resolve_symbols()` reads `SIGNAL_SYMBOLS` or falls back to `BTC-USD` + `AAPL`.
  - `_limit_df_to_days()` guards manual requests so we never store more than requested history.
  - `upsert_market_data()` writes OHLCV rows and keeps the latest row per (symbol, timestamp).
- **Indicators**: `pipe/tasks/indicators.py` loads price history (entire set or window), calls RSI/EMA/MACD helpers under `pipe/lib/indicators`, and bulk upserts `indicators` rows.

---

## 5. Strategy & Signal Generation

- Strategy definitions live in `pipe/lib/strategies/`:
  - `CryptoMomentumStrategy` → BTC-USD momentum, rewards EMA separation + MACD histogram surges, enforces profit-taking when RSI > 72.
  - `StockMeanReversionStrategy` → AAPL, penalizes extended RSI/EMA divergence and waits for RSI reclaim around 35–40 before issuing BUYs.
  - `HoldStrategy` → fallback for unknown symbols or when env overrides point to unsupported keys.
- The registry (`pipe/lib/strategies/__init__.py`) reads `SIGNAL_MODEL_<SYMBOL>` env overrides so we can remap strategies without code.
- Prefect tasks pass `StrategyInputs` containing price, RSI, EMA12/EMA26, and MACD histogram; results include signal type, strength, reasoning, and rule version (strategy name) for audits.

---

## 6. Backend ↔ Frontend Contract

- FastAPI routers under `backend/api/routers/` expose:
  - `/api/signals/*` – latest signal list, by-symbol history, and detail endpoints.
  - `/api/market-data/*` – OHLCV snapshots for charts (dashboard + detail pages).
  - `/api/indicators/*` – derived metrics for overlays (future UI work).
  - `/api/subscribe/*` – subscribe, confirm, unsubscribe, and admin listing.
  - `/health` – DB connectivity without leaking credentials.
- CORS allows all `*.vercel.app` via regex, so preview deployments keep working.
- Rate limiting (`slowapi`) protects public endpoints (60/min read, 5/min subscribe, 20/min confirm).
- Next.js 16 uses React Query hooks in `frontend/src/lib/hooks/` to call the API. Components such as `SubscribeForm` live in `frontend/src/components/forms/` and are shared between landing page, dashboard, and admin views.
- `NEXT_PUBLIC_API_URL` is the only frontend → backend configuration knob. Bun scripts (`bun run dev|lint|type-check`) ensure parity with CI.

---

## 7. Database & Messaging

Tables live under `db/schema.sql`:

| Table | Purpose | Key Constraints |
| --- | --- | --- |
| `market_data` | Canonical OHLCV storage | `UNIQUE(symbol, timestamp)` ensures idempotent inserts. |
| `indicators` | RSI/EMA/MACD snapshots | Mirrors `market_data` timestamps; updates overwrite existing rows. |
| `signals` | BUY/SELL/HOLD output | `UNIQUE(symbol, timestamp)` plus `idempotency_key` for auditing strategy changes. |
| `backtests` | Historical performance summaries (seeded) | Referenced by dashboard admin views. |
| `email_subscribers` | Subscription + token management | Stores `confirmed_at`, `confirmation_token`, `unsubscribe_token`. |

Email infrastructure lives in `backend/api/email.py` and `pipe/tasks/email_sending.py`. Today the notification flow uses Resend sandbox credentials; swapping to production only requires updating `RESEND_FROM_EMAIL` and API keys in Prefect + backend environments.

---

## 8. Observability & Operations

- Prefect Cloud executes all scheduled flows and captures structured logs + retries. See the [Operations Guide](resources/OPERATIONS.md) for CLI commands.
- Database validation: run the SQL snippets in the operations guide to confirm latest rows per symbol.
- Frontend health: `bun run lint && bun run type-check` locally; Vercel builds run the same commands.
- Backend health: hit `/health` (locally via `uv run --directory backend uvicorn api.main:app --reload` or in production) and sanity-check `/api/signals` responses when API changes land.
- Email verification: run through the subscribe → confirm flow locally and monitor the Resend dashboard when rotating templates or credentials.

---

## 9. Related Docs

- [MVP](MVP.md) – scope, user, and success metrics.
- [Operations Guide](resources/OPERATIONS.md) – day-to-day commands and troubleshooting.
- [Technical Analysis](resources/TECHNICAL-ANALYSIS.md) – indicator math + strategy notes.
- [README](../README.md) – quick start for the entire repository.

Keep this file updated whenever flows change, new data providers are added, or the frontend/backend contract evolves.

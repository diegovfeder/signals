# Implementation Summary

_Last updated: October 2025_

The project has moved beyond the single-flow MVP. This document summarizes what exists today so reviews and hand-offs stay grounded in facts.

---

## 1. Database & Schema

- `db/schema.sql` is the canonical migration (idempotent). It defines:
  - `market_data`, `indicators`, `signals`, `backtests`, `email_subscribers`, `assets`, and helper tables.
  - `signals` includes `strategy_name`, `rule_version`, `strength`, `reasoning`, and `idempotency_key` for upserts.
  - `email_subscribers` tracks `confirmed`, `confirmation_token`, `unsubscribe_token`, `unsubscribed`, and timestamps.
- Seed helpers live under `db/seeds/`.
- Connection string format: `postgresql+psycopg://user:pass@host:5432/signals`.

---

## 2. Pipeline Deliverables

### Tasks (`pipe/tasks/`)

- `market_data.py` – Alpha Vantage intraday fetcher with Yahoo fallback + resampling utilities + upsert helpers.
- `indicators.py` – Computes RSI/EMA/MACD and enforces numeric sanity checks.
- `signals.py` – Bridges indicator rows to the strategy registry, persists signals via `INSERT ... ON CONFLICT DO UPDATE`, and logs structured output.
- `db.py` – Connection helpers and URL normalization.

### Strategy Layer (`pipe/data/signals/strategies/`)

- `base.py`, `crypto_momentum.py`, `stock_mean_reversion.py`, `default_hold.py`, plus `__init__.py` which exposes `get_strategy`.
- Environment override convention: `SIGNAL_MODEL_<SYMBOL>=strategy_name`.

### Flows (`pipe/flows/`)

| Flow | Highlights |
| --- | --- |
| `historical_backfill.py` | Fetches up to 20 years of daily OHLCV via Yahoo, upserts into `market_data`, recomputes indicators. |
| `signal_generation.py` | Intraday slice fetch, indicator refresh, per-symbol strategy call, optional Resend hand-off. |
| `signal_replay.py` | Iterates over historical indicators, regenerates signals, writes `backtests` summaries, gracefully handles duplicates. |
| `notification_sender.py` | Queries the latest strong signals above `SIGNAL_NOTIFY_THRESHOLD`, loads confirmed subscribers, and sends Resend emails. |

All flows are executable via `python -m flows.<name>` from the `pipe/` directory and are Prefect-ready.

---

## 3. Backend API (FastAPI)

- `api/main.py` wires routers for signals, market data, backtests, subscribe/unsubscribe, and the health check.
- `api/routers/signals.py`
  - `GET /api/signals?limit=50`
  - `GET /api/signals/{symbol}`
  - `GET /api/signals/{symbol}/history`
- `api/routers/market_data.py`
  - `GET /api/market-data/{symbol}/ohlcv?range=2y`
  - `GET /api/market-data/{symbol}/indicators`
- `api/routers/backtests.py`
  - `GET /api/backtests/{symbol}?range=1y`
- `api/routers/subscribe.py`
  - `POST /api/subscribe` – idempotent insert/reactivation
  - `POST /api/subscribe/unsubscribe/{token}`
- Health check at `/health` performs a real DB round trip.

The backend expects the same `DATABASE_URL` as the pipeline and optional `RESEND_*` env vars for future email confirmation.

---

## 4. Frontend (Next.js 15)

- App Router pages: landing (`/`), dashboard (`/dashboard`), signal detail (`/signals/[symbol]`).
- TanStack Query powers data fetching (`useSignals`, `useMarketData`, `useBacktestSummary`).
- Chart rendering handled by `SymbolPriceChart` with indicator overlays.
- Shared subscription widget (`src/components/forms/SubscribeForm.tsx`) is embedded in the Hero and the dashboard header; it POSTs to `/api/subscribe` and handles optimistic UI states.
- Styling: Tailwind CSS 4 + custom CSS variables in `src/app/globals.css`. Buttons now use the green palette consistent with BUY signals.

Run locally with:

```bash
cd frontend
NEXT_PUBLIC_API_URL=http://localhost:8000 bun run dev
```

---

## 5. Subscription & Notifications

- Subscribe endpoint stores emails + tokens; reuses rows if a user re-enters an existing email and marks previously unsubscribed users as active again.
- Notification flow already fetches confirmed subscribers and sends Resend emails (placeholder templates). Scheduling + production API keys are pending.
- Frontend UX thanks the user immediately; once email confirmation ships we will surface the “pending confirmation” state instead.

---

## 6. Testing & Validation

- Manual QA steps:
  1. `docker-compose up -d`
  2. `python -m flows.historical_backfill --symbols BTC-USD,AAPL --backfill-range 2y`
  3. `python -m flows.signal_replay --symbols BTC-USD,AAPL --range-label 2y`
  4. `python -m flows.signal_generation --symbols BTC-USD,AAPL`
  5. `uvicorn api.main:app --reload`
  6. `bun run dev`
- Automated tests are still TODO; strategy-level unit tests are the next priority.

---

## 7. Outstanding Work

- Prefect deployments + alerting.
- Email confirmation + production templates.
- Improved backtest exits and win-rate calculations.
- Tests for strategies, flows, and API routers.
- Docs + README sync (tracked in `docs/TODOs.md`).

This file should only change when a major subsystem lands. For backlog grooming consult `docs/TODOs.md`.

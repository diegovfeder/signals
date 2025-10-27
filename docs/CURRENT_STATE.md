# Project Status & Developer Onboarding Guide

This document captures the current state of the Signals app after the latest refactor, the flows you need to run to populate the database, and the remaining gaps on the roadmap. Share this with any new engineer so they can become productive quickly.

---

## 1. High-Level Architecture

| Layer | Tech | Responsibilities |
| --- | --- | --- |
| **Pipeline (`pipe/`)** | Prefect 2 | Fetch OHLCV data, compute indicators, generate signals, nightly replay/backtests. |
| **Backend (`backend/`)** | FastAPI + SQLAlchemy | REST API at `/api/*` for signals, market data, indicators, future backtests. |
| **Frontend (`frontend/`)** | Next.js 15 + React Query | Dashboard + symbol detail pages consuming the API, renders charts using Chart.js. |
| **Database (`db/`)** | PostgreSQL | Tables: `market_data`, `indicators`, `signals`, plus supporting tables defined in `db/schema.sql`. |

All Prefect tasks now live under `pipe/tasks/`. Flows in `pipe/flows/` orchestrate those tasks and delegate BUY/SELL/HOLD decisions to the shared strategy registry.

---

## 2. Pipeline Overview

### 2.1 Shared Tasks (`pipe/tasks/`)

- `market_data.py`: Alpha Vantage intraday fetch, Yahoo chart API fallback for historical data, symbol/range resolution, and `upsert_market_data`.
- `indicators.py`: Loads price history from Postgres, computes RSI/EMA/MACD, and upserts rows into `indicators`.
- `signals.py`: Hydrates `StrategyInputs`, calls `get_strategy(symbol)` from the registry, writes BUY/SELL/HOLD rows into `signals`, and logs notifications for strong signals.
- `db.py`: Normalizes `DATABASE_URL` (supports `postgresql+psycopg://`) and returns psycopg connections.
- `data/signals/strategies/`: Concrete strategy classes plus the env-driven registry (`SIGNAL_MODEL_<SYMBOL>=crypto_momentum` overrides defaults).

### 2.2 Flows (`pipe/flows/`)

| Flow | Path | What it does | Typical command |
| --- | --- | --- | --- |
| **Historical Backfill** | `flows/historical_backfill.py` | Fetches ~N days of daily OHLCV per symbol (Yahoo fallback), upserts into `market_data`, recomputes the entire indicator history. | `python -m flows.historical_backfill --symbols BTC-USD,AAPL --backfill-range 2y` |
| **Intraday Signal Generation** | `flows/signal_generation.py` | Fetches the latest intraday slice from Alpha Vantage, upserts new bars, recomputes indicators for the tail window, and emits the *current* BUY/SELL/HOLD signal per symbol. | `python -m flows.signal_generation --symbols BTC-USD` |
| **Historical Signal Replay / Backtest** | `flows/signal_replay.py` | Replays stored indicator + price history, regenerates signals for every bar, stores them, and writes win-rate/return summaries to the `backtests` table. | `python -m flows.signal_replay --symbols BTC-USD --range-label 2y` |
| **Notification Sender** | `flows/notification_sender.py` | Looks up recent strong signals, fetches confirmed subscribers, and sends Resend emails with rate limiting. | `python -m flows.notification_sender --min-strength 70` |

### 2.3 Strategy Registry (`pipe/data/signals/strategies/`)

- `base.py` defines `StrategyInputs`, `StrategyResult`, and the `Strategy` protocol (returning `BUY`, `SELL`, or `HOLD` plus reasoning + strength).
- `crypto_momentum.py` targets BTC-style momentum (RSI 35–45 bounces, EMA spread, MACD histogram).
- `stock_mean_reversion.py` focuses on equities/ETFs, leaning on RSI reclaims and EMA compression for BUY, with SELL triggers when RSI > 70 and momentum fades.
- `default_hold.py` keeps a symbol in HOLD when no specific model exists.
- `__init__.py` exposes `get_strategy(symbol)` and the env override convention `SIGNAL_MODEL_<SYMBOL>=strategy_name`. Example: `SIGNAL_MODEL_ETH_USD=crypto_momentum`.

**Important**: Always run the flow modules from inside the `pipe/` directory so Python can resolve `tasks.*`.

### 2.4 Deployments (`pipe/deployments/register.py`)

- Register all Prefect deployments with `python -m deployments.register --work-pool <pool-name>`.
- Schedules: intraday every 15 min (UTC), notifications 10 min later, replay nightly (00:15 UTC), backfill on demand.
- Pause/resume with `prefect deployment pause|resume <flow>/<deployment>` or delete via `prefect deployment delete ...`.

---

## 3. Backend & Frontend Touchpoints

### Backend (`backend/`)

- Entry point: `api/main.py`
- Routers:
  - `api/routers/signals.py` – CRUD for signals.
  - `api/routers/market_data.py` – Range-filtered OHLCV + indicators endpoints (`/api/market-data/{symbol}/ohlcv?range=1y`).
  - `api/routers/backtests.py` – Serves the latest summary from the `backtests` table (falls back to a placeholder if empty).
  - `api/routers/subscribe.py` – `POST /api/subscribe` stores/reactivates emails, `/api/subscribe/unsubscribe/{token}` flips the `unsubscribed` flag.
- Settings come from `backend/.env`; `DATABASE_URL` must match the pipeline connection string (use `postgresql+psycopg://…` – our `tasks/db.py` strips the dialect suffix automatically).

### Frontend (`frontend/`)

- Hooks in `src/lib/hooks/useSignals.ts` use TanStack Query against the FastAPI endpoints.
- Symbol detail page (`src/app/signals/[symbol]/page.tsx`) now renders real price history with Chart.js and shows the most recent signal, plus placeholders for backtests.
- Shared subscribe experience lives in `src/components/forms/SubscribeForm.tsx`; both the marketing Hero and the dashboard embed this component so every entry point talks to `/api/subscribe`.
- Update `NEXT_PUBLIC_API_URL` when pointing the UI at a different backend.

---

## 4. End-to-End Setup Checklist

1. **Database**
   - Start PostgreSQL (`docker-compose up -d`).
   - Apply schema if needed: `psql $DATABASE_URL -f db/schema.sql`.

2. **Pipeline Environment**

   ```bash
   cd pipe
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   export DATABASE_URL=postgresql+psycopg://quantmaster:buysthedip@localhost:5432/signals
   export ALPHA_VANTAGE_API_KEY=...  # free key
   ```

3. **Backfill data**

   ```bash
   python -m flows.historical_backfill --symbols BTC-USD,AAPL,IVV,BRL=X --backfill-range 2y
   ```

   This seeds `market_data` and `indicators`.

4. **Generate live signals**

   ```bash
   python -m flows.signal_generation --mode intraday --symbols BTC-USD,AAPL,IVV,BRL=X
   ```

   Register Prefect deployments when you are ready to automate (`python -m deployments.register --work-pool default-prefect-managed-wp`).

5. **Backend & Frontend**

   ```bash
   cd backend && uvicorn api.main:app --reload --port 8000
   cd frontend && NEXT_PUBLIC_API_URL=http://localhost:8000 bun run dev
   ```

---

## 5. Known Gaps / Next Steps

1. **Backtest quality**
   - The replay flow uses a simple “BUY → exit next bar” heuristic. We still need richer exit logic, SELL signals, configurable holding periods, and risk metrics if we want production-grade backtests.

2. **Automation refinement**
   - Deployments exist; add monitoring/alerts and tune schedules before production.

3. **Notifications**
   - `notification_sender` now sends Resend emails, but we still need a UI/CLI to subscribe users and run the flow automatically after each intraday batch.

4. **Data quality & monitoring**
   - Add metrics/logging for insert counts, stale data alarms, and Alpha Vantage quota monitoring.

5. **Docs**
   - Update `README.md` to link here, add troubleshooting steps for common Alpha Vantage/Yahoo failures.

---

## 6. Quick Reference

| Action | Command |
| --- | --- |
| Install pipeline deps | `cd pipe && pip install -r requirements.txt` |
| Seed 2y history | `python -m flows.historical_backfill --backfill-range 2y` |
| Run intraday signals | `python -m flows.signal_generation` |
| Replay/backtest 2y | `python -m flows.signal_replay --range-label 2y` |
| Register Prefect deployments | `python -m deployments.register --work-pool default-prefect-managed-wp` |
| API Health | `curl http://localhost:8000/health` |
| Frontend dev server | `cd frontend && bun run dev` |

Keep this doc updated whenever we add flows or change the onboarding process. It should be the first stop for any new engineer joining the project.

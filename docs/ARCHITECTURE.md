# System Architecture

_Last updated: October 2025_

This document describes how data moves through the Signals stack after the strategy refactor and the subscription UX refresh. Treat it as the source of truth when onboarding new engineers or deciding where to plug in new features.

---

## 1. High-Level View

| Layer | Tech | Responsibilities |
| --- | --- | --- |
| Pipeline (`pipe/`) | Prefect 2 + pandas + psycopg | Fetch OHLCV data, normalize bars, compute indicators, pick a strategy per symbol, emit BUY/SELL/HOLD + strength, seed backtests, trigger emails. |
| Backend (`backend/`) | FastAPI + SQLAlchemy/psycopg | Read-only REST API for signals, indicators, market data, backtests, and subscriber management. |
| Frontend (`frontend/`) | Next.js 15 + React Query + Chart.js | Marketing site + dashboard, live signals grid, symbol detail chart, reusable signup component. |
| Database (`db/`) | PostgreSQL (local docker-compose) | Durable storage for `market_data`, `indicators`, `signals`, `backtests`, `email_subscribers`, etc. |
| Messaging | Resend (HTTP API) | Confirmation + high-confidence alert emails (Phase 2 automation lives in `flows/notification_sender.py`). |

### Execution Graph (simplified)

```mermaid
graph TD
    subgraph Pipeline
      A[Historical Backfill Flow<br/>python -m pipe.flows.historical_backfill] --> B(Indicators Task)
      B --> C(Strategy Engine)
      C --> D[Signals Table]
      D --> E[Backtests Table]
      subgraph Intraday
        F[Signal Generation Flow<br/>python -m pipe.flows.signal_generation] --> B
      end
      G[Signal Replay Flow] --> C
      H[Notification Sender] --> RESEND
    end
    YF[Alpha Vantage + Yahoo Finance] --> A
    YF --> F
    DB[(PostgreSQL)] --> API
    API --> NEXT
    NEXT --> USER
    D --> RESEND
    RESEND --> USER
```

---

## 2. Data Pipeline

All reusable logic lives under `pipe/tasks/`. Flows in `pipe/flows/` are orchestration shells with CLI entry points.

### Shared Tasks

- `tasks/market_data.py`
  - Resolves input symbols/ranges (`resolve_symbols`, `resolve_history_days`).
  - Calls Alpha Vantage intraday endpoints when available; falls back to the Yahoo Finance chart API for longer history.
  - Handles per-provider rate limits with locks, throttling, and graceful downgrade logs.
  - Upserts bars into `market_data` with `ON CONFLICT (symbol, timestamp)` semantics.
- `tasks/indicators.py`
  - Pulls the requested window from `market_data`, computes RSI/EMA/MACD via pandas, and writes rows into `indicators`.
- `tasks/signals.py`
  - Loads the most recent indicator row, hydrates a `StrategyInputs` dataclass, picks a strategy using the registry (see §3), and persists/updates the `signals` table.
  - Emits structured logs used by Prefect and by the replay/backtest flow.
- `tasks/db.py`
  - Normalizes SQLAlchemy-style URLs (e.g., `postgresql+psycopg://`) for psycopg, centralizes connection helpers, and enforces UTC timestamps.

### Flows

| Flow | Module | Typical command | Notes |
| --- | --- | --- | --- |
| Historical backfill | `flows/historical_backfill.py` | `python -m pipe.flows.historical_backfill --symbols BTC-USD,AAPL --backfill-range 2y` | Fetches up to N days of daily data per symbol, backfills indicators, and guarantees enough history for replay. |
| Intraday signal generation | `flows/signal_generation.py` | `python -m pipe.flows.signal_generation --symbols BTC-USD,AAPL` | Pulls the newest intraday slice (Alpha → Yahoo fallback), refreshes indicators for the tail window, generates a fresh signal per symbol, and logs BUY/SELL/HOLD decisions. |
| Signal replay / backtest | `flows/signal_replay.py` | `python -m pipe.flows.signal_replay --symbols BTC-USD --range-label 2y` | Replays historical indicators to rebuild the `signals` table and writes summary rows into `backtests`. Conflict handling ensures timestamps are upserted instead of duplicated. |
| Notification sender | `flows/notification_sender.py` | `python -m pipe.flows.notification_sender --min-strength 70` | Queries for the last strong signal per symbol and sends Resend emails to confirmed subscribers (real automation scheduled after MVP). |

Deployments live in `pipe/deployments/register.py`; run `python -m deployments.register --work-pool <pool>` to register schedules in Prefect Cloud (intraday every 15 min, replay nightly, notifications offset by 10 minutes).

---

## 3. Strategy Registry

The new signal layer lives under `pipe/data/signals/strategies/` and exposes a `Strategy` protocol plus concrete implementations:

- `StockMeanReversionStrategy` – RSI-driven mean reversion tuned for equities/ETFs (`AAPL`, `IVV`, `BRL=X`). Looks for RSI reclaiming the 35–40 zone, EMA compression, and penalizes extended overbought readings to issue SELL or HOLD.
- `CryptoMomentumStrategy` – Momentum-first strategy for `BTC-USD`. Rewards faster EMA separation, MACD histogram surges, and includes profit-taking SELLs when RSI > 72 with weakening momentum.
- `HoldStrategy` – Fallback that keeps the symbol in HOLD with a neutral reasoning line (used when a symbol isn’t mapped).

Usage model:

```python
from pipe.data.signals.strategies import get_strategy, StrategyInputs

strategy = get_strategy("BTC-USD")
result = strategy.generate(StrategyInputs(...))
```

- Registry defaults are defined in `_DEFAULT_SYMBOL_MAPPING`.
- Override any mapping at runtime via environment variables: `SIGNAL_MODEL_BTC_USD=crypto_momentum`. We normalize the env key so `SIGNAL_MODEL_IVV=stock_mean_reversion` just works. Use double underscores to encode `/` in forex pairs (e.g., `SIGNAL_MODEL_BRL__X=stock_mean_reversion`).
- Strategies return a `StrategyResult(signal_type, reasoning[], strength)` which the pipeline writes directly to the database and the frontend displays verbatim.

When data scientists introduce a new heuristic, they add a file next to the existing strategies and register it inside `pipe/data/signals/strategies/__init__.py`. All flows automatically pick it up on the next run or replay.

---

## 4. Database

- **Engine**: PostgreSQL 15 via `docker-compose up -d`.
- **Schema file**: `db/schema.sql` (idempotent, safe to re-run).
- **Key tables**:
  - `market_data` – canonical OHLCV history (`symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`).
  - `indicators` – RSI, EMA(12/26), MACD histogram, derived for the same timestamps as `market_data`.
  - `signals` – per-symbol BUY/SELL/HOLD entries with `strength`, `strategy_name`, `rule_version`, `idempotency_key`.
  - `backtests` – summary metrics produced by the replay flow.
  - `email_subscribers` – double opt-in tracking: `confirmed`, `confirmation_token`, `unsubscribe_token`, `unsubscribed`.
- **Constraints**: `UNIQUE(symbol, timestamp)` on data tables to make upserts cheap; `signals` uses the same constraint so replays overwrite instead of duplicating.
- **Connection string**: `postgresql+psycopg://quantmaster:buysthedip@localhost:5432/signals`. The `+psycopg` suffix keeps SQLAlchemy happy while `tasks/db.py` strips it for raw psycopg connections.

---

## 5. Backend API

Located in `backend/`. Highlights:

- `api/main.py` wires routers for signals, market data, backtests, and subscribe/unsubscribe.
- `api/routers/signals.py` offers list, latest, and history endpoints, including the `strength`, `reasoning`, and `strategy_name` fields required by the dashboard.
- `api/routers/market_data.py` streams OHLCV and indicators slices (with range filters the frontend’s chart uses).
- `api/routers/backtests.py` exposes the latest replay summary per symbol/range; returns sensible placeholders if no backtest exists.
- `api/routers/subscribe.py` handles POST `/api/subscribe` and `/api/subscribe/unsubscribe/{token}`. We store a confirmation token for Phase 2 email verification even though the MVP form just thanks the user inline.
- `api/routers/health.py` (via `main.py`) checks the DB with `SELECT 1`.

FastAPI runs locally with:

```bash
cd backend
uvicorn api.main:app --reload --port 8000
```

Set `DATABASE_URL`, `RESEND_API_KEY`, and `CORS_ORIGINS` in `backend/.env`.

---

## 6. Frontend

Next.js 15 (App Router) with Bun.

- `src/app/page.tsx` – marketing landing page made of modular sections (Hero, Value props, Coverage, CTA). The Hero now embeds the shared `<SubscribeForm />` so visitors can join the email list immediately.
- `src/app/dashboard/page.tsx` – authenticated-lite dashboard that fetches signals via TanStack Query (`useSignals`) and shows the same subscribe component for visitors coming from emails.
- `src/app/signals/[symbol]/page.tsx` – detail view with Chart.js + indicator overlays and room for backtest stats.
- `src/components/forms/SubscribeForm.tsx` – client component that posts to `/api/subscribe`, handles success/error messaging, and is reusable across sections.
- Providers (`src/app/providers.tsx`) wrap the tree with a `QueryClientProvider`.

Configure the API origin via `NEXT_PUBLIC_API_URL` (defaults to `http://localhost:8000`). Tailwind 4 powers the design system; button tokens live in `src/app/globals.css`.

---

## 7. Email + Subscription Flow

1. User enters an email on the landing page or dashboard.
2. `<SubscribeForm />` calls `POST /api/subscribe` → backend creates/updates a row in `email_subscribers`, issuing new confirmation + unsubscribe tokens if needed.
3. API currently returns a friendly message. In Phase 2 the notification sender will pick up confirmed emails and Resend will deliver both confirmation and signal alerts.
4. Users can self-serve removal via `POST /api/subscribe/unsubscribe/{token}` (link to be embedded in future emails).

`flows/notification_sender.py` already contains the plumbing to email confirmed subscribers when a signal stronger than `SIGNAL_NOTIFY_THRESHOLD` occurs; we only need to wire scheduling + templates once Resend credentials are live.

---

## 8. Data Quality & Observability

- Prefect manages retries (3 attempts with exponential backoff) and emits structured logs that show up in Prefect Cloud’s UI.
- Alpha Vantage calls are rate-limited via `_ALPHA_RATE_LOCK` and fall back to Yahoo automatically when the quota is exceeded or when we request >500 days of history.
- `pipe/data/utils/data_validation.py` (planned) hosts sanity checks (no negative prices, gap detection). Hook it into the flows as we mature the pipeline.
- Replay flow uses `ON CONFLICT DO UPDATE` to keep signals consistent whenever strategies change.
- Future enhancements: Prefect deployment alerts, Slack/email ops notifications, DB-level monitoring.

---

## 9. Deployment & Configuration

Environment variable quick reference (aggregate from `.env.example` files):

| Variable | Description | Location |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://…` connection string shared by pipeline + backend. | backend, pipe |
| `ALPHA_VANTAGE_API_KEY` | Required for Alpha Vantage intraday fetches. | pipe |
| `SIGNAL_SYMBOLS` | Optional comma-separated overrides for flows. | pipe |
| `BACKFILL_RANGE` / `BACKFILL_DAYS` | Preferred range for historical flow when CLI args aren’t provided. | pipe |
| `SIGNAL_MODEL_<SYMBOL>` | Override per-symbol strategies (e.g., `SIGNAL_MODEL_ETH_USD=crypto_momentum`). | pipe |
| `SIGNAL_NOTIFY_THRESHOLD` | Minimum strength to email from notification flow. | pipe |
| `RESEND_API_KEY`, `RESEND_FROM_EMAIL` | Email sender credentials. | backend, pipe |
| `NEXT_PUBLIC_API_URL` | Frontend → backend base URL. | frontend |

Deployment targets:

- **Frontend**: Vercel (Bun/Next.js). Add environment variables via the Vercel dashboard.
- **Backend**: Vercel functions, Railway, or Fly.io – any place that can run FastAPI + psycopg.
- **Pipeline**: Prefect Cloud deployments (historical backfill on-demand, intraday generation every 15 min, replay nightly, notification sender right after the intraday flow).

---

## 10. Related Docs

- [CURRENT_STATE.md](CURRENT_STATE.md) – step-by-step onboarding + CLI commands.
- [DATA-SCIENCE.md](DATA-SCIENCE.md) – indicator math and strategy heuristics.
- [TODOs.md](TODOs.md) – prioritized backlog.
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) – change log of what’s been built.
- [MVP.md](MVP.md) – business scope and success metrics.

Keep this document updated whenever the architecture shifts (new data providers, strategy bundles, notification transports, etc.).

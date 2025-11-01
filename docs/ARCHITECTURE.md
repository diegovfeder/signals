# System Architecture

> **Last Updated**: 2025-10-31
> **Applies to**: MVP Phase 1 (Daily signals, 4 flows)

This document describes how data moves through the Signals stack. Treat it as the source of truth when onboarding new engineers or deciding where to plug in new features.

**Related**: [MVP](MVP.md) | [Operations](reference/OPERATIONS.md) | [Technical Analysis](reference/TECHNICAL-ANALYSIS.md)

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
  - Loads the most recent indicator row, generates BUY/SELL/HOLD signals with strength scores, and persists to the `signals` table.
  - Emits structured logs visible in Prefect Cloud UI.
- `tasks/db.py`
  - Normalizes SQLAlchemy-style URLs (e.g., `postgresql+psycopg://`) for psycopg, centralizes connection helpers, and enforces UTC timestamps.

### Flows

| Flow | Module | Typical command | Notes |
| --- | --- | --- | --- |
| Market data backfill | `flows/market_data_backfill.py` | `uv run --directory pipe python -m pipe.flows.market_data_backfill --symbols BTC-USD,AAPL --backfill-range 2y` | Fetches multi-year daily OHLCV history from Yahoo Finance for new symbols. Run manually when onboarding new assets. |
| Market data sync | `flows/market_data_sync.py` | `uv run --directory pipe python -m pipe.flows.market_data_sync --symbols BTC-USD,AAPL` | Fetches the latest daily bars (last 5 days to handle weekends). Runs daily at 10:00 PM UTC to keep data current. |
| Signal analyzer | `flows/signal_analyzer.py` | `uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols BTC-USD,AAPL` | Reads market data from DB, calculates indicators (RSI/EMA), generates BUY/SELL/HOLD signals. Runs daily at 10:15 PM UTC. Does NOT fetch new data. |
| Notification dispatcher | `flows/notification_dispatcher.py` | `uv run --directory pipe python -m pipe.flows.notification_dispatcher --min-strength 60` | Queries recent strong signals and emails confirmed subscribers via Resend. Runs daily at 10:30 PM UTC. |

**Flow Sequence**: Data sync → Signal analysis → Email notifications (all daily: 10:00 PM, 10:15 PM, 10:30 PM UTC).

Deployments live in `pipe/deployments/register.py`; run `uv run python -m deployments.register --work-pool <pool>` to register schedules in Prefect Cloud.

---

## 3. Strategy Registry

The signal generation logic lives under `pipe/lib/signals/strategies/` and exposes a `Strategy` protocol plus concrete implementations:

- `StockMeanReversionStrategy` – RSI-driven mean reversion tuned for equities (`AAPL`). Looks for RSI reclaiming the 35–40 zone, EMA compression, and penalizes extended overbought readings to issue SELL or HOLD.
- `CryptoMomentumStrategy` – Momentum-first strategy for `BTC-USD`. Rewards faster EMA separation, MACD histogram surges, and includes profit-taking SELLs when RSI > 72 with weakening momentum.
- `HoldStrategy` – Fallback that keeps the symbol in HOLD with a neutral reasoning line (used when a symbol isn’t mapped).

Usage model:

```python
from pipe.lib.signals.strategies import get_strategy, StrategyInputs

strategy = get_strategy("BTC-USD")
result = strategy.generate(StrategyInputs(...))
```

- Registry defaults are defined in `_DEFAULT_SYMBOL_MAPPING`.
- Override any mapping at runtime via environment variables: `SIGNAL_MODEL_BTC_USD=crypto_momentum` or `SIGNAL_MODEL_AAPL=stock_mean_reversion`.
- Strategies return a `StrategyResult(signal_type, reasoning[], strength)` which the pipeline writes directly to the database and the frontend displays verbatim.

When adding new strategies, create a file in `pipe/lib/signals/strategies/` and register it in the `__init__.py`. All flows automatically pick it up on the next run.

---

## 4. Database

- **Engine**: PostgreSQL 15 via `docker-compose up -d`.
- **Schema file**: `db/schema.sql` (idempotent, safe to re-run).
- **Key tables**:
  - `market_data` – canonical OHLCV history (`symbol`, `timestamp`, `open`, `high`, `low`, `close`, `volume`).
  - `indicators` – RSI, EMA(12/26), derived for the same timestamps as `market_data`.
  - `signals` – per-symbol BUY/SELL/HOLD entries with `strength`, `reasoning`, `price_at_signal`, `idempotency_key`.
  - `email_subscribers` – double opt-in tracking: `confirmed`, `confirmation_token`, `unsubscribe_token`, `unsubscribed`.
- **Constraints**: `UNIQUE(symbol, timestamp)` on data tables to make upserts idempotent and prevent duplicates.
- **Connection string**: `postgresql+psycopg://quantmaster:buysthedip@localhost:5432/signals`. The `+psycopg` suffix keeps SQLAlchemy happy while `tasks/db.py` strips it for raw psycopg connections.

---

## 5. Backend API

Located in `backend/`. Highlights:

- `api/main.py` wires routers for signals, market data, and subscribe/unsubscribe.
- `api/routers/signals.py` offers list, latest, and history endpoints, including the `strength`, `reasoning`, and `strategy_name` fields required by the dashboard.
- `api/routers/market_data.py` streams OHLCV and indicators slices (with range filters the frontend’s chart uses).
- `api/routers/subscribe.py` handles POST `/api/subscribe` and `/api/subscribe/unsubscribe/{token}`. We store a confirmation token for Phase 2 email verification even though the MVP form just thanks the user inline.
- `api/routers/health.py` (via `main.py`) checks the DB with `SELECT 1`.

FastAPI runs locally with:

```bash
cd backend
uv run uvicorn api.main:app --reload --port 8000
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

`flows/notification_dispatcher.py` emails confirmed subscribers when a signal stronger than `SIGNAL_NOTIFY_THRESHOLD` occurs. It runs daily at 10:30 PM UTC after signal generation.

---

## 8. Data Quality & Observability

- Prefect manages retries (3 attempts with exponential backoff) and emits structured logs visible in Prefect Cloud's UI.
- Yahoo Finance provides daily OHLCV data for all tracked symbols.
- `pipe/lib/utils/data_validation.py` (planned) will host sanity checks (no negative prices, gap detection).
- Database constraints (`UNIQUE(symbol, timestamp)`) ensure idempotent upserts prevent duplicates.
- Future enhancements: Prefect deployment alerts, Slack/email ops notifications, DB-level monitoring.

---

## 9. Deployment & Configuration

Environment variable quick reference (aggregate from `.env.example` files):

| Variable | Description | Location |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql+psycopg://…` connection string shared by pipeline + backend. | backend, pipe |
| `SIGNAL_SYMBOLS` | Optional comma-separated symbol overrides (default: BTC-USD,AAPL). | pipe |
| `SIGNAL_NOTIFY_THRESHOLD` | Minimum strength to email from notification flow (default: 60). | pipe |
| `RESEND_API_KEY`, `RESEND_FROM_EMAIL` | Email sender credentials. | backend, pipe |
| `NEXT_PUBLIC_API_URL` | Frontend → backend base URL. | frontend |

Deployment targets:

- **Frontend**: Vercel (Bun/Next.js). Add environment variables via the Vercel dashboard.
- **Backend**: Vercel functions, Railway, or Fly.io – any place that can run FastAPI + psycopg.
- **Pipeline**: Prefect Cloud deployments (backfill on-demand, daily sync/analyzer/dispatcher at 10 PM UTC).

---

## 10. Related Docs

- [MVP.md](MVP.md) – Product vision and success metrics
- [TODOs.md](TODOs.md) – Current task tracking and prioritized backlog
- [Operations Guide](reference/OPERATIONS.md) – Running flows, deployments, troubleshooting
- [Technical Analysis](reference/TECHNICAL-ANALYSIS.md) – Indicator math (RSI/EMA) and signal strategies
- [Glossary](reference/GLOSSARY.md) – Terms and definitions
- [Resources](reference/RESOURCES.md) – External links and references

Keep this document updated whenever the architecture shifts (new data providers, strategy bundles, notification transports, etc.).

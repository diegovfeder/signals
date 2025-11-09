# CLAUDE.md

Guidance for Claude Code (and other AI collaborators) working inside the Signals repo. Updated **November 2025** to reflect the production MVP with Yahoo-only ingestion, nightly Prefect flows, and the Next.js 16 frontend.

---

## 1. Snapshot

- **Frontend**: Next.js 16 (Bun) at https://signals-dvf.vercel.app
- **Backend**: FastAPI on Vercel at https://signals-api-dvf.vercel.app
- **Pipeline**: Prefect Cloud (market data sync 22:00 UTC → signal analyzer 22:15 UTC → notification dispatcher 22:30 UTC)
- **Database**: Supabase PostgreSQL (Session Mode pooler, IPv4, psycopg v3 driver)
- **Email**: Resend (confirmation + reactivation live; signal notifications gated on backlog items)
- **Source of truth for future work**: GitHub Project "[Signals – Tasks](https://github.com/users/diegovfeder/projects/4/views/1)"

Everything auto-deploys from `main`. Keep docs in sync with code; outdated guidance is more harmful than missing detail.

---

## 2. Repo Map

| Path | Purpose |
| --- | --- |
| `backend/` | FastAPI app (`api/`) with routers, schemas, and email helpers. Uses **uv** for deps locally and `requirements.txt` for Vercel installs. |
| `frontend/` | Next.js 16 App Router, Bun-powered. UI in `src/app/`, shared components in `src/components/`, data hooks in `src/lib/`. |
| `pipe/` | Prefect 2 flows (`flows/`), reusable tasks (`tasks/`), indicators/strategies (`lib/`). All commands run via `uv run --directory pipe ...`. |
| `db/` | `schema.sql`, seeds, and Docker bootstrap for local Postgres. Supabase prod shares the same schema. |
| `docs/` | Architecture, MVP scope, operations guide, project workflow (TODOs.md), etc. Update here first when behavior changes. |
| `.github/ISSUE_TEMPLATE/` | `task.md` template for opening new GitHub issues that feed the “Signals – Tasks” project. |

---

## 3. Tooling & Commands

### Python (backend + pipeline)
- Install once: `uv sync` (root) or `uv sync --directory pipe`.
- Run API: `uv run --directory backend uvicorn api.main:app --reload --port 8000`.
- Formatters/linters: rely on `ruff`/`black` configs baked into `pyproject.toml` (run via `uv run ruff format` if needed).
- Prefect flows:
  - Historical backfill: `uv run --directory pipe python -m pipe.flows.market_data_backfill --backfill-range 10y`
  - Daily sync: `uv run --directory pipe python -m pipe.flows.market_data_sync --symbols AAPL,BTC-USD`
  - Analyzer: `uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD`
  - Notifier: `uv run --directory pipe python -m pipe.flows.notification_dispatcher --min-strength 60`
- Deployment helper: `uv run --directory pipe python -m pipe.deployments.register --work-pool <prefect-pool>`

### Frontend (Next.js 16 + Bun)
- Install: `cd frontend && bun install`
- Dev server: `bun run dev` → http://localhost:3000
- Quality gates: `bun run lint` and `bun run type-check`
- Use **Next.js DevTools MCP** when inspecting routes/components—call `mcp__next-devtools__init` at the start of a session, then leverage `nextjs_docs`/`nextjs_runtime` for authoritative info.

### Database
- Local: `docker-compose up -d` seeds schema + data automatically.
- Prod: Supabase Session Mode (Port 5432, IPv4). `DATABASE_URL` must be `postgresql+psycopg://` so SQLAlchemy/psycopg v3 work everywhere.

---

## 4. Data Pipeline Overview

1. **`market_data_backfill`** (manual) – Fetch up to 10 years per symbol, then recompute indicators.
2. **`market_data_sync`** (22:00 UTC) – Grab last ~5 daily bars from Yahoo Finance for every symbol to cover weekends/missed runs.
3. **`signal_analyzer`** (22:15 UTC) – Load stored OHLCV, compute RSI/EMA/MACD via Polars helpers, run per-symbol strategy, insert signals with reasoning + `rule_version`.
4. **`notification_dispatcher`** (22:30 UTC) – Fetch strong signals (≥ `SIGNAL_NOTIFY_THRESHOLD`), send emails via Resend (today it logs + optionally sends; production domain work tracked in task seeds).

Strategies live in `pipe/lib/strategies/` with environment overrides (`SIGNAL_MODEL_<SYMBOL>`). Default mapping: BTC-USD → crypto momentum, AAPL → stock mean reversion.

---

## 5. Backend & API Notes

- FastAPI routers under `backend/api/routers/*` expose signals, market data, indicators, subscribe/confirm/unsubscribe, and health endpoints.
- Rate limiting via `slowapi`: 5/min for subscribe, 20/min for confirm, 60/min for read endpoints.
- CORS allows any `*.vercel.app` origin; keep this when adding preview environments.
- Env vars: `DATABASE_URL`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `SIGNAL_NOTIFY_THRESHOLD`, `SIGNAL_SYMBOLS`, optional `APP_BASE_URL`.
- Email templates + sending helpers live in `backend/api/email.py`. They already support confirmation + reactivation with HTML/text variants and tokens stored in `email_subscribers`.
- We use `psycopg` (v3) + SQLAlchemy 2.0. Do **not** reintroduce `psycopg2`.

---

## 6. Frontend Notes

- Next.js 16 App Router with Bun runtime. Entry pages: `/` (marketing + signup), `/dashboard`, `/signals/[symbol]`, `/admin/*` (subscriber views).
- Data fetching currently uses lightweight client hooks; adoption of TanStack Query (#25) + better charts (#28, #29) tracked on the project board.
- For UI work, run `bun run lint && bun run type-check`, then manually verify in the browser. There are no Jest/Cypress suites yet.
- To inspect runtime/component tree, use Next.js MCP (`nextjs_runtime`) rather than scraping files manually.

---

## 7. Email & Notifications

- `backend/api/email.py` centralizes templates (HTML + text) plus Resend sends for subscribe/confirm/reactivate flows. Tokens live in `email_subscribers` and are surfaced via `/confirm/[token]` on the frontend.
- `pipe/flows/notification_dispatcher.py` is the single entry point for outbound signal alerts. It filters by `SIGNAL_NOTIFY_THRESHOLD`, respects confirmation status, and can either log or send via Resend depending on environment setup.
- When adjusting copy or cadence, update the templates + docs simultaneously and keep unsubscribe tokens working (links are generated server-side, rendered client-side).

---

## 8. Working Agreements

1. **Docs-first**: When behavior changes, update `docs/ARCHITECTURE.md`, `docs/MVP.md`, `docs/OPERATIONS.md`, etc., before merging code. Capture medium/long-term ideas as GitHub issues on the project board.
2. **Issues before implementation**: Open a GitHub issue with `.github/ISSUE_TEMPLATE/task.md` and add it to the “Signals – Tasks” board before making non-trivial changes.
3. **No automated tests (for now)**: Architecture is still in flux. Validate manually (run Prefect flows, hit `/health`, exercise the dashboard). The plan for reintroducing tests is tracked in issue #36.
4. **Manual validation expectations**: Mention which flows/commands you ran in PR descriptions (e.g., “ran `market_data_sync` locally” or “loaded `/dashboard` and confirmed signals render”).
5. **Secrets**: Never commit `.env*`. Resend/Supabase/PostHog keys belong in env vars or Vercel/Prefect secrets only.
6. **Dependencies**: Use `uv add/remove` for Python; update `requirements.txt` only after changes so Vercel stays in sync. For frontend, prefer Bun (`bun add/remove`).

---

## 9. Staying Aligned

- Source of truth for upcoming work: the "[Signals – Tasks](https://github.com/users/diegovfeder/projects/4/views/1)" GitHub project board. Issues describe *what* to build; this file only describes *how* the system works today.
- Before merging code, double-check that any behavior or configuration changes are reflected in the relevant doc (`ARCHITECTURE`, `MVP`, `OPERATIONS`, runbooks) and that manual validation steps are noted in your PR.
- Keep Python deps synchronized between `pyproject.toml`/`uv.lock` and `backend/requirements.txt` so Vercel deploys deterministically.
- Never commit secrets or `.env*`; update README/docs if new environment variables are required.

This file is intentionally lean—if you notice drift, tighten it rather than adding historical play-by-plays.

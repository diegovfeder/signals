# Repository Guidelines

These instructions keep AI/dev assistants aligned with how the Signals stack currently works (November 2025).

## Project Structure & Ownership

- `backend/` – FastAPI app under `api/` with routers in `api/routers/`. Uses **uv** for dependency management and ships to Vercel (functions runtime). `requirements.txt` exists solely for Vercel builds; local dev relies on `uv sync` / `uv run`.
- `frontend/` – Next.js **16** (App Router) powered by Bun. Routes live in `src/app/`, shared UI in `src/components/`, hooks in `src/lib/`. Prefer the Next.js MCP tooling (`next-devtools`) when inspecting routes or runtime state.
- `pipe/` – Prefect 2 flows (`pipe/flows/`) that orchestrate Yahoo ingestion, indicator calc, signal generation, and notifications. Reusable tasks live in `pipe/tasks/`, indicator/strategy logic in `pipe/lib/`.
- `db/` – `schema.sql`, seeds, and docker-compose bootstrap for the shared Postgres database (Supabase prod, Docker locally).
- `docs/` – Architecture, MVP scope, ops guides, and project workflow documentation. See the [project board](https://github.com/users/diegovfeder/projects/4/views/1) for backlog and active work.

## Tooling & Day-to-Day Commands

### Backend & Pipeline (Python + uv)
- Install deps once: `uv sync` (root defaults to creating `.venv`).
- Run API locally: `uv run --directory backend uvicorn api.main:app --reload --port 8000`.
- Prefect flows (from repo root):
  - `uv run --directory pipe python -m pipe.flows.market_data_sync --symbols AAPL,BTC-USD`
  - `uv run --directory pipe python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD`
  - `uv run --directory pipe python -m pipe.flows.notification_dispatcher --min-strength 60`
- Deploy flows: `uv run --directory pipe python -m pipe.deployments.register --work-pool <prefect-pool>`.
- All scripts talk to Postgres via `psycopg` (v3). No `psycopg2` remnants remain.

### Frontend (Next.js 16 + Bun)
- Install deps: `cd frontend && bun install`.
- Dev server: `bun run dev` → http://localhost:3000.
- Quality gates: `bun run lint`, `bun run type-check` (there are **no Jest/Cypress suites yet**).
- Use Next.js MCP (`next-devtools`) for route/component insight instead of guessing file structure.

### Database & Env
- Local Postgres: `docker-compose up -d` seeds schema + data automatically.
- Prod DB: Supabase Session Mode pooler (IPv4, port 5432). Connection lives in `DATABASE_URL` (must use `postgresql+psycopg://` format).
- Required variables (backend + pipe): `DATABASE_URL`, `RESEND_API_KEY`, `RESEND_FROM_EMAIL`, `SIGNAL_SYMBOLS`, `SIGNAL_NOTIFY_THRESHOLD`, optional `APP_BASE_URL`.
- Frontend env: `NEXT_PUBLIC_API_URL` (defaults to local API), optional PostHog keys.

## Deployments & Platform Notes

- **Frontend** + **Backend** ship to Vercel via GitHub integration. CORS is configured to allow all `*.vercel.app` origins so previews work out of the box.
- Vercel installs Python packages using `requirements.txt`; keep it in sync with `pyproject.toml` when adding backend deps, but prefer `uv add` during development.
- **Pipeline** lives in Prefect Cloud with three scheduled flows (10:00/10:15/10:30 PM UTC) plus manual backfill. Update `pipe/deployments/register.py` when schedules or work pools change.
- **Emails** use Resend. Production deliverability requires a custom domain with SPF/DKIM/DMARC—see [issue #18](https://github.com/diegovfeder/signals/issues/18) for the backlog item.

## Working Agreements

- **Docs-first**: Update `docs/ARCHITECTURE.md`, `docs/MVP.md`, or other references before/while changing code. New ideas belong in GitHub issues on the [project board](https://github.com/users/diegovfeder/projects/4/views/1).
- **No automated tests (yet)**: We intentionally paused pytest/front-end test suites while the architecture is in flux. Validate changes manually (run Prefect flows, hit `GET /health`, load dashboard). Only add tests if a task explicitly requests it.
- **Manual verification**: When touching pipeline logic, run the relevant `uv run --directory pipe ...` command. For backend changes, curl `http://localhost:8000/api/signals/` and ensure responses look sane. For frontend tweaks, run `bun run lint && bun run type-check` and test the affected page in the browser.
- **Commits & PRs**: Stick to Conventional Commits (`feat(pipeline): ...`). PRs should call out manual validation (e.g., "ran `market_data_sync`, checked dashboard") instead of automated test output.
- **Security & Secrets**: Never commit `.env*` files. Resend, Supabase, and PostHog keys live in environment variables only.

## Quick Reference

- Daily cadence: `market_data_sync 22:00 UTC` → `signal_analyzer 22:15 UTC` → `notification_dispatcher 22:30 UTC`.
- Default symbols: `BTC-USD`, `AAPL` (override via `SIGNAL_SYMBOLS`).
- Strategies: Configured via `pipe/lib/strategies` with env overrides (`SIGNAL_MODEL_<SYMBOL>`).
- Need tasks/backlog ideas? Check the [project board](https://github.com/users/diegovfeder/projects/4/views/1) and create a GitHub issue using `.github/ISSUE_TEMPLATE/task.md`.

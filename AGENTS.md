# Repository Guidelines

## Project Structure & Module Organization

- `backend/` (FastAPI) keeps application code in `api/` with routers under `api/routers/` and tests in `backend/tests/`.
- `frontend/` (Next.js 15 + Bun) stores routes and UI in `src/app/` and static assets in `public/`.
- `pipe/` houses Prefect orchestration: flows in `flows/`, reusable tasks in `tasks/`, and helpers in `scripts/`.
- `db/` contains migration SQL, schema snapshots, and seeds for local Postgres.
- `docs/` collects architecture notes; add new technical proposals here for discoverability.

## Build, Test, and Development Commands

- `docker-compose up -d` spins up Postgres; export `DATABASE_URL` before hitting the API or flows.
- `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` prepares the backend environment.
- `uvicorn api.main:app --reload --port 8000` (from the backend venv) runs the API with live reload.
- `cd frontend && bun install && bun run dev` serves the dashboard at `http://localhost:3000`.
- `cd pipe && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt` installs pipeline deps; run once with `python -m pipe.flows.signal_generation`.
- `pytest backend/tests -q` verifies the API layer; `cd frontend && bun run lint && bun run type-check` gates UI changes.
- Export `ALPHA_VANTAGE_API_KEY` before invoking Prefect flows; store it in `pipe/.env` for local runs.

## Coding Style & Naming Conventions

- Python follows PEP 8: 4-space indents, snake_case functions, PascalCase models and schemas.
- TypeScript relies on Next.js ESLint defaults; components stay PascalCase, hooks prefixed with `use`, CSS modules stay kebab-case.
- Use descriptive file names (`market_data.tsx`, `calculate_indicators.py`) and colocate domain helpers.
- Keep secrets in `.env`/`.env.local`; never check credentials into git.

## Testing Guidelines

- Mirror routers, services, and tasks in test modules (e.g., `backend/tests/test_signals.py`).
- Mock Yahoo Finance and Resend clients so pytest runs offline and deterministically.
- Add Prefect task tests under `pipe/tests/` (create the folder if absent) and execute with `pytest pipe/tests -q`.
- After backend updates, smoke-test with `curl http://localhost:8000/api/signals/` and reload the dashboard.

## Commit & Pull Request Guidelines

- Follow Conventional Commits (`feat: add rsi guard`, `fix: correct ema window`); include scope when it helps reviewers.
- Keep commits focused; include body details when touching configuration, migrations, or seed scripts.
- PRs need a summary, linked issue, test/validation notes (`pytest`, `bun run lint`), and UI screenshots when applicable.
- Tag the relevant domain owners (backend/frontend/pipeline) and confirm CI passes before requesting review.

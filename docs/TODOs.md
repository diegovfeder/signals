# TODOs

**Last Updated**: October 27, 2025

Actionable task list for the next MVP milestones. Critical-path items appear first; completed work lives at the bottom for reference.

## Critical Path (MVP Must-Haves)

### Data Pipeline (Prefect)

- [x] Asset-specific signal models (per symbol strategies that emit BUY/SELL/HOLD, e.g., crypto momentum vs. stock mean reversion).
- [x] Historical signal replay: run `flows/signal_replay.py` on a schedule and persist metrics to the `backtests` table.
- [x] Flow scheduling: create Prefect Deployments / cron jobs for `historical_backfill`, `signal_generation`, `signal_replay`, and `notification_sender`.
- [ ] Provider QA: document and test the Alpha Vantage + Yahoo fallback path end-to-end using real data.

### Backend & Frontend

- [ ] Deploy FastAPI backend (Railway/Render/Vercel) and update CORS settings.
- [ ] Deploy Next.js frontend to Vercel and wire it to the live API.
- [x] Hook the email signup form to `/api/subscribe` and surface confirmation states in the UI.
- [x] Provide a minimal internal subscriber dashboard (`/admin/subscribers`) and diagnostics console (`/admin/backtests`).

### Email Notifications (Resend)

- [ ] Finalize Resend sandbox sender (or verify custom domain when available).
- [ ] Implement confirmation + welcome templates (double opt-in flow).
- [ ] Configure DKIM/SPF/DMARC once the domain quota frees up.
- [ ] Run end-to-end delivery test (Resend dashboard + screenshot).

## Immediate Next Steps (Next Sprint)

### High Priority

- [x] Finish the strategy engine + BUY/SELL/HOLD thresholds and update the signal scorer accordingly.
- [x] Create a replay runbook: backfill → replay → intraday signals → notification sender; document CLI commands.
- [ ] Deploy backend/frontend + `/admin/backtests` diagnostics page to production and validate round-trip data.
- [x] Update README/docs with provider architecture, `/admin` usage, and env vars (`RESEND_FROM_EMAIL`, `SIGNAL_NOTIFY_THRESHOLD`, etc.).

### Medium Priority

- [ ] Monitoring & observability: structured logs for Prefect flows, Slack/Resend alerts on failures, metrics for signal/email volume.
- [ ] Data quality: enforce OHLCV validation (non-negative prices, gap detection, duplicate filtering) and surface indicator failures.
- [ ] UX polish: toast notifications for API errors, share buttons on signal cards, improved mobile responsiveness.
  - [ ] This should be really thought of. Think on how would a user want to share this? How can we make a share card image and text/link that describes it in a cool way and invites another user.
- [ ] Clean up legacy scripts (`pipe/seed_mvp_data.py`, `pipe/test_fetch.py`, `pipe/calculate_and_signal.py`) once the production pipeline stabilizes.

## Known Issues & Technical Debt

### Critical

- **Monitoring gap**: Deployments exist but alerts/observability are minimal; add Prefect notifications + dashboards.
- **Historical signals missing**: until the replay flow runs regularly, the `signals` table only has the latest row per symbol.

### Medium

- **Temporary scripts**: move/remove the legacy seeding/fetch scripts under `scripts/`.
- **Email domain**: Resend sandbox works but custom domain is unverified (blocked by DNS quota) – track status.

### Low

- **Automated tests**: none yet (unit, integration, E2E).
- **Error handling**: add retries, circuit breakers, graceful DB reconnection.

## Phase 2 (Post-MVP)

### Advanced Features

- MACD / Bollinger Bands / ADX support.
- Market hours handling + cooldown policy.
- Asset-specific strategies for additional tickers (GOOGL, TSM, SPY, etc.).

### User Experience

- Auth via Supabase, portfolio tracking, Telegram/weekly digests, richer signal history charts/backtesting views.

### Operational

- Data quality gates, circuit breakers, Ops alerts, email deliverability tracking, Timescale compression, rate limiting, Redis caching.

### Code Quality & DX

- Add Ruff for linting/formatting, optional pre-commit hooks, VS Code integration.

### Monetization

- Stripe payments, freemium tiers, analytics dashboard, referral program, external API tier.

## Completed

### Database & Historical Data

- [x] Initialize schema via `db/schema.sql`.
- [x] Seed baseline data and verify minimum bars per symbol.

### Pipeline Foundations

- [x] Unified Prefect flow with fetch → indicators → signals → notify tasks.
- [x] Alpha Vantage intraday fetch + Yahoo chart fallback for daily history.
- [x] Refactored provider layer (`data/sources`) and added `/admin/backtest` diagnostics page to validate pipeline → DB → API → UI.

### BE & FE

- [x] CRUD endpoints for signals, history, market data, and indicators.
- [x] Subscription endpoints (opt-in / unsubscribe) and health check.
- [x] Next.js dashboard, detail page, dark theme redesign, auto-refresh, loading/error states.

### Email

- [x] Integrated Resend (sandbox) with HTML/text templates for signal notifications; added `SIGNAL_NOTIFY_THRESHOLD` + `RESEND_FROM_EMAIL` env vars.

## Progress Summary

- ✅ Modern UI + API + Prefect pipeline running locally.
- ✅ Alpha Vantage intraday + Yahoo fallback provides 2-year history per symbol.
- ✅ Diagnostics page (`/admin/backtest`) verifies the data path after every flow run.
- ⏳ Remaining gap: production deploy + monitoring/alerting; strategies and scheduled flows are in place.

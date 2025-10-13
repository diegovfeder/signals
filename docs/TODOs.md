# TODOs

Actionable task list for MVP development. Focus on critical path first.

## Critical Path (MVP Must-Haves)

### Database & Historical Data
- [ ] Run `python scripts/setup_db.py` to initialize schema
- [ ] Run `python scripts/seed_historical_data.py` to backfill ~60 days
- [ ] Verify data loaded: `psql $DATABASE_URL -c "SELECT symbol, COUNT(*) FROM market_data GROUP BY symbol;"`
- [ ] Ensure minimum bars for indicators (need 27+ bars per symbol for EMA-26)

### Data Pipeline (Prefect)
- [ ] Implement `flows/signal_generation.py` with 4 tasks:
  - [ ] `fetch_market_data()` - Yahoo Finance → `market_data` table
  - [ ] `calculate_indicators()` - RSI + EMA → `indicators` table
  - [ ] `generate_signals()` - Apply rules → `signals` table
  - [ ] `send_notifications()` - Email strong signals (strength ≥70)
- [ ] Test flow locally: `python -m flows.signal_generation`
- [ ] Deploy to Prefect Cloud with 15-minute schedule
- [ ] Verify first live run completes successfully

### Backend API (FastAPI)
- [ ] Implement `GET /api/signals/` (list all signals, with filters)
- [ ] Implement `GET /api/signals/{symbol}` (latest signal per symbol)
- [ ] Implement `POST /api/subscribe/` (double opt-in email flow)
- [ ] Implement `POST /api/subscribe/unsubscribe/{token}`
- [ ] Test all endpoints with Swagger UI (`/api/docs`)
- [ ] Deploy to Vercel

### Frontend (Next.js)
- [ ] Landing page with hero, live signals preview, email signup
- [ ] Dashboard page: signal cards grid (4 assets)
- [ ] Signal detail page: chart with RSI/EMA overlays, reasoning, risk warnings
- [ ] Email signup form with double opt-in confirmation message
- [ ] Deploy to Vercel

### Email Notifications (Resend)
- [ ] Create Resend account and get API key
- [ ] Implement confirmation email template (double opt-in)
- [ ] Implement welcome email template (what to expect)
- [ ] Implement signal notification template (plain English, strength, reasoning)
- [ ] Configure DKIM/SPF/DMARC for custom domain
- [ ] Test email delivery (check spam folder)

## Phase 2 (Post-MVP)

### Advanced Features
- [ ] ADX regime detection (trend vs range markets)
- [ ] Market hours handling (skip signals when stocks/ETFs closed)
- [ ] Cooldown policy (max 1 signal per 8 hours per symbol)
- [ ] More indicators: MACD, Bollinger Bands
- [ ] Asset-specific strategies (different rules per asset type)

### User Experience
- [ ] User authentication (Supabase auth)
- [ ] Portfolio tracking (track which signals user acted on)
- [ ] Telegram notifications (in addition to email)
- [ ] Weekly digest email (summary of week's signals)
- [ ] Mobile-responsive dashboard improvements

### Operational
- [ ] Data quality gates (gap detection, staleness checks, spike filtering)
- [ ] Circuit breaker (pause signals on data issues or flow failures)
- [ ] Ops alerts (Slack notifications for missed runs, zero signals, bounces)
- [ ] Email deliverability tracking (Resend webhooks for opens, clicks, bounces)
- [ ] TimescaleDB compression (archive OHLCV >90 days old)

### Monetization
- [ ] Payment system (Stripe integration)
- [ ] Freemium model (BTC-USD free, paid for all 4 assets)
- [ ] Analytics dashboard for paid users
- [ ] Premium features (more assets, more indicators, priority support)

## Reference

**See domain READMEs for implementation details:**
- Database: `db/README.md`
- Pipeline: `pipe/README.md`
- Indicators: `data/README.md`
- API: `backend/README.md`
- Setup: `scripts/README.md`

**See docs for concepts:**
- MVP scope: `docs/MVP.md`
- Architecture: `docs/ARCHITECTURE.md`
- Indicators: `docs/DATA-SCIENCE.md`
- Terms: `docs/GLOSSARY.md`

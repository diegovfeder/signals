# TODOs

**Last Updated**: October 15, 2025

Actionable task list for MVP development. Focus on critical path first.

## Critical Path (MVP Must-Haves)

### Database & Historical Data
- [x] Initialize database schema (`db/schema.sql` applied via docker-compose)
- [x] Seed test data (using mock data scripts as workaround)
- [x] Verify data loaded (200 market_data + 200 indicators + 4 signals)
- [x] Ensure minimum bars for indicators (50 bars per symbol seeded)

### Data Pipeline (Prefect)
- [x] Create unified flow `flows/signal_generation.py` with tasks:
  - [x] `fetch_ohlcv()` - Yahoo Finance → `market_data` table
  - [x] `calculate_and_upsert_indicators()` - RSI + EMA → `indicators` table
  - [x] `generate_and_store_signal()` - Apply rules → `signals` table
  - [x] `notify_if_strong()` - Log strong signals (email in Phase 2)
- [ ] Fix Yahoo Finance integration (currently hanging)
- [ ] Test flow locally end-to-end with real Yahoo Finance data
- [ ] Deploy to Prefect Cloud with 15-minute schedule
- [ ] Verify first live run completes successfully

### Backend API (FastAPI)
- [x] Implement `GET /api/signals/` (list all signals, with filters)
- [x] Implement `GET /api/signals/{symbol}` (latest signal per symbol)
- [x] Implement `GET /api/signals/{symbol}/history`
- [x] Implement `GET /api/market-data/{symbol}/ohlcv`
- [x] Implement `GET /api/market-data/{symbol}/indicators`
- [x] Implement `POST /api/subscribe/` (stores to DB, generates tokens)
- [x] Implement `POST /api/subscribe/unsubscribe/{token}`
- [x] Implement `GET /health` with database connection test
- [x] Fix UUID serialization for Pydantic v2
- [x] Test all endpoints with Swagger UI (`/api/docs`)
- [ ] Deploy to Vercel

### Frontend (Next.js)
- [x] Landing page with hero, live signals preview, email signup
- [x] Dashboard page: signal cards grid (4 assets with glass morphism)
- [x] Signal detail page: strength meter, reasoning, back button
- [x] Redesign with Resend-inspired dark theme
- [x] Create 8 reusable components (Navbar, Hero, ValueProps, etc.)
- [x] Fix Next.js 15 async params issue
- [x] Migrate to TailwindCSS 4.0
- [x] Implement auto-refresh (60 seconds)
- [x] Add loading and error states
- [ ] Deploy to Vercel

### Email Notifications (Resend)
- [ ] Create Resend account and get API key
- [ ] Implement confirmation email template (double opt-in)
- [ ] Implement welcome email template (what to expect)
- [ ] Implement signal notification template (plain English, strength, reasoning)
- [ ] Configure DKIM/SPF/DMARC for custom domain
- [ ] Test email delivery (check spam folder)

## Immediate Next Steps (Tomorrow)

### High Priority
- [ ] **Fix Yahoo Finance Integration**
  - Debug yfinance library timeout issue
  - Consider alternatives: Alpha Vantage, Polygon.io, Twelve Data
  - Test with different intervals (1h instead of 15m)
  - Implement retry logic and timeout handling

- [ ] **Clean Up Temporary Scripts**
  - Delete `pipe/seed_mvp_data.py` (once real data works)
  - Delete `pipe/test_fetch.py` (debugging script)
  - Integrate `pipe/calculate_and_signal.py` logic into main flow
  - Or keep in `scripts/` for manual testing

- [ ] **Deploy to Production**
  - Deploy frontend to Vercel
  - Deploy backend to Vercel (or Railway/Render)
  - Update CORS settings for production domains
  - Test end-to-end in production

- [ ] **Documentation**
  - Update README.md with deployment URLs
  - Document environment variables for production
  - Add screenshots to docs/
  - Create DEPLOYMENT.md with step-by-step guide

### Medium Priority
- [ ] **Monitoring & Observability**
  - Add logging to Prefect flow
  - Set up error notifications (email or Slack)
  - Monitor API response times
  - Track signal generation frequency

- [ ] **Data Quality**
  - Add validation for OHLCV data (no negative prices, volume)
  - Detect data gaps and handle gracefully
  - Log when indicators can't be calculated (insufficient data)

- [ ] **User Experience**
  - Add toast notifications for errors
  - Implement email signup form (connect to `/api/subscribe`)
  - Add "Share" button to signal cards
  - Improve mobile responsiveness

## Known Issues & Technical Debt

### Critical
- **Yahoo Finance Integration**: yfinance library hangs during fetch (no data returned after 5 minutes)
  - Workaround: Using mock data seeding scripts
  - Impact: Can't test with real market data
  - Priority: HIGH - blocks production deployment

### Medium
- **Temporary Scripts**: Need cleanup once real data pipeline works
  - `pipe/seed_mvp_data.py`
  - `pipe/test_fetch.py`
  - `pipe/calculate_and_signal.py`

- **Email Notifications**: Not implemented (Phase 2)
  - Subscribe endpoint stores to DB but doesn't send email
  - No confirmation flow
  - No signal alerts

### Low
- **Tests**: No automated tests yet
  - Unit tests for indicators (pytest)
  - Integration tests for API endpoints
  - E2E tests for frontend

- **Error Handling**: Could be more robust
  - Add retry logic to Yahoo Finance fetches
  - Handle database connection failures gracefully
  - Add circuit breaker pattern

## Phase 2 (Post-MVP)

### Advanced Features
- [ ] MACD indicator (schema already supports it)
- [ ] Bollinger Bands
- [ ] ADX regime detection (trend vs range markets)
- [ ] Market hours handling (skip signals when stocks/ETFs closed)
- [ ] Cooldown policy (max 1 signal per 8 hours per symbol)
- [ ] Asset-specific strategies (different rules per asset type)
- [ ] More assets (ETH, TSLA, SPY, etc.)

### User Experience
- [ ] User authentication (Supabase auth)
- [ ] Portfolio tracking (track which signals user acted on)
- [ ] Telegram notifications (in addition to email)
- [ ] Weekly digest email (summary of week's signals)
- [ ] Mobile-responsive dashboard improvements
- [ ] Signal history charts (performance tracking)
- [ ] Backtesting view (historical signal performance)

### Operational
- [ ] Data quality gates (gap detection, staleness checks, spike filtering)
- [ ] Circuit breaker (pause signals on data issues or flow failures)
- [ ] Ops alerts (Slack notifications for missed runs, zero signals, bounces)
- [ ] Email deliverability tracking (Resend webhooks for opens, clicks, bounces)
- [ ] TimescaleDB compression (archive OHLCV >90 days old)
- [ ] Rate limiting on API endpoints
- [ ] Caching layer (Redis for frequently accessed data)

### Code Quality & Developer Experience
- [ ] Add Ruff for Python linting and formatting
  - Replaces flake8 + black + isort in one modern, fast tool
  - Zero-config with sensible defaults
  - Install: `pip install ruff` in backend and pipe venvs
  - Add `ruff.toml` configuration at project root
  - Run: `ruff check .` for linting, `ruff format .` for formatting
  - Optional: Add pre-commit hooks for auto-formatting on commit
  - Consider VS Code extension: `charliermarsh.ruff`

### Monetization
- [ ] Payment system (Stripe integration)
- [ ] Freemium model (BTC-USD free, paid for all 4 assets)
- [ ] Analytics dashboard for paid users
- [ ] Premium features (more assets, more indicators, priority support)
- [ ] Referral program
- [ ] API access tier

## Project Structure Notes

### Pipeline vs Scripts
- **`pipe/`**: Production pipeline code (Prefect flows, tasks)
  - Should only contain production-ready code
  - Mock/test scripts should be temporary

- **`scripts/`**: One-off utility scripts for manual operations
  - Database setup/seeding
  - Data backfills
  - Testing/debugging
  - Keep mock data generators here once cleaned up

### Recommended Cleanup
```bash
# Move temporary scripts to scripts/
mv pipe/seed_mvp_data.py scripts/testing/seed_mock_data.py
mv pipe/test_fetch.py scripts/testing/test_yahoo_finance.py
mv pipe/calculate_and_signal.py scripts/testing/manual_signal_gen.py

# Or delete once real pipeline works
rm pipe/seed_mvp_data.py pipe/test_fetch.py pipe/calculate_and_signal.py
```

## Reference

**See domain READMEs for implementation details:**
- Database: `db/README.md`
- Pipeline: `pipe/README.md`
- Indicators: `pipe/data/README.md` (moved from root)
- API: `backend/README.md`
- Setup: `scripts/README.md`

**See docs for concepts:**
- MVP scope: `docs/MVP.md`
- Architecture: `docs/ARCHITECTURE.md`
- Indicators: `docs/DATA-SCIENCE.md`
- Terms: `docs/GLOSSARY.md`
- Implementation details: `docs/IMPLEMENTATION_SUMMARY.md`

## Progress Summary

**October 15, 2025 Achievements:**
- ✅ Full MVP functional with modern UI
- ✅ Python 3.13 environment working
- ✅ Database seeded with 200+ records
- ✅ Backend API serving 4 signals
- ✅ Frontend completely redesigned (Resend-inspired)
- ✅ Landing page with 8 reusable components
- ✅ TailwindCSS 4.0 migration complete
- ✅ Next.js 15 compatibility fixed

**Remaining for Production:**
- ⏳ Fix Yahoo Finance integration
- ⏳ Deploy to Vercel
- ⏳ Clean up temporary scripts
- ⏳ Add email notifications (Phase 2)

# TODOs

**Last Updated**: November 1, 2025

Actionable task list for the next MVP milestones. Sprint-based approach with time estimates and success criteria.

---

## 🎯 Production Readiness: 60%

### ✅ What's Done
- Backend API (100%) - All endpoints working
- Pipeline (100%) - Deployed to Prefect Cloud, running daily at 10 PM UTC
- Database (100%) - Schema complete, running in Docker
- Indicators (100%) - RSI + EMA fully implemented
- Signal Strategies (100%) - Crypto momentum + Stock mean reversion
- Email Templates (100%) - HTML/text templates ready for Resend

### 🔴 What's Blocking Production
1. **Frontend TypeScript error** - `useSubscribers()` hook type inference broken → can't build/deploy
2. **No Vercel deployments** - Backend + Frontend sitting locally only
3. **Confirmation emails not wired** - Backend has TODO comments for double opt-in
4. **Documentation drift** - README mentions old flow names, CLAUDE.md outdated

### ⏱️ Time to Production: 4-6 hours

---

## Sprint 1: Fix & Deploy (Critical Path - 3 hours)

**Goal**: Get to production with working deployments

### Task 1: Fix TypeScript Build Error (30 min) 🔴 BLOCKER

**Problem**: `frontend/src/app/admin/subscribers/page.tsx:16` - type inference failure

**Files to modify**:
- `frontend/src/lib/hooks/useSignals.ts`
  - Fix `useSubscribers` hook return type
  - Replace deprecated `keepPreviousData: true` with `placeholderData: keepPreviousData`
- `frontend/src/app/admin/subscribers/page.tsx`
  - Ensure proper type handling for subscribers data

**Validation**:
```bash
cd frontend && npm run build
# Must succeed without TypeScript errors
```

---

### Task 2: Deploy Backend to Vercel (1 hour)

**Steps**:
1. Run `cd backend && vercel deploy --prod`
2. Set environment variables in Vercel dashboard:
   - `DATABASE_URL` - Supabase connection string with `+psycopg` suffix
   - `RESEND_API_KEY` - From Resend dashboard
   - `CORS_ORIGINS=["https://your-frontend.vercel.app"]`
   - `ENVIRONMENT=production`
3. Test health endpoint

**Validation**:
```bash
curl https://your-backend.vercel.app/health
# Should return: {"status": "healthy", "database": "connected"}
```

---

### Task 3: Deploy Frontend to Vercel (1 hour)

**Steps**:
1. Run `cd frontend && vercel deploy --prod`
2. Set environment variables in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL=https://your-backend.vercel.app`
   - `NEXT_PUBLIC_POSTHOG_KEY` (optional analytics)
   - `NEXT_PUBLIC_POSTHOG_HOST` (optional analytics)
3. Test signup flow on live site

**Validation**:
- Visit deployed URL
- See signals dashboard with live data
- Test email signup form
- Verify API calls work (check Network tab)

---

### Task 4: Verify Prefect Flows (30 min)

**Steps**:
1. Run `prefect deployment ls` to confirm all 4 flows deployed
2. Check Prefect Cloud UI for recent flow runs
3. Manually trigger `market_data_sync` flow to test
4. Verify signals appear in production database

**Validation**:
- Prefect shows successful runs
- `signals` table has recent data (within last 24h)
- Dashboard shows fresh signals

---

## Sprint 2: Email Flow (Phase 2 - 2 hours)

**Goal**: Complete double opt-in and notification emails

### Task 5: Wire Up Confirmation Emails (1.5 hours)

**Files to modify**:
- `backend/api/routers/subscribe.py`
  - Remove TODO comments on lines 119, 143
  - Import email sending function from pipeline
  - Call email function after creating subscriber
  - Create welcome email template (HTML + text)

**Implementation**:
```python
# In subscribe.py after creating subscriber
from pipe.tasks.email_sending import send_confirmation_email

# Send confirmation email
await send_confirmation_email(
    email=subscriber.email,
    confirmation_token=subscriber.confirmation_token
)
```

**Validation**:
1. Subscribe via frontend
2. Receive confirmation email in inbox
3. Click confirmation link
4. See "Email confirmed" message

---

### Task 6: Configure Resend Production Domain (30 min)

**Steps**:
1. Add custom domain in Resend dashboard
2. Configure DNS records:
   - DKIM record
   - SPF record
   - DMARC record
3. Wait for verification (usually 10-15 min)
4. Update `RESEND_FROM_EMAIL` to use custom domain (e.g., `signals@yourdomain.com`)
5. Test deliverability

**Validation**:
- Emails arrive from custom domain (not `onboarding@resend.dev`)
- Emails don't land in spam
- DKIM/SPF pass (check email headers)

---

## Sprint 3: Cleanup (Optional - 2 hours)

**Goal**: Remove dead code and fix documentation drift

### Task 7: Remove Dead Code (1 hour)

**Decision Required**: Keep Alpha Vantage as fallback or delete?

**If deleting** (recommended for MVP simplicity):
- [ ] Remove `pipe/lib/api/alpha_vantage.py` (361 lines)
- [ ] Remove `ALPHA_VANTAGE_API_KEY` from deployment env vars
- [ ] Update `pipe/tasks/market_data.py` to only use Yahoo Finance
- [ ] Update TODOs.md line 14 to remove "(Alpha Vantage removed from MVP)" note

**If keeping** (for future expansion):
- [ ] Update TODOs.md to clarify it's a fallback provider
- [ ] Add comment in `alpha_vantage.py` explaining when it's used
- [ ] Keep env var but mark as optional

**Also cleanup**:
- [ ] Remove stub functions in `pipe/lib/data/validation.py` OR implement them properly
  - Currently all checks return empty errors (no validation running)
  - Options: Delete file, or implement basic checks (non-negative prices, gap detection)

---

### Task 8: Update Documentation (1 hour)

**Files to fix**:

1. **README.md**:
   - Line 48: Update path reference `pipe/data/sources` → `pipe/lib/api/`
   - Lines 73-84: Update flow names to match actual implementation:
     - ❌ Old: `historical_backfill`, `signal_generation`, `notification_sender`
     - ✅ New: `market_data_backfill`, `market_data_sync`, `signal_analyzer`, `notification_dispatcher`

2. **CLAUDE.md**:
   - Update "single unified flow" references to reflect 4-flow architecture
   - Add section documenting the 4 flows and their responsibilities
   - Update deployment instructions to match current setup

3. **docs/TODOs.md** (this file):
   - Mark Sprint 1 tasks as completed after deployment
   - Move Sprint 2 tasks to "In Progress" when started
   - Archive old completed items

---

## Success Criteria

### After Sprint 1 (Critical Path):
- ✅ Frontend builds without TypeScript errors
- ✅ Backend deployed and accessible at public URL
- ✅ Frontend deployed and showing live signals
- ✅ Prefect flows running on schedule (daily at 10 PM UTC)
- ✅ Users can visit site and subscribe (even if confirmation email is Phase 2)
- ✅ `/health` endpoint returns database connected
- ✅ Dashboard fetches real data from API

### After Sprint 2 (Email Flow):
- ✅ Subscribers receive confirmation emails
- ✅ Confirmation links work (update `confirmed` flag)
- ✅ Subscribers receive signal notification emails when strength ≥ 70
- ✅ Unsubscribe links work
- ✅ Emails arrive from custom domain (not sandbox)
- ✅ DKIM/SPF records pass

### After Sprint 3 (Polish):
- ✅ No dead code or stub functions
- ✅ Documentation matches implementation
- ✅ All TODOs removed from main codebase
- ✅ Clean git history ready for new features
- ✅ Decision made on Alpha Vantage (keep or remove)

---

## Known Issues & Technical Debt

### 🔴 Critical (Blocking Production)
- **Frontend TypeScript error**: `useSubscribers()` hook type inference broken
  - File: `frontend/src/app/admin/subscribers/page.tsx:16`
  - Impact: Can't build/deploy frontend
  - Fix: 30 min (Sprint 1 Task 1)

### 🟡 High Priority
- **No production deployments**: Backend + Frontend sitting locally
  - Impact: No public access, can't onboard users
  - Fix: 2 hours (Sprint 1 Tasks 2-3)
- **Confirmation emails not wired**: Backend has TODO comments
  - Files: `backend/api/routers/subscribe.py:119, 143`
  - Impact: Users subscribe but don't get emails
  - Fix: 1.5 hours (Sprint 2 Task 5)
- **Documentation drift**: README, CLAUDE.md outdated
  - Impact: Confusion for new contributors
  - Fix: 1 hour (Sprint 3 Task 8)

### 🟢 Medium Priority
- **TanStack Query deprecated API**: Using `keepPreviousData: true`
  - Should use: `placeholderData: keepPreviousData`
  - Impact: Works but shows warnings, may break in future updates
- **Data validation stubs**: `pipe/lib/data/validation.py` not implemented
  - Impact: No data quality checks running
  - Options: Delete or implement properly
- **Alpha Vantage code**: Still exists despite TODOs saying "removed from MVP"
  - Impact: 361 lines of unused code (if truly unused)
  - Decision needed: Keep as fallback or delete?

### Low Priority
- **Monitoring gap**: Deployments exist but alerts/observability are minimal
  - Need: Prefect notifications, Slack/email alerts, metrics dashboard
- **Automated tests**: None yet (unit, integration, E2E)
  - Would catch type errors like the current blocker
- **Environment variable sprawl**: 10+ env vars across 3 projects
  - No central validation or documentation
- **Error handling**: Add retries, circuit breakers, graceful DB reconnection

---

## Recommended Order

**🚨 TODAY (Critical)**: Sprint 1 Tasks 1-4 → Get to production (3 hours)
**📧 THIS WEEK**: Sprint 2 Tasks 5-6 → Complete email flow (2 hours)
**🧹 NEXT WEEK**: Sprint 3 Tasks 7-8 → Polish and cleanup (2 hours)

**Total Time Investment**: 6-7 hours to full production MVP

---

## Phase 2 (Post-MVP)

### Advanced Features
- MACD / Bollinger Bands / ADX support
- Market hours handling + cooldown policy
- Asset-specific strategies for additional tickers (ETFs, more stocks)
- Multi-timeframe analysis (1h, 4h, daily)

### User Experience
- Auth via Supabase (user accounts)
- Portfolio tracking (track your own positions)
- Telegram bot for notifications
- Weekly digest emails
- Richer signal history charts
- Interactive backtesting UI

### Operational
- Data quality gates (detect anomalies, gaps, outliers)
- Circuit breakers (stop pipeline if data quality fails)
- Ops alerts (Slack/email for pipeline failures)
- Email deliverability tracking (open rates, bounces)
- Timescale compression (optimize database storage)
- Rate limiting (protect API from abuse)
- Redis caching (speed up repeated queries)

### Code Quality & DX
- Add Ruff for linting/formatting
- Pre-commit hooks (run tests before commit)
- VS Code integration (settings.json, extensions)
- CI/CD pipeline (GitHub Actions)
- Automated tests (pytest, Jest, Playwright)

### Monetization
- Stripe payments integration
- Freemium tiers (free: 2 symbols, pro: unlimited)
- Analytics dashboard (user engagement, signal performance)
- Referral program (give 1 month free for referrals)
- External API tier (sell API access to other platforms)

---

## Completed ✅

### Database & Historical Data
- [x] Initialize schema via `db/schema.sql`
- [x] Seed baseline data and verify minimum bars per symbol
- [x] Support for 2 symbols: BTC-USD (crypto), AAPL (stock)
- [x] Unique constraints prevent duplicate data

### Pipeline Foundations
- [x] 4-flow Prefect architecture:
  - `market_data_backfill` - Historical data for new symbols
  - `market_data_sync` - Daily updates at 10:00 PM UTC
  - `signal_analyzer` - RSI/EMA calculation at 10:15 PM UTC
  - `notification_dispatcher` - Email sending at 10:30 PM UTC
- [x] Yahoo Finance daily OHLCV fetch for all symbols
- [x] RSI + EMA indicator calculations
- [x] Asset-specific signal strategies:
  - Crypto momentum (BTC-USD)
  - Stock mean reversion (AAPL)
- [x] Signal generation with strength scoring (0-100)
- [x] Reasoning output (plain English explanations)
- [x] Deployed all flows to Prefect Cloud
- [x] Migrated all pipeline commands to uv package manager
- [x] Idempotency via unique constraints (prevent duplicate signals)

### Backend & Frontend
- [x] FastAPI backend with all CRUD endpoints:
  - `/api/signals/*` - List, get by symbol, history
  - `/api/market-data/*` - OHLCV, indicators
  - `/api/subscribe/*` - Subscribe, unsubscribe, list
  - `/api/backtests/*` - Backtest summaries
  - `/health` - Database connection test
- [x] SQLAlchemy ORM models matching schema
- [x] Pydantic response schemas for type safety
- [x] Next.js 15 frontend with App Router
- [x] Signal dashboard with auto-refresh
- [x] Dark theme redesign
- [x] Loading/error states
- [x] Admin dashboards:
  - `/admin/subscribers` - Manage email list
  - `/admin/backtests` - View signal performance
- [x] Email signup form connected to `/api/subscribe`
- [x] Unsubscribe token generation

### Email Infrastructure
- [x] Resend integration (sandbox mode)
- [x] HTML/text email templates for signal notifications
- [x] Environment variables: `SIGNAL_NOTIFY_THRESHOLD`, `RESEND_FROM_EMAIL`
- [x] Email sending code in `pipe/tasks/email_sending.py`
- [x] Notification logic in `notification_dispatcher` flow

### Documentation & Brand
- [x] BRAND.md - Single source of truth for messaging
- [x] Target user: "The Analytical Amateur" (28-40, tech professionals)
- [x] Brand identity: "Market insights made human"
- [x] Tagline: "Automated market signals you can actually read"
- [x] Updated all docs to reflect 2 symbols (removed IVV, BRL=X)
- [x] Updated schedule references (daily at 10 PM UTC, not every 15 min)

### Infrastructure
- [x] PostgreSQL Docker setup with auto-initialization
- [x] Environment variable templates (`.env.example` files)
- [x] Vercel deployment configs (`vercel.json`)
- [x] Database connection pooling with psycopg
- [x] CORS middleware configured

---

## Archive (Historical Context)

### Old TODOs (Pre-Sprint Reorganization)
- Provider QA: document and test Yahoo Finance (Sprint 3)
- Deploy backend/frontend (Sprint 1 Tasks 2-3)
- Monitoring & observability (Phase 2)
- Data quality validation (Sprint 3 or Phase 2)
- UX polish (Phase 2)
- Clean up legacy scripts (Sprint 3)

### Decisions Made
- Removed IVV and BRL=X from MVP scope (focus on 2 symbols)
- Changed schedule from 15-minute intervals to daily at 10 PM UTC
- Chose Yahoo Finance over Alpha Vantage for MVP
- Implemented 4-flow architecture (not single unified flow)
- Target user: "The Analytical Amateur" (not generic retail traders)

# Trading Signals MVP - Overview

## What Are We Building?

A dashboard that watches **Bitcoin and Ethereum only**, analyzes them using technical indicators every 15 minutes, and tells busy professionals when to consider buying or selling via email alerts.

## The One-Sentence Pitch

"Get automated trading signals for crypto, explained in plain English, so you don't miss opportunities while you're at work."

## ⚠️ Scope Refinements (Expert Feedback Integrated)

### Original Plan vs Refined MVP

| Aspect | Original | **Refined (RECOMMENDED)** |
|--------|----------|---------------------------|
| Assets | BTC, ETH, TSLA | **BTC-USD, ETH-USD only** |
| Timeframe | 1-hour bars | **15-minute bars** |
| Indicators | RSI + MACD | **RSI + EMA crossover** |
| Channels | Email | **Email only (DKIM/SPF/DMARC)** |
| Updates | Hourly | **Every 15 minutes** |

**Why These Changes?**

✅ **Crypto Only:**

- TSLA adds market hours complexity (9:30-4pm ET)
- Different volatility patterns
- Mixing asset classes dilutes focus for MVP

✅ **15-Minute Bars:**

- More actionable for day trading
- Catches intraday swings
- Still manageable data volume

✅ **RSI + EMA (not MACD):**

- Simpler to explain
- EMA crossover is universally understood
- MACD = Phase 2

✅ **Email Only:**

- One integration to perfect
- Better deliverability control
- Telegram = Phase 2

## Why This Matters

### The Problem: Meet Maria

Maria is a software engineer who wants to invest in Bitcoin but:

- She's in meetings during market hours
- She doesn't understand RSI, MACD, or technical analysis
- She panic-sold BTC during a dip and lost money
- She's too busy to watch charts all day

### Our Solution

Every 15 minutes, our system:

1. Checks BTC-USD, ETH-USD prices
2. Calculates RSI (14-period) + EMA crossover (12/26)
3. **Checks market regime** (trending vs ranging)
4. Generates a signal **only if regime allows**
5. Explains WHY in plain English
6. Emails her only if strength > 70 **AND cooldown period passed**

## MVP Scope (4 Weeks)

### IN SCOPE

**Assets:**

- BTC-USD (Bitcoin)
- ETH-USD (Ethereum)
- 15-minute candles
- Crypto markets only (24/7)

**Technical Approach:**

- RSI (14-period) - oversold/overbought detection
- EMA Crossover (12/26) - trend confirmation
- **Regime Detection (ADX or range index)** - market context
- **Cooldown: 1 signal per asset per 8 hours**

**User Experience:**

- Public dashboard (no login required)
- Email notifications for strong signals (>70/100)
- Plain English explanations
- Double opt-in for email signup
- One-click unsubscribe

**Data Pipeline:**

- Ingest every 5 minutes (create 15-min resampled views)
- Quality gates (reject gaps, stale data, >5% jumps)
- Prefect orchestration
- PostgreSQL storage

### OUT OF SCOPE (Phase 2)

- ❌ More symbols (wait for validation)
- ❌ Stock markets (TSLA, etc.)
- ❌ MACD indicator (keep it simple)
- ❌ Telegram/SMS notifications
- ❌ User accounts/authentication
- ❌ Portfolio tracking
- ❌ Mobile app
- ❌ Payment system

## Success Criteria

### Primary Goal

- **100 people sign up for email alerts in 30 days**

### Core Metrics (What Actually Matters)

1. **Activation Rate** - % of subscribers who click a signal within 7 days
   - Target: >20%
   - Measures: Do they care?

2. **Engagement** - Clicks per active user per week
   - Target: 2+ clicks/week
   - Measures: Do they return?

3. **Fatigue Rate** - Unsubscribes within 24h of signal
   - Target: <5%
   - Measures: Are we spamming?

4. **Data Health** - % of jobs on time with valid bars
   - Target: >95%
   - Measures: Is the system reliable?

### Secondary Metrics

- Email open rate: >25%
- Signal click-through: >15%
- Qualitative: 10+ people say "I traded based on your signal"

## Tech Stack

```bash
Frontend:  Next.js 15 + TypeScript + TailwindCSS
Backend:   FastAPI (Python) + PostgreSQL
Pipeline:  Prefect + Yahoo Finance API
Deploy:    Vercel (frontend + API) + Prefect Cloud
Analytics: PostHog (events: signal_generated, email_opened, signal_clicked, unsubscribed)
Email:     Resend (with DKIM/SPF/DMARC configured)
```

## How Data Flows

### Every 15 Minutes

```md
1. Prefect fetches last 5 minutes of data from Yahoo Finance
2. Resample to 15-minute bars
3. Run quality gates (reject bad data)
4. Calculate RSI + EMA
5. Detect market regime (trending/ranging/uncertain)
6. Generate signal ONLY if:
   - Regime allows it (trend for EMA, range for RSI)
   - Strength > 70
   - Cooldown period passed (8 hours)
7. Store signal in PostgreSQL
8. Send email to subscribers (idempotent)
9. Track event in PostHog
```

### User Flow

```md
1. User visits landing page
2. Sees live BTC signal: "STRONG BUY (82/100)"
3. Reads: "RSI oversold (28) in ranging market. Mean-reversion setup."
4. Enters email (double opt-in)
5. Receives confirmation email
6. Gets alerts when strong signals occur
7. Clicks, views dashboard
8. (Hopefully) trades based on signal
```

## Key Decisions Made

| Decision | Why | Risk Mitigation |
|----------|-----|-----------------|
| Crypto only (no TSLA) | Avoid market hours complexity | Clear in landing page copy |
| 15-min bars | More actionable than hourly | Higher data volume (manageable) |
| RSI + EMA (no MACD) | Simpler to explain | MACD in Phase 2 if needed |
| Email only | Perfect one channel first | Telegram in Phase 2 |
| Regime detection | Avoid signals in wrong context | ADX or simple range index |
| 8-hour cooldown | Prevent alert fatigue | Configurable per asset |
| Strength threshold (70) | Only high-confidence signals | Tuned via micro-backtest |

## Signal Engine Guardrails

### Regime Logic

```python
if regime == "trending":
    allow_ema_crossover_signals()
elif regime == "ranging":
    allow_rsi_mean_reversion_signals()
else:  # uncertain
    no_signals()
```

### Cooldown

- Max 1 signal per asset per rule per 8 hours
- Prevents spam during choppy markets

### Idempotency

```python
idempotency_key = f"{asset_id}:{timeframe}:{rule_version}:{signal_open_time}"
```

- Prevents duplicate signals if job reruns

### Plain English Template

```text
"RSI crossed below 30 in a ranging market.
Mean-reversion setup.
Risk is high during news."
```

## Tiny Calibration (Not "Backtesting")

Run offline on last 90 days per asset to determine:

- Win rate (target: >55%)
- Average excursion (how far price moves)
- Best cooldown period (6h vs 8h vs 12h)

**Output:** Threshold values, not PnL theatrics

## Ops & Safety

### Global Kill Switch

Disable signal generation if:

- Data is stale (>10 minutes old)
- Jobs fail twice in a row
- Deliverability drops below 90%

### Alerts

- Missed cron job
- Zero signals generated in 24 hours
- Email bounce rate spike

### Runbook

- How to reprocess a bad bar
- How to resend failed notifications
- How to manually disable a rule

## Four-Week Plan (Revised)

### Week 1: Data Foundation

- [x] PostgreSQL schema (signals, notifications tables)
- [ ] Yahoo Finance ingestion (5-min intervals)
- [ ] 15-minute resampling logic
- [ ] Quality gates (gap detection, staleness checks)
- [ ] Prefect flow scheduling
- [ ] RSI + EMA calculations
- [ ] Regime detection (ADX or range index)

**Milestone:** Can query indicators in database for BTC/ETH

### Week 2: Signal Engine + Email

- [ ] Signal generation with regime logic
- [ ] Cooldown enforcement
- [ ] Idempotency checks
- [ ] Resend setup (DKIM/SPF/DMARC)
- [ ] Email templates with plain English
- [ ] Double opt-in flow
- [ ] PostHog event tracking

**Milestone:** Can send test email with real signal

### Week 3: Calibration + Safety

- [ ] Micro-backtest on 90 days data
- [ ] Tune thresholds (strength, cooldown)
- [ ] Fat-finger checks (reject obvious errors)
- [ ] Global kill switch implementation
- [ ] Alert system (Slack/email for ops)
- [ ] Runbook documentation

**Milestone:** System runs autonomously with safety nets

### Week 4: Launch

- [ ] Landing page (clear promise + risk disclaimer)
- [ ] "How it works" explainer page
- [ ] Seed list (friends, Twitter followers)
- [ ] Send real signals
- [ ] Monitor activation, engagement, fatigue
- [ ] Iterate based on feedback

**Milestone:** 100 email signups, measure key metrics

## Nice-to-Have After MVP

- Telegram bot integration
- MACD indicator variant
- 1-hour timeframe for swing traders
- Per-user watchlists
- Timezone-aware email scheduling
- Model registry for A/B testing thresholds
- More crypto assets (SOL, BNB, etc.)

## Risk Disclosure

⚠️ **Important:** This is NOT financial advice.

- Signals are algorithmic and may be wrong
- Past performance does not guarantee future results
- Trade at your own risk
- We are an educational tool, not a licensed advisor

## Next Steps for You

1. Read `01-PROBLEM-AND-SOLUTION.md` - understand Maria's pain
2. Read `02-ARCHITECTURE.md` - see system design with regime logic
3. Read `05-INDICATORS-EXPLAINED.md` - understand RSI/EMA
4. Read `06-SIGNAL-GENERATION.md` - see regime-based rules
5. Start Week 1 implementation

## Glossary (Quick Reference)

- **Signal:** BUY or HOLD recommendation (no SELL in ranging markets)
- **Regime:** Market context (trending, ranging, uncertain)
- **Strength:** Confidence score 0-100 for a signal
- **Cooldown:** Minimum time between signals for same asset
- **OHLCV:** Open, High, Low, Close, Volume price data
- **RSI:** Relative Strength Index (0-100)
- **EMA:** Exponential Moving Average
- **ADX:** Average Directional Index (regime detection)
- **Idempotency:** Same input = same output (prevents duplicates)
- **Fat-finger:** Obvious data error (e.g., price spike)

---

**Version:** 0.1.0 (Revised with expert feedback)
**Last Updated:** January 2025
**Status:** Ready for Week 1 implementation

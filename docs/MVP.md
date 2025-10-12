# MVP Scope - Trading Signals

## What We're Building

An automated trading signals system that helps busy professionals catch opportunities across multiple asset classes without watching charts 24/7.

## The One-Sentence Pitch

"Get automated trading signals across crypto, stocks, ETFs, and forex—explained in plain English, so you don't miss opportunities while you're at work."

## Target User

### Maria - The Busy Professional

**Profile:**

- 32-year-old software engineer
- Works 9am-7pm, often in meetings
- Has $15K to invest across crypto, stocks, and ETFs
- Overwhelmed by multiple markets and conflicting advice

**Pain Points:**

- "I missed the BTC dip and AAPL earnings because I was in meetings"
- "I can't track crypto, stocks, ETFs, and forex all at once"
- "I don't know what RSI means or how indicators work"
- "I don't trust myself to make trading decisions across different markets"

**What She Needs:**

- Actionable signals in plain English
- Notifications only for high-confidence opportunities
- Understand WHY a signal occurred
- Build trading intuition over time

## Core Features

### 1. Signal Generation

- Monitor 4 assets across different classes every 15 minutes
- Calculate RSI and EMA indicators (same logic for all assets)
- Generate BUY/HOLD signals based on simple rules
- Score signal strength (0-100)
- Only send emails for strong signals (>70)

### 2. Email Notifications

- Plain English explanations
- Include current price, signal strength, and reasoning
- Risk warnings on every email
- One-click unsubscribe
- Max 3 alerts per day per asset (no spam)

### 3. Public Dashboard

- See latest signals without login
- View signal history
- Charts with indicators overlaid
- Educational tooltips

### 4. Simple Data Pipeline

- Fetch 15-minute data from Yahoo Finance
- Store in Supabase
- Run Prefect flow every 15 minutes
- Quality checks (reject stale data)

## MVP Scope

### ✅ In Scope

**Assets (4 diversified types):**

- **Crypto**: BTC-USD (Bitcoin)
- **Stocks**: AAPL (Apple)
- **ETF**: IVV (iShares Core S&P 500)
- **Forex**: BRL=X (Brazilian Real / US Dollar)
- 15-minute candles for all assets

**Indicators:**

- RSI (14-period) - oversold/overbought detection
- EMA (12/26 periods) - trend detection
- No MACD, Bollinger Bands, or other indicators yet

**User Experience:**

- Public dashboard (no login)
- Email notifications (Resend API)
- Double opt-in for subscriptions
- Plain English explanations
- Risk disclaimers

**Tech Stack:**

- Frontend: Next.js 15 + Vercel
- Backend: FastAPI
- Database: Supabase (PostgreSQL)
- Pipeline: Prefect (1 simple flow)
- Email: Resend

### ❌ Out of Scope (Phase 2)

**Not Building Yet:**

- More assets per category (expand after validation)
- Additional indicators (MACD, Bollinger Bands)
- Asset-specific strategies (different indicators per asset type)
- Market hours handling (stocks/ETFs closed on weekends)
- Telegram/SMS notifications
- User authentication/accounts
- Portfolio tracking
- Mobile app
- Payment system
- Real-time websocket updates

## How It Works

### User Flow

1. **Discovery**: Maria visits landing page, sees latest signals across multiple assets
2. **Signup**: Enters email, receives confirmation link
3. **Activation**: Clicks confirmation, receives welcome email
4. **Engagement**: Gets email when strong signal occurs (any asset)
5. **Action**: Clicks through to dashboard, compares signals across asset types
6. **Learning**: Reads explanations, builds intuition across markets

### Technical Flow

```text
Every 15 minutes:
1. Prefect flow triggers
2. Fetch data for all 4 assets from Yahoo Finance (15m bars)
3. Calculate RSI and EMA indicators for each asset
4. Apply signal rules (RSI < 30 = BUY, etc.) - same logic for all
5. Calculate signal strength (0-100) per asset
6. Save all signals to Supabase
7. If any signal has strength > 70, send email via Resend
8. Track events in PostHog
```

## Signal Rules (Simplified)

### RSI Signals

- RSI < 30 → BUY (oversold, likely to bounce)
- RSI > 70 → HOLD (overbought, wait for pullback)
- RSI 30-70 → HOLD (neutral zone)

### EMA Signals

- EMA-12 crosses above EMA-26 → BUY (bullish momentum)
- EMA-12 crosses below EMA-26 → HOLD (bearish, stay out)

### Signal Strength

- Weighted score based on:
  - How far RSI is from 30/70
  - How clear the EMA crossover is
  - Volume confirmation
- Only email if strength > 70

## Success Criteria

### Primary Goal

**100 email signups in 30 days** after launch

### Core Metrics

1. **Activation Rate**
   - Definition: % of subscribers who click a signal within 7 days
   - Target: >20%
   - Why it matters: Shows they care

2. **Engagement**
   - Definition: Clicks per active user per week
   - Target: 2+ clicks/week
   - Why it matters: Shows they return

3. **Fatigue Rate**
   - Definition: Unsubscribes within 24h of signal
   - Target: <5%
   - Why it matters: Shows we're not spamming

4. **Data Reliability**
   - Definition: % of Prefect flows that complete successfully
   - Target: >95%
   - Why it matters: Trust in the system

### Qualitative Success

- 10+ people say "I traded based on your signal"
- 5+ people say "I learned something new"
- 0 people say "This feels like spam"

## Risk Mitigation

### Legal Risk

- Clear disclaimers: "Not financial advice"
- No personalized recommendations
- Educational focus, not prescriptive
- Consult lawyer before monetizing

### Reputation Risk

- Risk warnings on every signal
- Emphasis on learning, not profits
- HOLD signals when uncertain
- Historical performance (win rate, not PnL)

### Technical Risk

- Quality gates (reject stale/bad data)
- Alert system for Prefect failures
- Manual override ability
- Start small (2 assets, 2 indicators)

## Go-to-Market Strategy

### Week 1-2: Friends & Family

- Personal outreach to friends interested in investing (not just crypto)
- Seed list who agreed to test
- Goal: 20 signups, 5 active users

### Week 3-4: Niche Communities

- Post on r/CryptoCurrency, r/StockMarket, r/ETFs
- Personal Twitter/LinkedIn posts
- Goal: 80+ signups, 20+ active users

### Month 2-3: Content Marketing

- Blog posts: "How I automated multi-asset trading signals"
- Product Hunt launch
- Goal: 500+ signups, 10% activation

## Development Timeline

### Week 1: Data Foundation

- [ ] Set up Supabase database
- [ ] Create database schema (assets, ohlcv, indicators, signals)
- [ ] Build Prefect flow: Fetch data from Yahoo Finance for all 4 assets
- [ ] Store raw 15m data in Supabase
- **Milestone**: Can query prices for all 4 assets in database

### Week 2: Indicators & Signals

- [ ] Implement RSI calculation
- [ ] Implement EMA calculation
- [ ] Build signal generation logic
- [ ] Add signal strength scoring
- [ ] Store signals in database
- **Milestone**: See signals generated in database

### Week 3: Email & Frontend

- [ ] Set up Resend account
- [ ] Build email templates
- [ ] Implement double opt-in flow
- [ ] Build Next.js landing page
- [ ] Build dashboard with signal cards
- **Milestone**: Send test email to yourself

### Week 4: Polish & Launch

- [ ] Add charts with indicators
- [ ] Write plain English explanations
- [ ] Add risk disclaimers
- [ ] Test end-to-end flow
- [ ] Deploy to Vercel
- [ ] Invite seed list
- **Milestone**: 20 signups, 5 active users

## Key Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| 4 diverse assets | Validate appeal across asset classes | More complex than single asset type |
| Same indicators for all | Simpler to build and explain | Not optimized per asset type |
| 15-min bars (no resampling) | Simpler pipeline, faster MVP | Less control over timeframes |
| 2 indicators only | Easy to explain, faster to build | Less sophisticated signals |
| Email only | Perfect one channel first | Missing Telegram users |
| Supabase (not Neon) | You already know it | Vendor lock-in |
| 1 Prefect flow | Learn incrementally | Less modularity |
| No authentication | Faster MVP, public dashboard | Can't personalize later |
| Ignore market hours (MVP) | Simpler logic, 24/7 operation | Signals during closed markets |

## Anti-Goals

Things we're explicitly NOT doing:

- ❌ Build a trading bot (we generate signals, not execute trades)
- ❌ Guarantee profits (we're educational, not a money machine)
- ❌ Support 50+ assets (focus on 4 representative assets first)
- ❌ Asset-specific optimization (same indicators for all assets in MVP)
- ❌ Real-time updates (15-minute delay is fine)
- ❌ Mobile app (responsive web is enough)
- ❌ Social features (comments, upvotes, etc.)

## Principles

1. **Start small, learn fast** - 4 assets, 2 indicators, 1 flow
2. **Solo dev friendly** - Use tools you know (Supabase, Vercel)
3. **Education over prediction** - Teach users, don't just tell them
4. **Transparency over black boxes** - Document the logic
5. **Quality over quantity** - Strong signals only (>70 strength)
6. **Asset-agnostic approach** - Same indicators work across all asset types

## Next Steps

1. Read [ARCHITECTURE.md](ARCHITECTURE.md) - See how components connect
2. Read [DATA-SCIENCE.md](DATA-SCIENCE.md) - Understand RSI and EMA
3. Set up local development environment (see root README.md)
4. Start Week 1: Database setup and Prefect flow

---

**Version**: 1.0.0
**Last Updated**: 2025-01-20
**Status**: Ready for implementation

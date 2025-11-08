# MVP Scope – Trading Signals

> **Last Updated**: 2025-11-06  
> **Status**: Production MVP live (daily pipeline + public dashboard)

Signals helps busy, data-minded investors keep tabs on Bitcoin and Apple with explainable, confidence-scored signals delivered via dashboard and daily digest emails. This page captures the current scope, the user promise, and how we measure success. Deep architectural details now live in [docs/ARCHITECTURE.md](ARCHITECTURE.md).

---

## 1. Product In One Minute

- **Promise**: "Automated BTC + AAPL signals explained in plain English so you never miss a move after work."
- **Stack**: Next.js 16 (Bun) · FastAPI · Prefect · PostgreSQL · Yahoo Finance · Resend.
- **Data care**: Up to 10 years of daily candles, refreshed nightly at 22:00 UTC and re-scored 15 minutes later.
- **Delivery**: Public dashboard (marketing + `/dashboard`), symbol detail pages, and opt-in email alerts with reasoning + confidence (0–100).
- **Tone**: Calm, transparent, "teach first" copy (see `docs/resources/BRAND.md`).

---

## 2. Target User – The Analytical Amateur

| Attribute | Detail |
| --- | --- |
| Age | 28–40 |
| Role | ICs in tech (software, design, analytics, product) |
| Portfolio | $10k–$25k spread over blue-chip equities + BTC |
| Behaviors | Checks markets after work, wants concise insights, distrusts hype |
| Motivation | "If I understand the signal, I can trust it." |

Success = users feel informed, not overwhelmed. Content must explain RSI/EMA shifts plainly, highlight risk, and stay under 200 words per signal/email.

---

## 3. Current Scope (Nov 2025)

| Area | What’s Live |
| --- | --- |
| Assets | `BTC-USD`, `AAPL` (daily candles). Additional assets come after reliability targets. |
| Indicators | RSI (14), EMA 12/26, MACD histogram. All recomputed from stored OHLCV; no on-the-fly calls. |
| Strategies | `CryptoMomentum` + `StockMeanReversion` (see `pipe/lib/strategies`). Configurable via env overrides per symbol. |
| Delivery Channels | Public site + dashboard, admin-only subscriber views, Resend-powered confirmation/reactivation emails, optional strong-signal digest. |
| Data Freshness | Historical backfill up to 10y; nightly sync/analyzer/notification flows at 22:00/22:15/22:30 UTC. |
| Deployments | Frontend + backend on Vercel, pipeline on Prefect Cloud, database on Supabase. |

---

## 4. Data & Pipeline Highlights

1. **Yahoo-only ingestion** keeps legal/security review simple. `pipe/lib/api/yahoo.py` abstracts HTTP + retries.
2. **Backfill**: `uv run --directory pipe python -m pipe.flows.market_data_backfill --backfill-range 10y` runs once per symbol to seed enough history for indicators/backtests.
3. **Daily sync** handles weekends by always fetching last 5 bars and deduping on `(symbol, timestamp)`.
4. **Indicators** (RSI/EMA/MACD) live in `pipe/tasks/indicators.py` and are recalculated on every analyzer run to guard against upstream revisions.
5. **Signals** carry the reasoning string + `rule_version` (strategy name) so we can audit how explanations evolve over time.
6. **Notifications** respect `SIGNAL_NOTIFY_THRESHOLD` (default 60). Prefect logs show exactly which signals cross the bar even when emailing is disabled.

---

## 5. User Experience

### Landing + Dashboard
- Hero + sections highlight trust and education.
- `<SubscribeForm />` sits on landing, dashboard, and detail pages; all share the same hook + toast UX.
- `/dashboard` lists the two assets, exposes confidence, trend notes, and recent history without login.
- `/signals/[symbol]` shows indicator overlays via Chart.js (daily candles only).

### Email Flow
1. User subscribes via frontend → `POST /api/subscribe`.
2. Backend stores subscriber row, sends confirmation (Resend) with CTA linking to `/confirm/[token]`.
3. Once confirmed, nightly notifier sends strong signals (text + HTML) with reasoning, price, and unsubscribe link.
4. Users can unsubscribe via tokenized endpoint or admin tooling.

---

## 6. Success Metrics

| Metric | Target (MVP) |
| --- | --- |
| Email signups | 100 within 30 days |
| Activation | 20% click at least one signal within 7 days |
| Email open rate | ≥25% |
| Delivery rate | ≥90% (Resend dashboard) |
| Pipeline reliability | ≥95% successful daily runs |
| Qualitative | 10+ users report acting on a signal; 5+ say they "learned something" |

We only expand asset coverage or indicators after we hit reliability + comprehension goals above.

---

## 7. What’s Next

Work-in-progress and future tasks now live in GitHub Issues + the "Signals – Tasks" GitHub Project board (seeded from `docs/TASK_SEEDS.md`). Today’s top themes:

1. **Email polish** – Double opt-in edge cases, resend confirmations, deliverability monitoring.
2. **Dashboard UX** – Expose indicator deltas, add stronger storytelling per signal.
3. **Pipeline resilience** – Provider fallback detection, Prefect alerting, historical replay tooling.
4. **Data expansion** – Evaluate ETFs/forex once BTC + AAPL hit engagement goals.
5. **Strategy & scoring research** – Refine RSI/EMA weightings, explore Bollinger + asset-specific models for richer reasoning.

---

## 8. Out of Scope (Still True)

- Automated trading / order execution
- User authentication, billing, or role-based dashboards
- High-frequency (≤15m) candles
- Social/community features
- Mobile app (responsive web only)

---

## 9. Archive & Change Log

- 2025-11-06 – Reframed document around live scope; sprint checklists moved to GitHub issues.
- 2025-01-20 – Initial MVP spec (timeline + weekly plan). Pull from git history if you need the detailed weekly plan.

Need something clarified? Start with [ARCHITECTURE.md](ARCHITECTURE.md) for deep dives or open a GitHub issue for product questions.

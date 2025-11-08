# Task Seeds for GitHub Issues

> **Purpose**: Capture well-defined backlog ideas distilled from the retired `WARP.md` so they can be converted into GitHub issues / project cards without re-reading historical docs.
>
> **How to use**: Copy any row/section into a new issue using `.github/ISSUE_TEMPLATE/task.md`, keep the bolded "Outcome" as the title seed, and include the bullets as scope/DoD items.

---

## 1. Data Coverage & Indicator Depth

| Outcome | Why It Matters | Key Steps / Acceptance |
| --- | --- | --- |
| **Add ETF coverage (QQQ) with 10y history** | Validates multi-asset promise beyond BTC + AAPL and exercises long-range backfill. | - Backfill 10y `QQQ` via `market_data_backfill` (ensure PREFECT + Supabase storage).<br>- Create/update strategy mapping (likely mean reversion variant).<br>- Update frontend copy + tables to include ETF badge.<br>- Extend tests/seed data to cover third symbol. |
| **Add forex pair (EURUSD=X) to daily pipeline** | Demonstrates ability to span forex; stresses timezone handling. | - Fetch + store Yahoo Finance pair symbol (test weekend gaps).<br>- Adjust pipeline env defaults (`SIGNAL_SYMBOLS`).<br>- Add strategy selection + reasoning copy tuned for FX. |
| **Introduce MACD + Bollinger indicators** | Users keep asking for richer technical context; schema already has nullable MACD fields. | - Implement Bollinger calc in `pipe/lib/indicators` and persist.<br>- Expose MACD histogram (already computed) + Bollinger bands through API endpoints.<br>- Update frontend charts to toggle indicators. |
| **Asset-specific strategies by class** | Current logic shares thresholds; needs tailored behavior per asset type. | - Split strategy config into crypto/stock/ETF/forex modules.<br>- Wire env overrides (`SIGNAL_MODEL_<SYMBOL>`).<br>- Document reasoning differences in emails + dashboard. |

---

## 2. Notification & Email Delivery

| Outcome | Why It Matters | Key Steps / Acceptance |
| --- | --- | --- |
| **Buy production domain + set up DKIM/SPF/DMARC** | Resend deliverability + brand trust require custom domain and DNS hygiene. | - Pick domain (e.g., `signals.fyi`).<br>- Configure DNS records (SPF, DKIM, DMARC, return-path).<br>- Verify domain in Resend + document renewal plan. |
| **Ship production notification dispatcher** | Currently logging to console; need live email blast for strength ≥ threshold. | - Move Resend calls into Prefect `notification_dispatcher` (retry-aware).<br>- Respect `SIGNAL_NOTIFY_THRESHOLD` and per-subscriber confirmation state.<br>- Add audit rows to `sent_notifications`. |
| **Harden email flow (List-Unsubscribe + webhooks)** | Improves compliance and measurement once emails go live. | - Add `List-Unsubscribe` headers to backend email module.<br>- Stand up webhook endpoint to record bounces/complaints.<br>- Update docs with playbook for monitoring via Resend dashboard. |
| **Polish double opt-in UX + resend confirmations** | Users occasionally miss the first email; need resilient confirmation loop + deliverability monitoring. | - Add "resend confirmation" endpoint + frontend CTA.<br>- Surface confirmation status in admin view and allow manual resend.<br>- Track bounce/complaint metrics and document triage steps. |
| **Expire confirmation tokens after 7 days** | Stale tokens are a security risk and confuse users. | - Add `confirmation_expires_at` column + backfill data.<br>- Reject expired tokens with helpful messaging + resend option.<br>- Rotation logic for re-subscribe/reactivate flows. |
| **Richer reasoning + signal summary email** | Differentiator is human-friendly explanation; current template is minimal. | - Pull RSI/EMA deltas into template.<br>- Highlight time-to-next-refresh and risk disclaimer.<br>- Add CTA to `/signals/{symbol}` page. |
| **Move transactional emails to background queue** | Sync email sends block HTTP requests and risk timeouts. | - Add task runner (Prefect task or lightweight background worker) to send emails asynchronously.<br>- Persist send attempts + retry policy.<br>- Ensure API returns immediately and surfaces send status in logs/admin UI. |

---

## 3. Frontend Experience & Platform Capabilities

| Outcome | Why It Matters | Key Steps / Acceptance |
| --- | --- | --- |
| **Adopt TanStack Query across dashboard pages** | Current client hooks manually manage fetching; Query simplifies caching/polling. | - Replace `useSignals` and related hooks with TanStack Query + stale time aligned to daily cadence.<br>- Ensure SSR-safe usage (Next.js 16 App Router).<br>- Add retry/backoff + loading skeletons tied to query states. |
| **Basic authentication for admin views** | Admin routes are currently open; minimal auth protects subscriber data. | - Add passwordless magic link or Supabase-auth gating for `/admin/*`.<br>- Restrict API routes (subscriber list) accordingly.<br>- Document local overrides for development. |
| **Portfolio tracking MVP** | Users want to log positions + see signal impact. | - Add lightweight table to capture user-provided holdings.<br>- Show personalized signal suggestions (e.g., highlight assets user owns).<br>- Defer to static demo data if auth not ready. |
| **Improve chart overlays & storytelling** | Signal detail charts need clearer RSI/EMA/Bollinger layers and better "last updated" cues. | - Refactor Chart.js datasets to toggle indicators + highlight thresholds.<br>- Add copy/legend updates explaining indicator context.<br>- Optimize mobile view + loading skeleton to avoid layout shift. |
| **Expose indicator deltas + narrative on dashboard** | Users should see how RSI/EMA changed since last run to grasp momentum quickly. | - Compute deltas in API response (or client) and render badges/tooltips.<br>- Add "last updated" + narrative block per asset.<br>- Ensure responsive layout + accessible color coding. |

---

## 4. Messaging & Channel Expansion

| Outcome | Why It Matters | Key Steps / Acceptance |
| --- | --- | --- |
| **Telegram notification bot** | Many users prefer instant messaging alerts. | - Create bot + store token securely.<br>- Build simple Prefect task to post when signals exceed threshold.<br>- Allow users to link Telegram chat ID via subscribe flow. |
| **Lifecycle experiment: weekly digest email** | Complements real-time alerts with educational recap. | - Aggregate best signals + stats once a week.<br>- Generate narrative (top mover, RSI swing) and send via Resend.<br>- Add unsubscribe preference for digests vs realtime. |

---

## 5. Operations & Reliability

| Outcome | Why It Matters | Key Steps / Acceptance |
| --- | --- | --- |
| **Prefect failure alerts + incident playbook** | Today we notice pipeline failures manually; proactive alerts keep nightly runs trustworthy. | - Configure Prefect notification policies (email/Slack) for failed runs + retry exhaustion.<br>- Document severity levels + on-call steps in `docs/OPERATIONS.md`.<br>- Add checklist for pausing/resuming deployments after incidents. |
| **Provider fallback + retry metrics** | Yahoo hiccups can stall the pipeline; visibility + a fallback keep data fresh. | - Instrument provider errors/retries (Prometheus-style counters or Prefect logs summary).<br>- Evaluate secondary source (e.g., Twelve Data) for emergency fills.<br>- Surface stats in admin/backoffice or Prefect dashboard notes. |
| **Historical replay tooling** | Need the ability to replay missed days or simulate new logic against stored OHLCV. | - Build CLI/Prefect flow to run analyzer over arbitrary date ranges and write results to `signals_replay` table.<br>- Provide diff report vs. production signals.<br>- Document when/how to replay during incidents or strategy updates. |
| **Ops runbook refresh** | Operators need current SOPs for manual backfill, DNS/email changes, etc. | - Update `docs/resources/OPERATIONS.md` with screenshots + latest commands (uv, Bun, Prefect UI).<br>- Add explicit manual backfill SOP + DNS checklist for email domain work.<br>- Version stamp the doc and link it from README. |

---

## 6. Engineering Foundations

| Outcome | Why It Matters | Key Steps / Acceptance |
| --- | --- | --- |
| **Plan first automated test slice (later)** | We intentionally paused automated tests during architecture churn; capture the eventual re-entry plan. | - Define smallest valuable target (e.g., indicator math + one API contract) and document fixtures.<br>- Add instructions for running `pytest`/`bun test` when we flip the switch.<br>- Leave clear TODO in docs so future contributors know tests are currently optional. |

---

## 7. Strategy & Scoring Research

| Outcome | Why It Matters | Key Steps / Acceptance |
| --- | --- | --- |
| **Refine RSI/EMA weighting & narrative** | Better scoring improves trust; current weights are static across assets. | - Analyze historical signals vs. outcomes, adjust weighting curves per symbol class.<br>- Update `pipe/lib/strategies` reasoning strings to highlight main drivers (RSI bounce, EMA spread, etc.).<br>- Add regression tests or notebooks documenting before/after metrics. |
| **Explore Bollinger-assisted strategies** | Bollinger Bands were requested for richer context; need a concrete plan. | - Prototype band calculations alongside existing indicators.<br>- Define entry/exit heuristics for BTC vs. AAPL (e.g., band squeeze + RSI confirmation).<br>- Gate rollout via feature flag/env override per symbol. |

---

## 8. Reference Items from WARP.md (for archival cross-check)

- Phase 2 wishlist also mentioned: Market hours handling, Telegram notifications, User authentication, Portfolio tracking, advanced indicators (MACD/Bollinger), and expanded asset coverage. All are represented in the sections above—use this table as the source of truth going forward.
- Email improvements require domain purchase + DNS entries (SPF/DKIM/DMARC) plus List-Unsubscribe/webhook handling before flipping notifications to live sends.
- Frontend fetching should move toward TanStack Query for caching/polling once backend endpoints stabilize.

Update this file whenever new long-range ideas surface so the GitHub board stays lean and execution-ready.

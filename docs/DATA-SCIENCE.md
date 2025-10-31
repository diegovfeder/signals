# Data Science & Signal Logic

_Last updated: October 2025_

This note explains how we fetch data, compute indicators, and translate them into BUY/SELL/HOLD decisions after the strategy-registry refactor. Share it with anyone designing new heuristics or reviewing signal quality.

---

## 1. Data Inputs

| Source | Usage | Notes |
| --- | --- | --- |
| **Alpha Vantage** | Intraday slices (1–60 min) for live signals. | Rate-limited to ~5 req/min on the free tier. We throttle via `_ALPHA_RATE_LOCK`. |
| **Yahoo Finance chart API** | Daily history (up to ~20 years) and fallback when Alpha throttles. | Used by the historical backfill + replay flow. |
| **PostgreSQL** | Canonical storage (`market_data`, `indicators`, `signals`). | All downstream tasks read/write here. |

All timestamps are stored in UTC. Daily history is backfilled at the start to guarantee enough bars for RSI/EMA and backtesting.

---

## 2. Indicators

We currently calculate three indicators per bar:

| Indicator | Settings | Why |
| --- | --- | --- |
| **RSI** | 14-period, standard Wilder smoothing. | Detects overbought/oversold conditions and reclaims. |
| **EMA Fast / Slow** | 12-period and 26-period | Captures short vs. medium trend strength. |
| **MACD Histogram** | `EMA(12) - EMA(26)` smoothed with 9-period signal line. | Provides momentum confirmation and divergence hints. |

Implementation lives in `pipe/tasks/indicators.py` (pandas). We always round to 6 decimals before inserting to avoid float drift between replays.

---

## 3. Strategy Registry

Every signal request flows through the registry at `pipe/data/signals/strategies/`. A strategy receives:

```python
StrategyInputs(
    symbol="BTC-USD",
    timestamp=ts,
    price=last_close,
    rsi=latest_row.rsi,
    ema_fast=latest_row.ema_fast,
    ema_slow=latest_row.ema_slow,
    macd_hist=latest_row.macd_hist,
)
```

and returns a `StrategyResult(signal_type, reasoning: list[str], strength: float)`.

### 3.1 Default Mappings

| Symbol | Strategy | Rationale |
| --- | --- | --- |
| `BTC-USD` | `CryptoMomentumStrategy` | BTC trends violently — we prioritize momentum bursts and overbought profit-taking. |
| `AAPL`, `IVV`, `BRL=X` | `StockMeanReversionStrategy` | These behave more mean-reverting on the daily timeframe — RSI reclaims and EMA compression work better. |
| Any unmapped symbol | `HoldStrategy` | Keeps us in HOLD until a bespoke model is defined. |

Override mappings via environment variables, e.g. `SIGNAL_MODEL_ETH_USD=crypto_momentum`.

### 3.2 Crypto Momentum Strategy

Heuristics (`pipe/data/signals/strategies/crypto_momentum.py`):

- **BUY triggers**
  - RSI reclaiming 35–45 after a dip (`rsi > 35` and `rsi_delta > 3` over the past 3 bars).
  - EMA12 above EMA26 by >0.35% and widening (momentum confirmation).
  - MACD histogram positive and growing.
  - Strength increases when all three agree; capped at 90 to leave room for future signals.
- **SELL triggers**
  - RSI > 72 and rolling over, or MACD histogram crosses below zero while price makes a marginal new high.
  - EMA spread collapsing by >40% over the past 3 bars.
- **HOLD**
  - Default fallback when signals disagree; reasoning explains which requirement failed (e.g., “RSI still neutral”).

### 3.3 Stock Mean-Reversion Strategy

Heuristics (`pipe/data/signals/strategies/stock_mean_reversion.py`):

- **BUY triggers**
  - RSI between 28 and 40 and trending upward (oversold bounce).
  - Close above EMA12 after trading under it for ≥2 bars (momentum flip).
  - EMA12 within 0.2% of EMA26 (compression encourages breakout).
- **SELL triggers**
  - RSI above 70 with EMA12 rolling under EMA26 (take profits).
  - MACD histogram negative for 2 consecutive bars while RSI stays >60.
- **HOLD**
  - When neither bounce nor exhaustion conditions are satisfied.

### 3.4 Hold Strategy

Simple placeholder that emits HOLD with a neutral reasoning line. Useful for assets not yet modeled.

---

## 4. Strength Scoring

- Base strength comes from indicator alignment (RSI distance to trigger, EMA spread percentage, MACD histogram magnitude).
- Crypto model weights momentum 50%, RSI 30%, and mean-reversion clues 20%.
- Stock model weights RSI 50%, EMA compression 30%, MACD 20%.
- SELL strengths are mirrored (e.g., RSI 80 with weakening MACD yields ~65/100). We currently email only when strength ≥ `SIGNAL_NOTIFY_THRESHOLD` (default 70).
- Scores are clamped to `[5, 95]` so UI meters never hit 0 or 100 unless we explicitly decide to.

---

## 5. Extending Strategies

1. Create a new file next to the existing strategies, subclassing the `Strategy` protocol (or a dataclass implementing `generate`).
2. Register it inside `pipe/data/signals/strategies/__init__.py`.
3. Map a symbol via `_DEFAULT_SYMBOL_MAPPING` or an environment variable.
4. Run:

```bash
cd pipe
python -m pipe.flows.signal_replay --symbols BTC-USD,AAPL --range-label 2y
```

to regenerate historical signals and backtests with the new logic.

5. Update this document with the heuristics so downstream teams know what changed.

---

## 6. Subscription Tie-In

Signals with `strength >= SIGNAL_NOTIFY_THRESHOLD` are candidates for email.

- The intraday flow logs strong signals.
- `flows/notification_sender.py` queries for the last strong signal per symbol, fetches confirmed subscribers, and hands the payload to Resend.
- Until email templates ship, the frontend’s `<SubscribeForm />` stores intent so we have a warm list once notifications go live.

---

## 7. Future Ideas

- Add regime detection (ADX) to choose between momentum vs. mean-reversion automatically.
- Support different timeframes (e.g., 4 h for crypto, daily for equities) and aggregate results.
- Expand the strength model into a probabilistic scorer using historical win rates derived from the replay flow.
- Feed realized backtest metrics back into the UI so users can see the rolling win rate per strategy.

Document updates belong here whenever the indicator set, weighting, or strategy heuristics change.

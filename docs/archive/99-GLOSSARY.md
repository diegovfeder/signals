# Glossary

A comprehensive reference of terms, acronyms, and concepts used in the Trading Signals MVP project.

---

## Trading Terms

### ADX (Average Directional Index)

**Definition:** A technical indicator that measures the strength of a trend, regardless of direction.

**Range:** 0-100

- **ADX > 25:** Strong trend (trending market)
- **ADX < 20:** Weak trend (ranging market)
- **20 ≤ ADX ≤ 25:** Uncertain regime (transition phase)

**Usage in our system:** Used for regime detection to determine whether to use EMA crossover signals (trends) or RSI mean-reversion signals (ranges).

**Example:** If BTC has ADX = 32, we classify it as "trending" and allow EMA crossover signals.

**See also:** Regime Detection, Trending Market, Ranging Market

---

### Asset

**Definition:** A tradable financial instrument tracked by our system.

**MVP Scope:** BTC-USD (Bitcoin) and ETH-USD (Ethereum) only.

**Future:** May expand to other cryptocurrencies (SOL, BNB, etc.) or stocks (TSLA, AAPL).

**Database:** Stored in `assets` table with fields: `id`, `name`, `display_name`, `icon_url`.

**See also:** Symbol, Cryptocurrency

---

### ATR (Average True Range)

**Definition:** A volatility indicator that measures price movement range.

**Status:** Not implemented in MVP (potential Phase 2 addition).

**Potential use:** Risk sizing (adjust position size based on volatility).

---

### Backtesting

**Definition:** Testing a trading strategy on historical data to see how it would have performed.

**Our approach:** We do **micro-calibration**, not full backtesting. We run rules on last 90 days to determine thresholds (cooldown period, strength cutoff), not to calculate PnL or win rates for marketing.

**Why limited scope:** Backtesting can be misleading (overfitting, survivorship bias). We focus on logical soundness and user education instead.

**See also:** Calibration, Micro-Backtest

---

### Bar

**Definition:** A single unit of price data containing Open, High, Low, Close, Volume (OHLCV).

**Types:**

- **5-minute bar:** OHLCV data for a 5-minute period
- **15-minute bar:** OHLCV data for a 15-minute period (resampled from 3x 5-min bars)

**Example:**

```bash
timestamp: 2025-01-20 10:15:00
open: 42,350
high: 42,450
low: 42,320
close: 42,410
volume: 1,234,567
```

**See also:** OHLCV, Candle, Timeframe

---

### Breakout

**Definition:** When price moves above resistance (bullish breakout) or below support (bearish breakout).

**Status:** Not explicitly detected in MVP (potential Phase 2 addition).

**Related:** EMA crossovers in trending markets can signal breakouts.

---

### Candlestick

**Definition:** Visual representation of a bar (OHLCV data) on a chart.

**Components:**

- **Body:** Rectangle from open to close (green if close > open, red if close < open)
- **Wick (shadow):** Lines extending to high and low

**Usage:** Frontend charts display candlesticks for OHLCV data.

**See also:** Bar, OHLCV

---

### Cooldown

**Definition:** Minimum time period between signals for the same asset and rule to prevent spam.

**MVP Setting:** 8 hours per asset per rule version.

**Rationale:** Prevents alert fatigue during choppy markets.

**Implementation:** Check `signals` table for any signals in last 8 hours before generating new one.

**Example:** If BTC generates RSI signal at 10:15 AM, next RSI signal cannot occur before 6:15 PM.

**Database:** Enforced via query:

```sql
SELECT EXISTS (
    SELECT 1 FROM signals
    WHERE asset_id = 'BTC-USD'
      AND rule_version = 'rsi_v1'
      AND signaled_at > NOW() - INTERVAL '8 hours'
)
```

**See also:** Alert Fatigue, Spam Prevention

---

### Cryptocurrency

**Definition:** Digital or virtual currency secured by cryptography.

**MVP Assets:** Bitcoin (BTC) and Ethereum (ETH) only.

**Characteristics:**

- **24/7 markets:** No market hours (unlike stocks)
- **High volatility:** Large price swings common
- **Global:** Trade on exchanges worldwide

**Why crypto-only for MVP:** Avoids market hours complexity, higher volatility = more signal opportunities.

**See also:** Asset, Bitcoin, Ethereum

---

### Crossover

**Definition:** When one line crosses above or below another on a chart.

**Types:**

- **Golden Cross:** Fast EMA crosses above slow EMA (bullish signal)
- **Death Cross:** Fast EMA crosses below slow EMA (bearish signal)

**Our implementation:**

- EMA-12 crosses above EMA-26 → BUY signal (in trending markets only)
- EMA-12 crosses below EMA-26 → SELL signal (in trending markets only)

**Code example:**

```python
ema_12_prev <= ema_26_prev and ema_12_curr > ema_26_curr  # Golden cross
```

**See also:** EMA, Golden Cross, Death Cross

---

### Death Cross

**Definition:** When a fast-moving average crosses below a slow-moving average, signaling bearish momentum.

**Our implementation:** EMA-12 crosses below EMA-26 in a trending market.

**Regime requirement:** Only signaled when ADX > 25 (trending market).

**See also:** Crossover, EMA, Golden Cross

---

### Divergence

**Definition:** When price and indicator move in opposite directions (e.g., price makes new high but RSI doesn't).

**Status:** Not implemented in MVP (potential Phase 2 addition).

---

## Indicator Terms

### EMA (Exponential Moving Average)

**Definition:** A moving average that gives more weight to recent prices, making it more responsive to price changes than Simple Moving Average (SMA).

**Formula:**

```text
EMA_today = (Price_today × α) + (EMA_yesterday × (1 - α))
where α = 2 / (period + 1)
```

**Our implementation:**

- **EMA-12:** 12-period EMA (fast line)
- **EMA-26:** 26-period EMA (slow line)

**Usage:** Detect trend direction and momentum via crossovers.

**When it works:** Trending markets (ADX > 25). Unreliable in ranging markets (generates false breakouts).

**See also:** Moving Average, Crossover, Golden Cross

---

### Indicator

**Definition:** A mathematical calculation based on price and/or volume data, used to generate trading signals.

**MVP Indicators:**

- **RSI (Relative Strength Index):** Oversold/overbought detection
- **EMA (Exponential Moving Average):** Trend following
- **ADX (Average Directional Index):** Trend strength

**Future indicators (Phase 2):**

- MACD (Moving Average Convergence Divergence)
- Bollinger Bands
- Volume Profile

**Database:** Stored in `indicators` table with fields: `rsi`, `ema_12`, `ema_26`, `adx`, `regime`.

**See also:** RSI, EMA, ADX

---

### MACD (Moving Average Convergence Divergence)

**Definition:** A trend-following momentum indicator showing the relationship between two EMAs.

**Status:** Postponed to Phase 2 (RSI + EMA are simpler to explain).

**Components:**

- **MACD line:** 12-EMA minus 26-EMA
- **Signal line:** 9-EMA of MACD line
- **Histogram:** MACD line minus signal line

**Potential use:** Generate signals when MACD crosses signal line.

---

### Moving Average (MA)

**Definition:** Average price over a specific number of periods, smoothing out price fluctuations.

**Types:**

- **Simple Moving Average (SMA):** All prices weighted equally
- **Exponential Moving Average (EMA):** Recent prices weighted more

**Our choice:** EMA (more responsive to recent price changes).

**See also:** EMA, SMA

---

### Overbought

**Definition:** A condition where an asset's price has risen too quickly and may be due for a pullback.

**RSI indicator:** RSI > 70 suggests overbought.

**Our signal:** In ranging markets, RSI > 70 triggers potential SELL signal (mean reversion).

**Caution:** In strong trending markets, assets can stay overbought for extended periods.

**See also:** RSI, Oversold, Mean Reversion

---

### Oversold

**Definition:** A condition where an asset's price has fallen too quickly and may be due for a bounce.

**RSI indicator:** RSI < 30 suggests oversold.

**Our signal:** In ranging markets, RSI < 30 triggers BUY signal (mean reversion).

**Caution:** In strong downtrends, assets can stay oversold for extended periods (don't "catch a falling knife").

**See also:** RSI, Overbought, Mean Reversion

---

### RSI (Relative Strength Index)

**Definition:** Momentum oscillator measuring speed and magnitude of price changes.

**Range:** 0-100

**Formula:**

```text
RSI = 100 - (100 / (1 + RS))
where RS = Average Gain / Average Loss over period (typically 14)
```

**Interpretation:**

- **RSI < 30:** Oversold (potential buy in ranging markets)
- **RSI > 70:** Overbought (potential sell in ranging markets)
- **30 ≤ RSI ≤ 70:** Neutral

**When it works:** Ranging markets (ADX < 20). Unreliable in strong trends (can stay overbought/oversold).

**Our implementation:** 14-period RSI calculated on 15-minute bars.

**See also:** Oversold, Overbought, Mean Reversion

---

## Market Regime Terms

### Ranging Market

**Definition:** A market condition where price oscillates between support and resistance levels without a clear trend.

**Detection:** ADX < 20

**Characteristics:**

- Price bounces between levels
- No sustained directional movement
- High probability of mean reversion

**Best strategies:** RSI mean-reversion signals (buy oversold, sell overbought).

**Avoid:** Trend-following strategies (EMA crossovers generate false breakouts).

**Example:** BTC trading between $42K and $43K for 3 days.

**See also:** Regime Detection, Trending Market, Mean Reversion

---

### Regime

**Definition:** The current market context or phase (trending, ranging, or uncertain).

**Types:**

1. **Trending:** Strong directional movement (ADX > 25)
2. **Ranging:** Sideways movement (ADX < 20)
3. **Uncertain:** Transition phase (20 ≤ ADX ≤ 25)

**Importance:** Determines which signal rules to apply. EMA works in trends, RSI works in ranges.

**Our implementation:**

```python
if adx > 25:
    regime = "trend"
elif adx < 20:
    regime = "range"
else:
    regime = "uncertain"  # No signals
```

**Database:** Stored in `indicators` table and `signals` table.

**See also:** Regime Detection, ADX, Trending Market, Ranging Market

---

### Regime Detection

**Definition:** The process of classifying the current market condition (trend, range, or uncertain).

**Method:** ADX-based classification

- ADX > 25 → Trending
- ADX < 20 → Ranging
- 20 ≤ ADX ≤ 25 → Uncertain

**Purpose:** Prevent signals that work in one regime but fail in another (e.g., don't signal EMA crossover in ranging market).

**Implementation:** Run ADX calculation on every 15-minute bar, store regime in `indicators` table.

**Future alternatives:** Volatility-based (ATR), price action patterns, machine learning.

**See also:** Regime, ADX, Context-Aware Signals

---

### Trending Market

**Definition:** A market condition where price moves consistently in one direction (up or down).

**Detection:** ADX > 25

**Characteristics:**

- Sustained directional movement
- Higher highs (uptrend) or lower lows (downtrend)
- Momentum-based strategies work well

**Best strategies:** EMA crossover signals (golden cross = buy, death cross = sell).

**Avoid:** Mean-reversion strategies (RSI signals fail in strong trends).

**Example:** BTC rising from $40K to $50K over 2 weeks with consistent higher highs.

**See also:** Regime Detection, Ranging Market, Momentum

---

### Uncertain Regime

**Definition:** A transition phase where the market is neither clearly trending nor ranging.

**Detection:** 20 ≤ ADX ≤ 25

**Characteristics:**

- Ambiguous price action
- Could break into trend or continue ranging
- Low confidence for any signal type

**Our approach:** **No signals** generated during uncertain regimes. System returns HOLD.

**Rationale:** Avoid false signals during transition periods. Better to miss an opportunity than generate bad signals.

**User communication:** "Market regime is uncertain. Sitting out this period."

**See also:** Regime Detection, HOLD Signal

---

## Signal Terms

### Alert Fatigue

**Definition:** When users receive too many notifications and start ignoring them.

**Causes:**

- Too many signals (>5 per day per asset)
- Low-quality signals (many losers)
- Signals during choppy markets

**Prevention:**

- Strength threshold (only send signals with strength ≥ 70)
- Cooldown period (max 1 signal per 8 hours per asset)
- Regime filtering (no signals during uncertain periods)

**Metrics:** Track unsubscribe rate within 24h of signal (target: <5%).

**See also:** Cooldown, Strength, Fatigue Rate

---

### BUY Signal

**Definition:** A recommendation to enter a long position (bet that price will go up).

**Generation rules:**

1. **Ranging market (ADX < 20):**
   - RSI < 30 (oversold) → BUY
2. **Trending market (ADX > 25):**
   - EMA-12 crosses above EMA-26 (golden cross) → BUY

**Requirements:**

- Cooldown period passed (8 hours)
- Strength ≥ 70 (for email notification)
- Data quality = 'valid'

**User communication:** Plain English explanation of why signal triggered, what it means, and risks to consider.

**See also:** Signal, SELL Signal, HOLD Signal

---

### Confidence Score

**Definition:** See **Strength**.

---

### Context-Aware Signals

**Definition:** Signals that adapt based on market regime (trending vs ranging vs uncertain).

**Traditional approach:** Apply same rules in all market conditions (generates many false signals).

**Our approach:**

- Use EMA crossovers only in trends
- Use RSI mean-reversion only in ranges
- Generate no signals during uncertain periods

**Benefit:** Higher quality signals, less spam, better user trust.

**Implementation:** Check regime field in `indicators` table before applying signal rules.

**See also:** Regime Detection, Regime

---

### False Signal

**Definition:** A signal that triggers but price moves in the opposite direction.

**Causes:**

- Wrong regime classification
- Sudden news event
- Low liquidity (price spike)
- Overfitting to historical data

**Mitigation:**

- Quality gates (reject bad data)
- Regime detection (avoid signals in wrong context)
- Risk warnings in every email
- No guarantees or promises

**Acceptance:** Some false signals are inevitable. Goal is to maximize signal quality, not eliminate all losses.

**See also:** Quality Gates, Data Quality

---

### HOLD Signal

**Definition:** A recommendation to take no action (neither buy nor sell).

**When generated:**

- Regime is uncertain (20 ≤ ADX ≤ 25)
- Indicators are neutral (30 ≤ RSI ≤ 70, no EMA crossover)
- Cooldown period active
- Data quality is not 'valid'

**Purpose:** Give users permission to sit out ambiguous periods. Not every moment requires action.

**User communication:** "Market conditions are unclear. Best to wait for a better setup."

**See also:** Signal, BUY Signal, SELL Signal, Uncertain Regime

---

### Idempotency

**Definition:** The property that an operation can be applied multiple times without changing the result beyond the initial application.

**In our system:** Prevents duplicate signals if a Prefect flow reruns due to error or retry.

**Implementation:** Idempotency key format:

```text
{asset_id}:{rule_version}:{signaled_at_timestamp}
```

**Example:**

```text
BTC-USD:rsi_v1:2025-01-20T10:15:00Z
```

**Database:** Unique constraint on `idempotency_key` column in `signals` table.

**Code:**

```sql
INSERT INTO signals (..., idempotency_key)
VALUES (..., :idempotency_key)
ON CONFLICT (idempotency_key) DO NOTHING
```

**See also:** Duplicate Prevention, Deduplication

---

### Mean Reversion

**Definition:** A trading strategy based on the assumption that price will return to its average (mean) after extreme moves.

**Logic:** "What goes up must come down, what goes down must come up" (in ranging markets).

**When it works:** Ranging markets (ADX < 20) where price oscillates between support and resistance.

**When it fails:** Trending markets (price can trend far from mean without reverting).

**Our implementation:** RSI < 30 (oversold) in ranging market → expect price to bounce back up.

**See also:** RSI, Ranging Market, Oversold, Overbought

---

### Momentum

**Definition:** The rate of price change, indicating how fast price is moving in a direction.

**High momentum:** Large price moves in short time (trending market).

**Low momentum:** Small price moves, sideways action (ranging market).

**Indicators:** EMA (trend direction), ADX (trend strength).

**Our signals:** EMA crossovers work best in high-momentum trending markets.

**See also:** Trending Market, EMA, ADX

---

### Notification

**Definition:** An email sent to subscribers when a strong signal (strength ≥ 70) is generated.

**Content:**

- Signal type (BUY/SELL)
- Asset name and current price
- Strength score (0-100)
- Plain English reasoning (why signal triggered)
- Risk warnings
- Link to dashboard for full details

**Delivery:** Via Resend API with DKIM/SPF/DMARC authentication.

**Tracking:** Stored in `notifications` table with `sent_at` timestamp and `email_provider_id`.

**See also:** Email, Resend, Subscriber

---

### Regime-Based Rules

**Definition:** Signal generation logic that changes based on the current market regime.

**Example:**

```python
if regime == "trend":
    # Use momentum strategies
    if ema_12 > ema_26 and ema_12_prev <= ema_26_prev:
        signal = "BUY"
elif regime == "range":
    # Use mean-reversion strategies
    if rsi < 30:
        signal = "BUY"
else:  # uncertain
    signal = "HOLD"
```

**Benefit:** Prevents signals that work in one regime but fail in another.

**See also:** Regime Detection, Context-Aware Signals

---

### SELL Signal

**Definition:** A recommendation to exit a long position or enter a short position (bet that price will go down).

**Generation rules:**

1. **Ranging market (ADX < 20):**
   - RSI > 70 (overbought) → SELL
2. **Trending market (ADX > 25):**
   - EMA-12 crosses below EMA-26 (death cross) → SELL

**MVP Note:** SELL signals are generated but not emphasized (most users are long-only).

**Future:** May add SHORT signals for advanced users or inverse ETFs.

**See also:** Signal, BUY Signal, Death Cross

---

### Signal

**Definition:** A recommendation to take a trading action (BUY, SELL, or HOLD) based on technical indicators and market regime.

**Components:**

- **Type:** BUY, SELL, or HOLD
- **Asset:** BTC-USD, ETH-USD
- **Strength:** Confidence score (0-100)
- **Regime:** Trend, range, or uncertain
- **Reasoning:** Plain English explanation
- **Timestamp:** When signal was generated
- **Price:** Asset price at signal time

**Lifecycle:**

1. Generated by Flow 4 (Signal Generation)
2. Stored in `signals` table
3. If strength ≥ 70, sent to subscribers via email
4. Displayed on dashboard for all users
5. Tracked in PostHog for performance analysis

**Database:** Stored in `signals` table with idempotency key.

**See also:** BUY Signal, SELL Signal, HOLD Signal, Strength

---

### Signal Strength

**Definition:** See **Strength**.

---

### Strength

**Definition:** A confidence score (0-100) indicating how strongly the signal is supported by indicators and context.

**Calculation:** Weighted average of:

- Indicator extremity (how far RSI from 30/70, how wide EMA separation)
- Regime alignment (ADX strength)
- Volume confirmation (higher volume = stronger signal)
- Price action context (bouncing off support/resistance)

**Thresholds:**

- **Strength ≥ 80:** Very strong (rare, ~5% of signals)
- **Strength ≥ 70:** Strong (email notification sent)
- **Strength < 70:** Weak (displayed on dashboard only, no email)

**Example calculation:**

```python
def calculate_strength(indicators, signal_type, regime):
    score = 50  # Start at neutral

    # RSI extremity (0-30 points)
    if signal_type == "BUY" and indicators["rsi"] < 30:
        score += (30 - indicators["rsi"])  # Lower RSI = stronger buy

    # Regime alignment (0-20 points)
    if regime == "range" and indicators["adx"] < 20:
        score += (20 - indicators["adx"])
    elif regime == "trend" and indicators["adx"] > 25:
        score += min(indicators["adx"] - 25, 20)

    # Cap at 100
    return min(score, 100)
```

**User communication:** Displayed prominently in email and dashboard (e.g., "82/100").

**See also:** Signal, Confidence Score, Threshold

---

### Threshold

**Definition:** A cutoff value that determines whether a signal is acted upon.

**Our thresholds:**

- **Email notification:** Strength ≥ 70
- **RSI oversold:** RSI < 30
- **RSI overbought:** RSI > 70
- **Trending regime:** ADX > 25
- **Ranging regime:** ADX < 20

**Calibration:** Determined via micro-backtest on 90 days of historical data.

**Adjustable:** Can be tuned per asset if needed (e.g., BTC may have different threshold than ETH).

**See also:** Strength, Calibration

---

## Data Terms

### Bar Count

**Definition:** Number of smaller bars combined to create a larger bar.

**Our implementation:** 15-minute bars are created from 3x 5-minute bars (bar_count = 3).

**Quality check:** Only store 15-min bars with `bar_count = 3` (reject incomplete bars).

**Database:** `bar_count` field in `ohlcv_15m` table.

**See also:** Resampling, OHLCV

---

### Calibration

**Definition:** Tuning system parameters (thresholds, cooldown periods) based on historical data.

**Our approach (Micro-Backtest):**

1. Run signal rules on last 90 days of data
2. Measure win rate (signals where price moved in predicted direction)
3. Determine optimal cooldown period (6h vs 8h vs 12h)
4. Set strength threshold to achieve target email volume

**Goal:** Reasonable parameters, not PnL theatrics.

**Not backtesting:** We don't calculate hypothetical returns or publish performance claims.

**See also:** Backtesting, Micro-Backtest, Threshold

---

### Data Quality

**Definition:** An assessment of whether OHLCV data is trustworthy for analysis.

**Quality flags:**

- **'valid':** Passed all quality gates
- **'gap':** Missing prior bar (data gap)
- **'stale':** Data is >10 minutes old
- **'spike':** Price jump >5% from prior bar (fat-finger error)

**Usage:** Only use bars with `data_quality = 'valid'` for resampling and indicator calculation.

**Database:** `data_quality` field in `ohlcv` table.

**See also:** Quality Gates, Gap Check, Staleness Check, Spike Check

---

### Fat-Finger Error

**Definition:** A data error caused by a typo or system glitch, resulting in an impossible price.

**Example:** BTC price jumps from $42,000 to $420,000 in one 5-minute bar (typo: extra zero).

**Detection:** Spike check (price change >5% from prior bar).

**Mitigation:** Flag bar with `data_quality = 'spike'`, exclude from analysis.

**See also:** Spike Check, Data Quality, Quality Gates

---

### Gap

**Definition:** A missing bar in the OHLCV time series.

**Causes:**

- Yahoo Finance API failure
- Network timeout
- Exchange downtime (rare for crypto)

**Detection:** Gap check (compare current bar timestamp to prior bar timestamp, expect 5-minute difference).

**Mitigation:** Flag bar with `data_quality = 'gap'`, attempt backfill, exclude from analysis.

**See also:** Gap Check, Data Quality, Quality Gates

---

### Gap Check

**Definition:** A quality gate that detects missing bars in the OHLCV time series.

**Implementation:**

```python
prior_timestamp = get_prior_timestamp(asset_id)
expected_timestamp = prior_timestamp + timedelta(minutes=5)

if current_timestamp != expected_timestamp:
    quality = "gap"
```

**Outcome:** Bar flagged with `data_quality = 'gap'`.

**See also:** Quality Gates, Gap, Data Quality

---

### OHLCV

**Definition:** Open, High, Low, Close, Volume - the five data points that make up a price bar.

**Components:**

- **Open:** First price in the period
- **High:** Highest price in the period
- **Low:** Lowest price in the period
- **Close:** Last price in the period
- **Volume:** Number of units traded in the period

**Example:**

```json
{
  "timestamp": "2025-01-20T10:15:00Z",
  "open": 42350.00,
  "high": 42450.00,
  "low": 42320.00,
  "close": 42410.00,
  "volume": 1234567
}
```

**Database:** Stored in `ohlcv` (5-min) and `ohlcv_15m` (15-min) tables.

**See also:** Bar, Candlestick, Timeframe

---

### Quality Gates

**Definition:** A series of checks that validate OHLCV data before using it for analysis.

**MVP Gates:**

1. **Gap check:** Is there a missing prior bar?
2. **Staleness check:** Is data <10 minutes old?
3. **Spike check:** Did price jump >5% from prior bar?

**Implementation:** Run in Flow 1 (Market Data Ingestion) before storing in database.

**Outcome:** Bar tagged with `data_quality` field ('valid', 'gap', 'stale', 'spike').

**Rationale:** Bad data → bad signals → lost user trust.

**See also:** Data Quality, Gap Check, Staleness Check, Spike Check

---

### Resampling

**Definition:** Combining multiple smaller bars into a larger bar.

**Our implementation:** 3x 5-minute bars → 1x 15-minute bar

**Rules:**

- `open` = first bar's open
- `high` = max of 3 highs
- `low` = min of 3 lows
- `close` = last bar's close
- `volume` = sum of 3 volumes

**Flow:** Flow 2 (OHLCV Resampling) runs every 15 minutes on the hour (0, 15, 30, 45).

**Database:** Result stored in `ohlcv_15m` table.

**See also:** Bar, OHLCV, Timeframe

---

### Spike Check

**Definition:** A quality gate that detects abnormally large price jumps (>5%) that may indicate fat-finger errors.

**Implementation:**

```python
prior_close = get_prior_close(asset_id)
price_change_pct = abs((current_close - prior_close) / prior_close * 100)

if price_change_pct > 5:
    quality = "spike"
```

**Rationale:** While crypto is volatile, >5% moves in 5 minutes are rare and often indicate bad data.

**Outcome:** Bar flagged with `data_quality = 'spike'`.

**Tuning:** Threshold may be adjusted per asset (ETH may be more volatile than BTC).

**See also:** Quality Gates, Fat-Finger Error, Data Quality

---

### Staleness Check

**Definition:** A quality gate that rejects data that is too old to be useful.

**Threshold:** Data must be <10 minutes old.

**Implementation:**

```python
data_age_minutes = (datetime.now(UTC) - bar_timestamp).seconds / 60

if data_age_minutes > 10:
    quality = "stale"
```

**Rationale:** Crypto markets move fast. Data older than 10 minutes is not actionable for 15-minute signals.

**Outcome:** Bar flagged with `data_quality = 'stale'`.

**See also:** Quality Gates, Data Quality

---

### Symbol

**Definition:** A unique identifier for a tradable asset (e.g., "BTC-USD" for Bitcoin priced in US dollars).

**Format:** `{base}-{quote}` (e.g., BTC-USD, ETH-USD)

**MVP Symbols:** BTC-USD, ETH-USD

**See also:** Asset, Ticker

---

### Ticker

**Definition:** See **Symbol**.

---

### Timeframe

**Definition:** The duration of time represented by a single bar (e.g., 5 minutes, 15 minutes, 1 hour).

**MVP Timeframes:**

- **5 minutes:** Raw data from Yahoo Finance (stored in `ohlcv` table)
- **15 minutes:** Resampled from 3x 5-min bars (stored in `ohlcv_15m` table)

**Future:** May add 1-hour or 4-hour timeframes for swing traders.

**See also:** Bar, OHLCV, Resampling

---

## System Terms

### API (Application Programming Interface)

**Definition:** A set of endpoints that allow external systems to interact with our backend.

**Our APIs:**

- **Yahoo Finance API:** Fetch OHLCV data
- **Resend API:** Send emails
- **PostHog API:** Track events
- **FastAPI:** Our backend API (endpoints like /api/signals, /api/subscribe)

**See also:** FastAPI, Endpoint, REST

---

### Cooldown Enforcement

**Definition:** The mechanism that prevents signals from being generated too frequently.

**Implementation:** Query `signals` table before generating new signal:

```sql
SELECT EXISTS (
    SELECT 1 FROM signals
    WHERE asset_id = :asset_id
      AND rule_version = :rule_version
      AND signaled_at > NOW() - INTERVAL '8 hours'
) AS cooldown_active
```

**If cooldown active:** Skip signal generation for this asset and rule.

**See also:** Cooldown, Spam Prevention

---

### DAG (Directed Acyclic Graph)

**Definition:** A workflow structure where tasks have dependencies (A must complete before B starts).

**In Prefect:** Flows contain tasks with dependencies (e.g., "fetch data" → "validate data" → "store data").

**Not explicitly needed:** Prefect 2.x uses decorators (@task, @flow) instead of DAG files (unlike Airflow).

**See also:** Prefect, Flow, Task

---

### Deduplication

**Definition:** See **Idempotency**.

---

### Double Opt-In

**Definition:** A two-step email subscription process where users must confirm their subscription via email.

**Steps:**

1. User enters email on landing page
2. System sends confirmation email with unique token
3. User clicks "Confirm Subscription" link
4. System marks subscription as confirmed
5. User receives welcome email

**Benefits:**

- Prevents spam signups (bots, typos)
- Improves deliverability (ISPs favor confirmed lists)
- GDPR compliance (explicit consent)

**Database:** `email_subscribers.confirmed` field (boolean), `confirmation_token` (unique).

**See also:** Email Subscriber, Resend, Deliverability

---

### Email Subscriber

**Definition:** A user who has signed up to receive email notifications for strong signals.

**Requirements:**

- Valid email address
- Confirmed subscription (double opt-in)
- Not unsubscribed

**Database:** Stored in `email_subscribers` table with fields: `email`, `confirmed`, `confirmation_token`, `unsubscribe_token`.

**See also:** Double Opt-In, Notification, Unsubscribe

---

### Endpoint

**Definition:** A specific URL path in an API that performs a function.

**Our endpoints:**

- `GET /api/signals` - Fetch all signals
- `GET /api/signals/{signal_id}` - Fetch single signal
- `GET /api/market-data/{asset_id}` - Fetch OHLCV data
- `POST /api/subscribe` - Subscribe to emails
- `GET /api/confirm` - Confirm email subscription
- `GET /api/unsubscribe` - Unsubscribe from emails
- `GET /api/health` - System health check

**See also:** API, FastAPI, REST

---

### ETL (Extract, Transform, Load)

**Definition:** A data pipeline pattern for moving data from source to destination.

**Our implementation:**

- **Extract:** Fetch from Yahoo Finance API (Flow 1)
- **Transform:** Resample, calculate indicators (Flows 2, 3)
- **Load:** Store in PostgreSQL (all flows)

**See also:** Data Pipeline, Prefect, Flow

---

### FastAPI

**Definition:** A modern Python web framework for building APIs.

**Why we use it:**

- Auto-generated OpenAPI docs
- Pydantic validation (type-safe)
- Async support (handles concurrent requests)
- Fast development velocity

**Our usage:** Backend API with endpoints for signals, market data, subscriptions.

**See also:** API, Endpoint, Pydantic

---

### Flow

**Definition:** In Prefect, a flow is a container for tasks that defines a workflow.

**Our flows:**

1. **Market Data Ingestion** - Fetch OHLCV from Yahoo Finance
2. **OHLCV Resampling** - Convert 5-min bars to 15-min bars
3. **Indicator Calculation** - Calculate RSI, EMA, ADX
4. **Signal Generation** - Apply regime-based rules
5. **Notification Sender** - Send emails for strong signals

**Scheduling:** Each flow runs on a cron schedule (e.g., every 5 minutes, every 15 minutes).

**See also:** Prefect, Task, DAG

---

### Global Kill Switch

**Definition:** A manual override that disables signal generation system-wide.

**Triggers:**

- Data is stale (>10 minutes old)
- Prefect flows fail twice in a row
- Email deliverability drops below 90%
- Manual trigger by ops team

**Implementation:** Environment variable `SIGNALS_ENABLED=false` checked before signal generation.

**Purpose:** Prevent bad signals during system issues.

**See also:** Safety Mechanisms, Ops

---

### Idempotency Key

**Definition:** A unique string that identifies a signal, used to prevent duplicates.

**Format:** `{asset_id}:{rule_version}:{signaled_at_timestamp}`

**Example:** `BTC-USD:rsi_v1:2025-01-20T10:15:00Z`

**Database:** Unique constraint on `signals.idempotency_key` column.

**See also:** Idempotency, Deduplication

---

### Micro-Backtest

**Definition:** A limited form of backtesting focused on parameter tuning, not performance claims.

**Our approach:**

1. Run signal rules on last 90 days of data per asset
2. Measure win rate (% of signals where price moved in predicted direction)
3. Determine optimal cooldown period (6h vs 8h vs 12h)
4. Set strength threshold to achieve target email volume (3 signals per day max)

**Output:** Threshold values and win rate (for internal use, not marketing).

**Not used for:** PnL claims, performance marketing, backtested returns.

**See also:** Calibration, Backtesting

---

### Notification Record

**Definition:** A database entry tracking that an email was sent for a specific signal to a specific subscriber.

**Database:** `notifications` table with fields:

- `signal_id` - Which signal was sent
- `subscriber_id` - Who received it
- `sent_at` - When it was sent
- `email_provider_id` - Resend message ID (for tracking)

**Purpose:**

- Prevent duplicate sends
- Track deliverability
- Measure engagement (open rate, click rate)

**See also:** Notification, Email Subscriber

---

### Ops (Operations)

**Definition:** The practice of monitoring, maintaining, and troubleshooting a production system.

**Our ops tasks:**

- Monitor Prefect flow runs (check for failures)
- Monitor email deliverability (check bounce rate)
- Monitor data freshness (check for stale data)
- Respond to alerts (Slack notifications)
- Manual interventions (global kill switch, reprocess bad data)

**Tools:** Prefect Cloud dashboard, PostHog analytics, Vercel logs, Neon database metrics.

**See also:** Global Kill Switch, Runbook, Alerts

---

### Orchestration

**Definition:** Managing and scheduling a sequence of data pipeline tasks.

**Our tool:** Prefect 2.x

**Why:** Built-in scheduling, retries, logging, observability.

**Alternative:** Apache Airflow (more complex, requires self-hosting).

**See also:** Prefect, Flow, Task, DAG

---

### PostHog

**Definition:** An open-source analytics platform for tracking user behavior and system events.

**Our usage:**

- **User events:** page_viewed, email_subscribed, signal_clicked, unsubscribed
- **System events:** signal_generated, email_sent, email_opened, data_quality_issue

**Dashboards:**

- User funnel (visit → subscribe → engage)
- Signal performance (generated → sent → opened → clicked)
- Data health (valid bars % over time)

**Deployment:** PostHog Cloud (free tier, no self-hosting).

**See also:** Analytics, Events, Metrics

---

### Prefect

**Definition:** A Python-based workflow orchestration platform for data pipelines.

**Our usage:** Schedule and run 5 flows (ingestion, resampling, indicators, signals, notifications).

**Key features:**

- Decorators (@flow, @task) for defining workflows
- Built-in scheduling (cron syntax)
- Retries and error handling
- Observability (logs, metrics, flow run history)

**Deployment:** Prefect Cloud (free tier, no self-hosting).

**Alternative:** Apache Airflow (more complex).

**See also:** Orchestration, Flow, Task

---

### Pydantic

**Definition:** A Python library for data validation using type annotations.

**Our usage:** FastAPI request/response schemas (e.g., `SignalResponse`, `SubscribeRequest`).

**Benefits:**

- Automatic validation (reject invalid input)
- Auto-generated OpenAPI docs
- Type safety (catch bugs before runtime)

**Example:**

```python
class SubscribeRequest(BaseModel):
    email: EmailStr  # Validates email format
```

**See also:** FastAPI, Type Safety

---

### Resend

**Definition:** A developer-focused email API for transactional emails.

**Our usage:** Send signal notifications and subscription confirmation emails.

**Benefits:**

- High deliverability (built-in DKIM/SPF/DMARC)
- Simple API (10 lines of code)
- Generous free tier (3K emails/month)
- Webhooks for open/bounce tracking

**Configuration:** Domain authentication (DKIM/SPF/DMARC DNS records).

**Alternative:** SendGrid (more complex, legacy API).

**See also:** Email, Notification, Deliverability

---

### REST (Representational State Transfer)

**Definition:** An architectural style for building APIs using HTTP methods (GET, POST, etc.).

**Our API endpoints:**

- `GET /api/signals` - Retrieve signals
- `POST /api/subscribe` - Create subscription
- `GET /api/health` - Check system status

**Principles:**

- Stateless (each request is independent)
- Resource-based URLs (/signals, /market-data)
- Standard HTTP methods (GET, POST, DELETE)

**See also:** API, FastAPI, Endpoint

---

### Runbook

**Definition:** A documented set of procedures for handling common operational tasks and issues.

**Our runbook items:**

1. **Reprocess a bad bar:** Delete from `ohlcv`, re-run Flow 1
2. **Resend failed notifications:** Update `signals.notified_at = NULL`, re-run Flow 5
3. **Manually disable a rule:** Set environment variable `RSI_RULE_ENABLED=false`
4. **Global kill switch:** Set `SIGNALS_ENABLED=false`
5. **Backfill historical data:** Run `scripts/seed_historical_data.py`

**Purpose:** Enable quick responses to issues without guesswork.

**See also:** Ops, Global Kill Switch

---

### Safety Mechanisms

**Definition:** Systems and checks in place to prevent bad signals or system failures from harming users.

**Our mechanisms:**

1. **Quality gates:** Reject bad data
2. **Regime detection:** Avoid signals in wrong context
3. **Cooldowns:** Prevent spam
4. **Idempotency:** Prevent duplicates
5. **Global kill switch:** Disable signals during issues
6. **Strength threshold:** Only send high-confidence signals
7. **Risk warnings:** Every email and page

**See also:** Quality Gates, Global Kill Switch, Risk Disclosure

---

### SQLAlchemy

**Definition:** A Python SQL toolkit and Object-Relational Mapping (ORM) library.

**Our usage:** Database access in FastAPI and Prefect (models, queries).

**Benefits:**

- Type-safe queries (catch SQL errors at dev time)
- ORM models (Python classes ↔ database tables)
- Migration support (via Alembic)

**Alternative:** Raw SQL (more verbose, error-prone).

**See also:** PostgreSQL, Database, ORM

---

### Task

**Definition:** In Prefect, a task is a unit of work within a flow (e.g., "fetch data", "validate data").

**Characteristics:**

- Defined with `@task` decorator
- Can retry on failure
- Can run concurrently (if independent)
- Outputs logged for observability

**Example:**

```python
@task(name="fetch-ohlcv")
def fetch_ohlcv(asset_id: str) -> pd.DataFrame:
    # Fetch data from Yahoo Finance
    pass
```

**See also:** Flow, Prefect, DAG

---

### Type Safety

**Definition:** Using type annotations to catch errors at development time instead of runtime.

**Our usage:**

- TypeScript in frontend (Next.js)
- Python type hints in backend (FastAPI, Prefect)
- Pydantic validation (FastAPI request/response)

**Benefits:**

- Catch bugs before production
- Better IDE autocomplete
- Easier refactoring

**Example:**

```python
def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    # Type hints: df is DataFrame, period is int, returns Series
    pass
```

**See also:** Pydantic, TypeScript

---

### Unsubscribe

**Definition:** The action of opting out of email notifications.

**Implementation:** One-click link in every email footer:

```html
<a href="https://yourdomain.com/unsubscribe?token={unsubscribe_token}">Unsubscribe</a>
```

**Process:**

1. User clicks unsubscribe link
2. Backend deletes record from `email_subscribers` table
3. User sees "You've been unsubscribed" page
4. Event tracked in PostHog

**GDPR compliance:** Immediate deletion (right to be forgotten).

**See also:** Email Subscriber, Double Opt-In

---

### Webhook

**Definition:** A callback URL that receives HTTP POST requests when an event occurs.

**Our usage:** Resend sends webhooks for email opens, bounces, complaints.

**Endpoint:** `POST /api/webhooks/resend`

**Payload example:**

```json
{
  "type": "email.opened",
  "email_id": "abc123",
  "recipient": "user@example.com",
  "timestamp": "2025-01-20T10:15:00Z"
}
```

**Purpose:** Track email deliverability and engagement without polling.

**See also:** Resend, Notification, Event

---

## User Experience Terms

### Activation Rate

**Definition:** Percentage of email subscribers who click through to view a signal within 7 days of subscribing.

**Formula:** `(Subscribers who clicked ≥1 signal within 7 days) / (Total confirmed subscribers) × 100`

**Target:** >20%

**Interpretation:** Measures whether users care about signals after signing up.

**Tracked in:** PostHog event funnel (email_confirmed → signal_clicked).

**See also:** Engagement, Metrics

---

### Dashboard

**Definition:** A web page displaying all recent signals with filters and charts.

**URL:** /dashboard

**Content:**

- Signal cards (BTC-USD, ETH-USD)
- Filters (asset, signal type, timeframe)
- Performance metrics (win rate, avg excursion)
- Educational sidebar

**Access:** Public (no login required for MVP).

**See also:** Frontend, Landing Page

---

### Deliverability

**Definition:** The percentage of emails that successfully reach recipients' inboxes (not spam folder).

**Factors:**

- **Email authentication:** DKIM, SPF, DMARC configured
- **List quality:** Double opt-in (no spam signups)
- **Content:** Avoid spam trigger words
- **Engagement:** High open rates signal to ISPs that emails are wanted

**Target:** >90% delivered, >25% opened.

**Monitoring:** Resend dashboard, PostHog events.

**See also:** Resend, Double Opt-In, Email

---

### Engagement

**Definition:** Metric measuring how often users interact with signals.

**Measurement:** Clicks per active user per week.

**Target:** 2+ clicks per week.

**Interpretation:** Do users return regularly? Are signals compelling?

**Tracked in:** PostHog event (signal_clicked).

**See also:** Activation Rate, Metrics

---

### Fatigue Rate

**Definition:** Percentage of users who unsubscribe within 24 hours of receiving a signal.

**Formula:** `(Unsubscribes within 24h of signal) / (Signals sent) × 100`

**Target:** <5%

**Interpretation:** Are we spamming users? Are signals too frequent or low quality?

**Mitigation:** Cooldowns, strength thresholds, regime filtering.

**See also:** Alert Fatigue, Cooldown, Unsubscribe

---

### Landing Page

**Definition:** The main entry point to the website (homepage).

**URL:** /

**Content:**

- Hero section (value proposition)
- Live signals (BTC, ETH with strength scores)
- How it works (explainer)
- Email signup form
- FAQ
- Risk disclaimer

**Goal:** Convert visitors to email subscribers (target: 20% conversion rate).

**See also:** Dashboard, Frontend

---

### Metrics

**Definition:** Quantitative measurements used to evaluate system performance and user behavior.

**Core metrics:**

1. **Activation Rate:** % of subscribers who click a signal within 7 days (target: >20%)
2. **Engagement:** Clicks per active user per week (target: 2+)
3. **Fatigue Rate:** Unsubscribes within 24h of signal (target: <5%)
4. **Data Health:** % of jobs on time with valid bars (target: >95%)

**Secondary metrics:**

- Email open rate (target: >25%)
- Signal click-through rate (target: >15%)
- Win rate (% of signals where price moved predicted direction)

**Tracked in:** PostHog dashboards.

**See also:** Activation Rate, Engagement, Fatigue Rate, Data Health

---

### Plain English

**Definition:** Explaining technical concepts without jargon, as if talking to a non-expert.

**Bad:** "EMA-12 crossed above EMA-26 in a regime where ADX > 25, indicating positive momentum alpha."

**Good:** "The fast-moving average crossed above the slow one, and the trend is strong. This suggests upward momentum."

**Our approach:** Every signal includes:

- What happened (RSI dropped to 28)
- What it means (Price is oversold, likely to bounce)
- Risk context (Watch for breaking news)

**See also:** User Experience, Educational Content

---

### Risk Disclosure

**Definition:** A legal and ethical disclaimer that our signals are educational, not financial advice.

**Placement:** Every page footer, every email footer.

**Content:**

```text
⚠️ Not financial advice. Signals are algorithmic and may be wrong.
Past performance does not guarantee future results.
Trade at your own risk. We are not licensed financial advisors.
```

**Purpose:**

- Legal protection
- Set user expectations
- Build trust through transparency

**See also:** Legal, Safety Mechanisms

---

### Win Rate

**Definition:** Percentage of signals where price moved in the predicted direction within a specific timeframe.

**Example:** If BUY signal is generated and price is higher 4 hours later, it's a "win."

**Not used for:** Marketing claims, performance advertising.

**Used for:** Internal calibration, parameter tuning.

**Target:** >55% (better than random).

**Caveat:** Win rate ≠ profitability (need to consider position sizing, risk/reward ratio, fees).

**See also:** Calibration, Micro-Backtest

---

## Phase 2 Terms (Out of Scope for MVP)

### Telegram Bot

**Definition:** A messaging bot on Telegram for delivering signal notifications.

**Status:** Phase 2 (email only for MVP).

**Why postponed:** Focus on perfecting one channel (email) first.

---

### User Authentication

**Definition:** System for creating accounts, logging in, and managing user preferences.

**Status:** Phase 2 (no login required for MVP).

**Why postponed:** Public dashboard + email subscriptions are sufficient for MVP.

---

### Portfolio Tracking

**Definition:** Tracking user's asset holdings and PnL.

**Status:** Phase 2.

**Why postponed:** Adds complexity, requires user authentication.

---

### Payment System

**Definition:** Accepting payment for premium features (more assets, advanced signals).

**Status:** Phase 2 (free tier for MVP).

**Why postponed:** Validate product-market fit before monetizing.

---

## Acronyms Quick Reference

- **ADX:** Average Directional Index
- **API:** Application Programming Interface
- **ATR:** Average True Range
- **DAG:** Directed Acyclic Graph
- **EMA:** Exponential Moving Average
- **ETL:** Extract, Transform, Load
- **MACD:** Moving Average Convergence Divergence
- **OHLCV:** Open, High, Low, Close, Volume
- **ORM:** Object-Relational Mapping
- **REST:** Representational State Transfer
- **RSI:** Relative Strength Index
- **SMA:** Simple Moving Average
- **SPF:** Sender Policy Framework (email authentication)
- **DKIM:** DomainKeys Identified Mail (email authentication)
- **DMARC:** Domain-based Message Authentication, Reporting & Conformance

---

**Version:** 0.1.0
**Last Updated:** January 2025
**Status:** Ready for reference

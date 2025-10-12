# Signal Generation

Complete guide to regime-based signal generation with cooldowns and idempotency.

## Core Philosophy

> **"Right signal, right context, right time."**

- Not all market conditions favor the same strategy
- Trending markets → Follow the trend (EMA crossover)
- Ranging markets → Mean reversion (RSI oversold/overbought)
- Uncertain markets → No signals (wait for clarity)

## Signal Generation Flow

```bash
1. Fetch latest indicators (RSI, EMA12, EMA26, ADX, regime)
2. Check cooldown (has this asset had a signal in last 8 hours?)
3. Check regime:
   - If "trend" → Check EMA crossover rules
   - If "range" → Check RSI mean-reversion rules
   - If "uncertain" → Skip (no signal)
4. If rule triggered:
   - Calculate signal strength (0-100)
   - Generate plain English explanation
   - Create idempotency key
   - Store signal (with conflict handling)
5. Track in PostHog
```

## Regime Detection

### ADX-Based Regime Classification

**ADX (Average Directional Index)** measures trend strength, not direction.

```python
def detect_regime(adx: float) -> str:
    """
    Classify market regime from ADX value.

    Returns:
        'trend': Strong directional movement (ADX > 25)
        'range': Sideways/choppy movement (ADX < 20)
        'uncertain': Transition phase (20 <= ADX <= 25)
    """
    if adx > 25:
        return "trend"
    elif adx < 20:
        return "range"
    else:
        return "uncertain"
```

**Why This Works:**

- High ADX = Price is moving strongly in one direction → EMA crossover works
- Low ADX = Price is bouncing between levels → RSI mean-reversion works
- Mid ADX = Market is indecisive → Don't trade

### Regime Visualization

```bash
ADX
100 ┤                  ╭─────╮
 75 ┤         ╭────────╯     ╰────╮
 50 ┤    ╭────╯                   ╰───╮
 25 ┤────╯ TREND                      ╰────
 20 ┤┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
    └────RANGE────UNCERTAIN───TREND──RANGE
    │            │         │
    RSI works    Skip      EMA works
```

## Signal Rules

### Rule 1: RSI Mean-Reversion (Ranging Markets)

**When:** `regime == "range"` AND `ADX < 20`

**BUY Signal:**

```python
if regime == "range":
    if rsi < 30:
        signal_type = "BUY"
        reasoning = [
            f"RSI oversold ({rsi:.1f})",
            "Price likely to bounce in ranging market",
            f"ADX low ({adx:.1f}) confirms sideways movement"
        ]
```

**Logic:**

- RSI < 30 = Oversold (price pushed down too far)
- In ranging market, price bounces back to mean
- Classic mean-reversion setup

**HOLD Signal:**

```python
elif rsi > 70:
    signal_type = "HOLD"
    reasoning = [
        f"RSI overbought ({rsi:.1f})",
        "Price likely to pullback in ranging market",
        "Consider taking profit if holding"
    ]
```

**No Signal:**

```python
else:  # 30 <= RSI <= 70
    # Neutral zone, no clear setup
    return None
```

### Rule 2: EMA Crossover (Trending Markets)

**When:** `regime == "trend"` AND `ADX > 25`

**BUY Signal (Bullish Crossover):**

```python
if regime == "trend":
    ema_diff = ema_12 - ema_26
    ema_diff_prev = get_previous_ema_diff(asset_id)

    # Crossover detected
    if ema_diff_prev < 0 and ema_diff > 0:
        signal_type = "BUY"
        reasoning = [
            "EMA-12 crossed above EMA-26 (golden cross)",
            f"ADX strong ({adx:.1f}) confirms trend",
            "Momentum turning bullish"
        ]
```

**Logic:**

- EMA-12 crossing above EMA-26 = Short-term momentum > long-term
- In trending market, this signals continuation
- Classic trend-following setup

**HOLD Signal (Bearish Crossover):**

```python
elif ema_diff_prev > 0 and ema_diff < 0:
    signal_type = "HOLD"
    reasoning = [
        "EMA-12 crossed below EMA-26 (death cross)",
        f"ADX strong ({adx:.1f}) confirms downtrend",
        "Consider exiting longs"
    ]
```

### Rule 3: No Signal (Uncertain Regime)

**When:** `regime == "uncertain"` OR `20 <= ADX <= 25`

```python
if regime == "uncertain":
    # Market is transitioning, unclear which strategy to use
    return None
```

**Why Skip:**

- ADX in middle range = Market deciding direction
- Neither RSI nor EMA reliable in transition
- Better to wait for clarity than force a signal

## Signal Strength Calculation

Signal strength (0-100) represents confidence in the setup.

### Strength Formula

```python
def calculate_signal_strength(
    signal_type: str,
    rsi: float,
    ema_diff: float,
    adx: float,
    regime: str
) -> int:
    """
    Calculate signal strength (0-100).

    Higher strength = More confident setup.
    Only signals with strength >= 70 trigger email notifications.
    """
    strength = 0

    if regime == "range":
        # RSI-based strength (max 50 points from RSI deviation)
        if signal_type == "BUY":
            # RSI 0 = 50 points, RSI 30 = 0 points
            strength += max(0, (30 - rsi) * 50 / 30)

        # ADX confirmation (max 30 points for low ADX)
        # ADX 0 = 30 points, ADX 20 = 0 points
        strength += max(0, (20 - adx) * 30 / 20)

        # Bonus points if RSI extremely oversold (max 20 points)
        if rsi < 20:
            strength += (20 - rsi) * 20 / 20

    elif regime == "trend":
        # EMA-based strength (max 40 points from crossover magnitude)
        # Larger crossover = stronger signal
        strength += min(40, abs(ema_diff) / 100 * 40)

        # ADX confirmation (max 30 points for high ADX)
        # ADX 25 = 0 points, ADX 50+ = 30 points
        strength += min(30, (adx - 25) * 30 / 25)

        # Momentum bonus if RSI also aligned (max 30 points)
        if signal_type == "BUY" and rsi < 50:
            strength += (50 - rsi) * 30 / 50
        elif signal_type == "HOLD" and rsi > 50:
            strength += (rsi - 50) * 30 / 50

    return min(100, int(strength))
```

### Strength Thresholds

```python
STRENGTH_LEVELS = {
    90-100: "VERY STRONG",  # Rare, perfect setup
    70-89:  "STRONG",       # Email notification threshold
    50-69:  "MODERATE",     # Show on dashboard, no email
    30-49:  "WEAK",         # Show on dashboard
    0-29:   "VERY WEAK"     # Don't display
}
```

**Example Calculations:**

**RSI Mean-Reversion (Range):**

```bash
RSI = 25, ADX = 15
- RSI deviation: (30 - 25) * 50 / 30 = 8.3 points
- ADX confirmation: (20 - 15) * 30 / 20 = 7.5 points
- Oversold bonus: (20 - 25) = 0 points (RSI not < 20)
Total: 15.8 → Not strong enough for email (< 70)

RSI = 18, ADX = 12
- RSI deviation: (30 - 18) * 50 / 30 = 20 points
- ADX confirmation: (20 - 12) * 30 / 20 = 12 points
- Oversold bonus: (20 - 18) * 20 / 20 = 2 points
Total: 34 → Still not strong enough

RSI = 15, ADX = 8
- RSI deviation: (30 - 15) * 50 / 30 = 25 points
- ADX confirmation: (20 - 8) * 30 / 20 = 18 points
- Oversold bonus: (20 - 15) * 20 / 20 = 5 points
Total: 48 → Moderate (show on dashboard)
```

**Note:** These numbers need tuning via micro-backtest (Week 3).

## Cooldown Enforcement

**Purpose:** Prevent spam during choppy markets.

**Rule:** Max 1 signal per asset per rule version per 8 hours.

### Implementation

```python
def check_cooldown(asset_id: str, rule_version: str) -> bool:
    """
    Check if cooldown period has passed.

    Returns:
        True if cooldown active (skip signal generation)
        False if cooldown expired (allow signal)
    """
    from sqlalchemy import create_engine

    engine = create_engine(os.getenv("DATABASE_URL"))

    query = """
        SELECT EXISTS (
            SELECT 1
            FROM signals
            WHERE asset_id = :asset_id
              AND rule_version = :rule_version
              AND signaled_at > NOW() - INTERVAL '8 hours'
        ) AS cooldown_active
    """

    result = engine.execute(query, {
        "asset_id": asset_id,
        "rule_version": rule_version
    }).fetchone()

    return result["cooldown_active"]


# In signal generation flow
if check_cooldown(asset_id, rule_version):
    logger.info(f"{asset_id}: Cooldown active, skipping signal")
    return None
```

### Why 8 Hours?

- Long enough to avoid spam (3 signals max per day)
- Short enough to catch swings (crypto moves fast)
- Tunable via micro-backtest (test 6h, 8h, 12h)

## Idempotency

**Purpose:** If Prefect job reruns, don't create duplicate signals.

### Idempotency Key Format

```python
def create_idempotency_key(
    asset_id: str,
    timeframe: str,
    rule_version: str,
    signaled_at: datetime
) -> str:
    """
    Create unique key for signal.

    Format: {asset_id}:{timeframe}:{rule_version}:{iso_timestamp}
    Example: BTC-USD:15m:rsi_v1:2025-01-20T10:15:00Z
    """
    return f"{asset_id}:{timeframe}:{rule_version}:{signaled_at.isoformat()}"
```

### Database Constraint

```sql
-- Unique constraint enforces idempotency
CREATE UNIQUE INDEX idx_signals_idempotency ON signals(idempotency_key);
```

### Insert with Conflict Handling

```python
def store_signal(signal: dict):
    """
    Store signal, handling conflicts gracefully.

    If idempotency_key exists, skip (return existing signal ID).
    """
    insert_query = """
        INSERT INTO signals (
            asset_id, timeframe, signaled_at, rule_version,
            regime, signal_type, strength, explanation, reasoning,
            price_at_signal, idempotency_key
        )
        VALUES (
            :asset_id, :timeframe, :signaled_at, :rule_version,
            :regime, :signal_type, :strength, :explanation, :reasoning,
            :price_at_signal, :idempotency_key
        )
        ON CONFLICT (idempotency_key) DO NOTHING
        RETURNING id
    """

    result = engine.execute(insert_query, signal).fetchone()

    if result:
        logger.info(f"New signal created: {result['id']}")
    else:
        logger.info("Signal already exists (idempotent skip)")
```

## Plain English Explanations

**Purpose:** Users don't understand "MACD histogram crossed signal line" — translate to human language.

### Template System

```python
EXPLANATION_TEMPLATES = {
    "rsi_oversold_range": """
        {asset} is oversold (RSI {rsi:.1f}) in a ranging market.
        This often leads to a bounce back toward average price.
        Risk: News events can override technical signals.
    """,

    "ema_bullish_cross_trend": """
        {asset} momentum shifted bullish (fast EMA crossed above slow EMA).
        Strong trend detected (ADX {adx:.1f}) confirms this isn't a false signal.
        Consider entering long position with stop loss below recent low.
    """,

    "ema_bearish_cross_trend": """
        {asset} momentum turned bearish (fast EMA crossed below slow EMA).
        Strong downtrend confirmed (ADX {adx:.1f}).
        If holding: Consider taking profit or setting trailing stop.
    """
}


def generate_explanation(
    signal_type: str,
    regime: str,
    indicators: dict
) -> str:
    """
    Generate plain English explanation.

    Args:
        signal_type: 'BUY' or 'HOLD'
        regime: 'trend' or 'range'
        indicators: dict with rsi, ema_diff, adx, etc.

    Returns:
        Human-readable string
    """
    if regime == "range" and signal_type == "BUY":
        template = EXPLANATION_TEMPLATES["rsi_oversold_range"]
    elif regime == "trend" and signal_type == "BUY":
        template = EXPLANATION_TEMPLATES["ema_bullish_cross_trend"]
    elif regime == "trend" and signal_type == "HOLD":
        template = EXPLANATION_TEMPLATES["ema_bearish_cross_trend"]

    return template.format(**indicators)
```

### Example Output

**User sees:**

```text
Bitcoin is oversold (RSI 18.5) in a ranging market.
This often leads to a bounce back toward average price.
Risk: News events can override technical signals.

Strength: 82/100 (STRONG)
Current Price: $43,250
Regime: Ranging (ADX 12.3)
```

**Not:**

```text
RSI(14) = 18.5, MACD = -120.5, Signal = -95.2, Histogram = -25.3
```

## Complete Signal Generation Flow

```python
@flow(name="signal-generation")
def signal_generation_flow(assets: list[str] = ["BTC-USD", "ETH-USD"]):
    """
    Generate trading signals with regime logic.

    Runs 5 minutes after indicator calculation (every 15 min).
    """
    for asset_id in assets:
        try:
            # 1. Fetch latest indicators
            indicators = fetch_latest_indicators(asset_id)

            if not indicators:
                logger.warning(f"{asset_id}: No indicators available")
                continue

            # 2. Extract values
            rsi = indicators["rsi"]
            ema_12 = indicators["ema_12"]
            ema_26 = indicators["ema_26"]
            ema_diff = ema_12 - ema_26
            adx = indicators["adx"]
            regime = indicators["regime"]
            timestamp = indicators["timestamp"]
            price = indicators["close"]

            # 3. Check regime
            if regime == "uncertain":
                logger.info(f"{asset_id}: Uncertain regime, skipping signal")
                continue

            # 4. Determine rule version
            if regime == "range":
                rule_version = "rsi_mean_reversion_v1"
            else:  # trend
                rule_version = "ema_crossover_v1"

            # 5. Check cooldown
            if check_cooldown(asset_id, rule_version):
                logger.info(f"{asset_id}: Cooldown active")
                continue

            # 6. Apply rules
            signal_type = None
            reasoning = []

            if regime == "range":
                if rsi < 30:
                    signal_type = "BUY"
                    reasoning = [
                        f"RSI oversold ({rsi:.1f})",
                        "Mean-reversion setup in ranging market",
                        f"ADX low ({adx:.1f}) confirms sideways price action"
                    ]
                elif rsi > 70:
                    signal_type = "HOLD"
                    reasoning = [
                        f"RSI overbought ({rsi:.1f})",
                        "Price likely to pullback",
                        "Consider taking profit"
                    ]

            elif regime == "trend":
                ema_diff_prev = get_previous_ema_diff(asset_id)

                if ema_diff_prev < 0 and ema_diff > 0:
                    signal_type = "BUY"
                    reasoning = [
                        "EMA-12 crossed above EMA-26",
                        f"Strong trend (ADX {adx:.1f})",
                        "Bullish momentum shift"
                    ]
                elif ema_diff_prev > 0 and ema_diff < 0:
                    signal_type = "HOLD"
                    reasoning = [
                        "EMA-12 crossed below EMA-26",
                        f"Strong downtrend (ADX {adx:.1f})",
                        "Bearish momentum shift"
                    ]

            # 7. If no signal triggered, skip
            if not signal_type:
                logger.info(f"{asset_id}: No signal triggered")
                continue

            # 8. Calculate strength
            strength = calculate_signal_strength(
                signal_type, rsi, ema_diff, adx, regime
            )

            # 9. Generate explanation
            explanation = generate_explanation(
                signal_type, regime, {
                    "asset": asset_id,
                    "rsi": rsi,
                    "ema_diff": ema_diff,
                    "adx": adx,
                    "price": price
                }
            )

            # 10. Create idempotency key
            idempotency_key = create_idempotency_key(
                asset_id, "15m", rule_version, timestamp
            )

            # 11. Store signal
            signal = {
                "asset_id": asset_id,
                "timeframe": "15m",
                "signaled_at": timestamp,
                "rule_version": rule_version,
                "regime": regime,
                "signal_type": signal_type,
                "strength": strength,
                "explanation": explanation,
                "reasoning": json.dumps(reasoning),
                "price_at_signal": price,
                "idempotency_key": idempotency_key
            }

            signal_id = store_signal(signal)

            # 12. Track in PostHog
            posthog.capture(
                distinct_id="system",
                event="signal_generated",
                properties={
                    "asset_id": asset_id,
                    "signal_type": signal_type,
                    "strength": strength,
                    "regime": regime,
                    "rule_version": rule_version
                }
            )

            logger.info(
                f"{asset_id}: {signal_type} signal generated "
                f"(strength: {strength}, regime: {regime})"
            )

        except Exception as e:
            logger.error(f"Failed to generate signal for {asset_id}: {e}")
            alert_ops(f"Signal generation failed: {asset_id} - {e}")
```

## Testing Signals Manually

```bash
cd /Users/diegovfeder/workspace/jobs/signals

# Run signal generation locally
python scripts/test_signals.py
```

**test_signals.py:**

```python
# Manually trigger signal generation with mock data
indicators = {
    "rsi": 25,
    "ema_12": 43000,
    "ema_26": 42500,
    "adx": 15,
    "regime": "range",
    "timestamp": datetime.now(),
    "close": 43100
}

signal = generate_signal("BTC-USD", indicators)
print(f"Signal: {signal['signal_type']}, Strength: {signal['strength']}")
print(f"Explanation: {signal['explanation']}")
```

---

**Next:** See `11-MONITORING.md` for notification delivery and PostHog tracking.

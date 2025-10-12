# Technical Indicators Explained

Deep dive into RSI and EMA - what they measure, when they work, and how to implement them.

## Philosophy

**Indicators are tools, not magic.**

- They measure past price behavior
- They don't predict the future
- They work *sometimes* in *certain contexts*
- Our job: Use them when context is right (regime detection)

## RSI (Relative Strength Index)

### What It Measures

- **"How overbought or oversold is this asset?"**

RSI tracks momentum by comparing average gains vs average losses over a period (typically 14 bars).

### The Formula

```bash
Step 1: Calculate price changes
  gain = max(close_today - close_yesterday, 0)
  loss = max(close_yesterday - close_today, 0)

Step 2: Calculate average gain and loss (14-period)
  avg_gain = SMA(gains, 14)
  avg_loss = SMA(losses, 14)

Step 3: Calculate Relative Strength
  RS = avg_gain / avg_loss

Step 4: Normalize to 0-100 scale
  RSI = 100 - (100 / (1 + RS))
```

### Implementation

```python
import pandas as pd
import numpy as np

def calculate_rsi(df: pd.DataFrame, period: int = 14, price_column: str = "close") -> pd.Series:
    """
    Calculate RSI (Relative Strength Index).

    Args:
        df: DataFrame with price data
        period: Lookback period (default: 14)
        price_column: Column name for prices (default: "close")

    Returns:
        pd.Series: RSI values (0-100)

    Example:
        >>> df = pd.DataFrame({'close': [100, 102, 101, 105, 107, 103, 108, 106, 110]})
        >>> rsi = calculate_rsi(df, period=6)
        >>> rsi.iloc[-1]
        65.43
    """
    # Calculate price changes
    delta = df[price_column].diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    # Calculate average gain and loss using EMA (smoothed)
    # Note: Wilder uses a special smoothing method, equivalent to EMA with alpha = 1/period
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()

    # Calculate RS
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi
```

### Interpretation

```text
RSI Value    Interpretation           Action in Range    Action in Trend
───────────────────────────────────────────────────────────────────────
90-100       Extremely Overbought     Strong HOLD        Continue trend
70-89        Overbought               HOLD               Neutral
50-69        Neutral-Bullish          -                  -
30-49        Neutral-Bearish          -                  -
20-29        Oversold                 BUY signal         Possible bounce
0-19         Extremely Oversold       Strong BUY         Divergence?
```

### When RSI Works

✅ **Ranging Markets (ADX < 20)**

- Price bounces between support/resistance
- RSI < 30 → Price likely to bounce up (mean reversion)
- RSI > 70 → Price likely to pull back

❌ **Trending Markets (ADX > 25)**

- RSI can stay >70 or <30 for extended periods
- "The trend is your friend" - don't fight it
- RSI overbought in uptrend ≠ time to sell

### Visual Example

```bash
Price Chart (Ranging Market):
     45000 ──────╮           ╭──────
     44000        ╰───╮   ╭───╯
     43000            ╰───╯
                      ▲
                   RSI < 30
                   BUY signal

RSI Chart:
     100  ─────────────────────────────
      70  ──────╮           ╭──────
      50         │           │
      30  ───────╰───╮   ╭───╯
       0             ╰───╯
                      ▲
                   Oversold
```

### Common Mistakes

1. **Ignoring Regime**

    ```python
    # WRONG: Always buy on RSI < 30
    if rsi < 30:
        buy()

    # RIGHT: Check regime first
    if rsi < 30 and regime == "range":
        buy()  # OK, mean reversion works here
    elif rsi < 30 and regime == "trend":
        pass   # Might keep going down, skip
    ```

2. **Using Fixed Thresholds**

    ```python
    # WRONG: RSI 30/70 doesn't work everywhere
    if rsi < 30:
        buy()

    # BETTER: Tune thresholds per asset via backtest
    BTC_THRESHOLDS = {"oversold": 25, "overbought": 75}
    ETH_THRESHOLDS = {"oversold": 28, "overbought": 72}
    ```

3. **Not Waiting for Confirmation**

    ```python
    # WRONG: Buy the instant RSI < 30
    if rsi < 30:
        buy_immediately()

    # BETTER: Wait for RSI to turn back up
    if rsi_prev < 30 and rsi_current > rsi_prev:
        buy()  # Momentum shifting
    ```

### RSI Divergence (Advanced - Phase 2)

**Bullish Divergence:**

- Price makes lower low
- RSI makes higher low
- Signal: Momentum weakening, reversal possible

**Bearish Divergence:**

- Price makes higher high
- RSI makes lower high
- Signal: Momentum weakening, pullback likely

*Not implemented in MVP - adds complexity.*

---

## EMA (Exponential Moving Average)

- What It Measures

> **"What's the average price, but recent prices matter more?"**

EMA is a moving average that gives more weight to recent data. Traders use EMA crossovers to detect momentum shifts.

- The Formula

```bash
Step 1: Calculate smoothing factor
  α (alpha) = 2 / (period + 1)

Step 2: Calculate EMA recursively
  EMA_today = (Price_today × α) + (EMA_yesterday × (1 - α))

For first value:
  EMA_first = SMA(prices, period)
```

- Implementation

```python
def calculate_ema(df: pd.DataFrame, period: int, price_column: str = "close") -> pd.Series:
    """
    Calculate EMA (Exponential Moving Average).

    Args:
        df: DataFrame with price data
        period: EMA period (e.g., 12, 26)
        price_column: Column name for prices (default: "close")

    Returns:
        pd.Series: EMA values

    Example:
        >>> df = pd.DataFrame({'close': [100, 102, 101, 105, 107, 103, 108]})
        >>> ema_12 = calculate_ema(df, period=12)
        >>> ema_26 = calculate_ema(df, period=26)
    """
    return df[price_column].ewm(span=period, adjust=False).mean()
```

### EMA Crossover Strategy

**Setup:** Two EMAs

- **Fast EMA (12-period):** Reacts quickly to price changes
- **Slow EMA (26-period):** Smoother, filters noise

**Signals:**

- **Bullish Crossover (Golden Cross):** EMA-12 crosses above EMA-26
  - Interpretation: Short-term momentum > long-term momentum
  - Action: BUY in trending markets

- **Bearish Crossover (Death Cross):** EMA-12 crosses below EMA-26
  - Interpretation: Short-term momentum < long-term momentum
  - Action: HOLD (or sell if long)

- Implementation

```python
def detect_ema_crossover(
    ema_12: pd.Series,
    ema_26: pd.Series
) -> tuple[str, bool]:
    """
    Detect EMA crossover events.

    Args:
        ema_12: Fast EMA series
        ema_26: Slow EMA series

    Returns:
        (crossover_type, crossover_detected)
        crossover_type: 'bullish', 'bearish', or 'none'
        crossover_detected: True if crossover happened in last bar

    Example:
        >>> ema_12 = pd.Series([100, 101, 102, 103])
        >>> ema_26 = pd.Series([102, 102, 102, 102])
        >>> detect_ema_crossover(ema_12, ema_26)
        ('bullish', True)  # EMA-12 crossed above EMA-26
    """
    if len(ema_12) < 2 or len(ema_26) < 2:
        return "none", False

    # Current values
    ema_12_curr = ema_12.iloc[-1]
    ema_26_curr = ema_26.iloc[-1]

    # Previous values
    ema_12_prev = ema_12.iloc[-2]
    ema_26_prev = ema_26.iloc[-2]

    # Check for bullish crossover
    if ema_12_prev <= ema_26_prev and ema_12_curr > ema_26_curr:
        return "bullish", True

    # Check for bearish crossover
    elif ema_12_prev >= ema_26_prev and ema_12_curr < ema_26_curr:
        return "bearish", True

    else:
        return "none", False
```

### When EMA Crossover Works

✅ **Trending Markets (ADX > 25)**

- Strong directional movement
- Crossover confirms trend continuation
- Low false signals

❌ **Ranging Markets (ADX < 20)**

- Price chops sideways
- Frequent whipsaws (false crossovers)
- Better to use RSI

- Visual Example

```bash
Trending Market (EMA Crossover Works):

Price
50000 ─────────────────────╱
                        ╱
45000              ╱─────     EMA-12 (fast, red)
                ╱─────────    EMA-26 (slow, blue)
40000      ╱────
        ╱──
35000 ──
      │
      └─ Bullish crossover → BUY signal
         (confirmed by ADX > 25)


Ranging Market (EMA Crossover Fails):

Price
45000 ──╮   ╭──╮   ╭──╮
        │   │  │   │  │   Many false crossovers!
40000 ──╰───╯──╰───╯──╰──  Don't use EMA here.
                           Use RSI instead.
```

- Common Mistakes

1. **Using EMA in Ranging Markets**

    ```python
    # WRONG: Blindly follow crossovers
    if ema_12 > ema_26:
        buy()

    # RIGHT: Check regime first
    if ema_12 > ema_26 and regime == "trend":
        buy()  # OK, trend-following works here
    ```

2. **Not Confirming with ADX**

    ```python
    # WRONG: Crossover without trend strength
    if ema_12 > ema_26:
        buy()

    # BETTER: Require strong trend
    if ema_12 > ema_26 and adx > 25:
        buy()  # Confirmed trend
    ```

3. **Reacting to Every Wiggle**

    ```python
    # WRONG: Tiny crossover might be noise
    if ema_12 > ema_26:
        buy()

    # BETTER: Require meaningful separation
    ema_diff = ema_12 - ema_26
    if ema_diff > threshold:  # e.g., $100 for BTC
        buy()
    ```

### EMA vs SMA (Simple Moving Average)

| Aspect | SMA | EMA |
|--------|-----|-----|
| Weight | All prices equal | Recent prices weighted more |
| Lag | More lag | Less lag |
| Smoothness | Smoother | More reactive |
| Use Case | Long-term trends | Short-term momentum |

**Why We Use EMA:**

- Crypto moves fast (EMA reacts faster than SMA)
- We trade 15-min bars (need quick signals)
- Less lag = earlier entry

---

## ADX (Average Directional Index)

- What It Measures

> **"How strong is the trend, regardless of direction?"**

ADX measures trend strength from 0-100:

- 0-20: Weak/no trend (ranging)
- 20-25: Developing trend (uncertain)
- 25-50: Strong trend (follow the trend)
- 50+: Very strong trend (rare in crypto)

### Implementation (Simplified)

```python
def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate ADX (Average Directional Index).

    This is a simplified version. Full implementation uses:
    1. True Range (TR)
    2. Directional Movement (+DM, -DM)
    3. Directional Indicators (+DI, -DI)
    4. Directional Index (DX)
    5. Average Directional Index (ADX)

    For MVP, we can use a simpler volatility-based proxy.

    Args:
        df: DataFrame with OHLC data
        period: ADX period (default: 14)

    Returns:
        pd.Series: ADX values (0-100)
    """
    # Simplified approach (replace with ta-lib in production):
    # Use rolling standard deviation / rolling mean as proxy

    rolling_std = df["close"].rolling(period).std()
    rolling_mean = df["close"].rolling(period).mean()

    # Coefficient of variation * 100 ≈ volatility-based ADX proxy
    adx_proxy = (rolling_std / rolling_mean) * 100

    # Normalize to roughly match ADX scale (0-50)
    adx_proxy = adx_proxy.clip(0, 50)

    return adx_proxy


# Production implementation using ta-lib:
import talib

def calculate_adx_talib(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate ADX using TA-Lib (more accurate).

    Install: pip install TA-Lib
    """
    return talib.ADX(df["high"], df["low"], df["close"], timeperiod=period)
```

- Interpretation

```python
def interpret_adx(adx: float) -> str:
    """
    Interpret ADX value.

    Returns:
        Human-readable interpretation
    """
    if adx < 20:
        return "Weak trend or ranging market (use RSI)"
    elif adx < 25:
        return "Developing trend (uncertain, wait)"
    elif adx < 40:
        return "Strong trend (use EMA crossover)"
    else:
        return "Very strong trend (ride it)"
```

---

## Combining Indicators: The Regime Logic

### The Decision Tree

```bash
Check ADX first:
│
├─ ADX > 25 (TRENDING)
│  ├─ Check EMA crossover
│  │  ├─ EMA-12 > EMA-26 → BUY
│  │  └─ EMA-12 < EMA-26 → HOLD
│  │
│  └─ Ignore RSI (can stay extreme for long periods)
│
├─ ADX < 20 (RANGING)
│  ├─ Check RSI
│  │  ├─ RSI < 30 → BUY (oversold bounce)
│  │  └─ RSI > 70 → HOLD (overbought pullback)
│  │
│  └─ Ignore EMA (too many false crossovers)
│
└─ 20 <= ADX <= 25 (UNCERTAIN)
   └─ No signals (wait for clarity)
```

### Why This Works

**Problem:** No single indicator works all the time.

- RSI fails in trends (stays overbought/oversold)
- EMA fails in ranges (whipsaws)

**Solution:** Use ADX to pick the right tool.

- Trending? Use EMA.
- Ranging? Use RSI.
- Uncertain? Wait.

### Example Scenarios

- **Scenario 1: Strong Uptrend**

```bash
Price: ↗↗↗
ADX: 35 (strong trend)
RSI: 75 (overbought)
EMA: 12 > 26 (bullish)

Decision:
- Ignore RSI (overbought in uptrend is normal)
- Follow EMA (trend is strong)
- Action: BUY on EMA crossover
```

- **Scenario 2: Sideways Range**

```bash
Price: ↔↔↔
ADX: 15 (weak trend)
RSI: 25 (oversold)
EMA: Frequent crossovers

Decision:
- Ignore EMA (too many false signals)
- Follow RSI (mean reversion works)
- Action: BUY on RSI < 30
```

- **Scenario 3: Uncertain Market**

```bash
Price: ↗↔↘
ADX: 22 (transitioning)
RSI: 50 (neutral)
EMA: Close to crossover

Decision:
- Don't trust either indicator yet
- Action: WAIT for ADX to break 25 or drop below 20
```

---

## Testing Your Indicators

### Unit Tests

```python
import pytest
import pandas as pd

def test_rsi_calculation():
    """Test RSI with known values."""
    # Simple case: all prices going up
    df = pd.DataFrame({"close": [100, 101, 102, 103, 104, 105]})
    rsi = calculate_rsi(df, period=5)

    # RSI should be high (overbought) since prices only go up
    assert rsi.iloc[-1] > 70

def test_ema_crossover():
    """Test EMA crossover detection."""
    ema_12 = pd.Series([100, 101, 102, 103])
    ema_26 = pd.Series([102, 102, 102, 102])

    crossover_type, detected = detect_ema_crossover(ema_12, ema_26)

    assert crossover_type == "bullish"
    assert detected == True

def test_regime_detection():
    """Test ADX-based regime classification."""
    assert detect_regime(adx=30) == "trend"
    assert detect_regime(adx=15) == "range"
    assert detect_regime(adx=22) == "uncertain"
```

### Visual Verification

```python
import matplotlib.pyplot as plt

def plot_indicators(df: pd.DataFrame):
    """
    Plot price, RSI, EMA, and ADX for visual inspection.
    """
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

    # Price + EMA
    ax1.plot(df["timestamp"], df["close"], label="Price", color="black")
    ax1.plot(df["timestamp"], df["ema_12"], label="EMA-12", color="red")
    ax1.plot(df["timestamp"], df["ema_26"], label="EMA-26", color="blue")
    ax1.set_ylabel("Price ($)")
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # RSI
    ax2.plot(df["timestamp"], df["rsi"], label="RSI", color="purple")
    ax2.axhline(70, color="red", linestyle="--", alpha=0.5, label="Overbought")
    ax2.axhline(30, color="green", linestyle="--", alpha=0.5, label="Oversold")
    ax2.set_ylabel("RSI")
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    # ADX
    ax3.plot(df["timestamp"], df["adx"], label="ADX", color="orange")
    ax3.axhline(25, color="blue", linestyle="--", alpha=0.5, label="Trend Threshold")
    ax3.axhline(20, color="gray", linestyle="--", alpha=0.5, label="Range Threshold")
    ax3.set_ylabel("ADX")
    ax3.set_xlabel("Time")
    ax3.legend()
    ax3.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()
```

---

## Further Reading

- **RSI:** [Investopedia - RSI](https://www.investopedia.com/terms/r/rsi.asp)
- **EMA:** [Investopedia - EMA](https://www.investopedia.com/terms/e/ema.asp)
- **ADX:** [Investopedia - ADX](https://www.investopedia.com/terms/a/adx.asp)
- **Technical Analysis Library:** [TA-Lib Python](https://github.com/mrjbq7/ta-lib)

---

**Next:** See `06-SIGNAL-GENERATION.md` for how these indicators combine into trading signals.

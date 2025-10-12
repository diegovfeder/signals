# Data Science - Indicators & Signals

## Overview

This guide explains the 2 indicators we use (RSI and EMA) and how we generate trading signals from them. Written for developers new to technical analysis.

## The Basics

### What is an Indicator?

An indicator is a mathematical calculation based on price and/or volume data. It helps identify patterns that might predict future price movements.

### What is a Signal?

A signal is a recommendation to BUY or HOLD based on indicator values. We don't generate SELL signals in this MVP - if conditions aren't good for buying, we signal HOLD.

---

## Indicator #1: RSI (Relative Strength Index)

### What It Measures

RSI measures how "overbought" or "oversold" an asset is on a scale of 0-100.

- **RSI < 30**: Oversold (price might bounce up)
- **RSI > 70**: Overbought (price might pull back)
- **RSI 30-70**: Neutral zone

### The Math

```python
def calculate_rsi(prices, period=14):
    """
    Calculate RSI (Relative Strength Index)

    Args:
        prices: pandas Series of closing prices
        period: lookback period (default 14)

    Returns:
        pandas Series of RSI values (0-100)
    """
    # Calculate price changes
    delta = prices.diff()

    # Separate gains and losses
    gain = delta.where(delta > 0, 0)  # Positive changes only
    loss = -delta.where(delta < 0, 0)  # Negative changes (absolute value)

    # Calculate average gain and loss over period
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()

    # Calculate relative strength
    rs = avg_gain / avg_loss

    # Calculate RSI
    rsi = 100 - (100 / (1 + rs))

    return rsi
```

### Example

```python
import pandas as pd
import yfinance as yf

# Fetch BTC data
btc = yf.Ticker("BTC-USD")
df = btc.history(period="30d", interval="15m")

# Calculate RSI
df['rsi'] = calculate_rsi(df['Close'], period=14)

# Check latest value
print(f"Current RSI: {df['rsi'].iloc[-1]:.1f}")

# Example outputs:
# RSI = 28 → Oversold, likely to bounce (BUY signal)
# RSI = 75 → Overbought, might pull back (HOLD signal)
# RSI = 50 → Neutral (HOLD signal)
```

### When RSI Works Best

✅ **Good for:**

- Ranging markets (price bouncing between support/resistance)
- Identifying extreme conditions (panic selling, euphoric buying)
- Short-term reversals

❌ **Bad for:**

- Strong trending markets (RSI can stay oversold/overbought for long periods)
- Low volume periods (false signals)

### Common Mistakes

1. **Treating RSI < 30 as guaranteed bounce** - RSI can stay low during strong downtrends
2. **Using RSI alone** - Always combine with other indicators or price action
3. **Wrong period** - 14 is standard, but shorter periods (7-9) are more sensitive

---

## Indicator #2: EMA (Exponential Moving Average)

- What It Measures

EMA is a moving average that gives more weight to recent prices. It helps identify trends and momentum.

We use two EMAs:

- **EMA-12** (fast, reacts quickly to price changes)
- **EMA-26** (slow, smoother)

### The Signal

- **EMA-12 crosses ABOVE EMA-26**: Bullish momentum (BUY signal)
- **EMA-12 crosses BELOW EMA-26**: Bearish momentum (HOLD signal)

### The Math

```python
def calculate_ema(prices, period):
    """
    Calculate EMA (Exponential Moving Average)

    Args:
        prices: pandas Series of closing prices
        period: EMA period (e.g., 12 or 26)

    Returns:
        pandas Series of EMA values
    """
    # Pandas has built-in EMA calculation
    ema = prices.ewm(span=period, adjust=False).mean()

    return ema


def detect_ema_crossover(df):
    """
    Detect EMA crossover signals

    Args:
        df: DataFrame with 'Close' column

    Returns:
        'BUY', 'HOLD', or None
    """
    # Calculate EMAs
    df['ema_12'] = calculate_ema(df['Close'], 12)
    df['ema_26'] = calculate_ema(df['Close'], 26)

    # Get current and previous values
    curr_12 = df['ema_12'].iloc[-1]
    curr_26 = df['ema_26'].iloc[-1]
    prev_12 = df['ema_12'].iloc[-2]
    prev_26 = df['ema_26'].iloc[-2]

    # Detect crossover
    if prev_12 <= prev_26 and curr_12 > curr_26:
        return 'BUY'  # Bullish crossover (golden cross)
    elif prev_12 >= prev_26 and curr_12 < curr_26:
        return 'HOLD'  # Bearish crossover (death cross)
    else:
        return None  # No crossover
```

### Example

```python
import yfinance as yf

# Fetch ETH data
eth = yf.Ticker("ETH-USD")
df = eth.history(period="7d", interval="15m")

# Calculate EMAs
df['ema_12'] = calculate_ema(df['Close'], 12)
df['ema_26'] = calculate_ema(df['Close'], 26)

# Detect crossover
signal = detect_ema_crossover(df)

print(f"EMA-12: {df['ema_12'].iloc[-1]:.2f}")
print(f"EMA-26: {df['ema_26'].iloc[-1]:.2f}")
print(f"Signal: {signal}")

# Example outputs:
# EMA-12: 2,345.67, EMA-26: 2,340.12 → EMA-12 > EMA-26 (bullish)
# EMA-12: 2,310.45, EMA-26: 2,315.89 → EMA-12 < EMA-26 (bearish, HOLD)
```

### When EMA Works Best

✅ **Good for:**

- Trending markets (identifies momentum early)
- Catching the start of new trends
- Filtering out noise (smooths price action)

❌ **Bad for:**

- Ranging markets (whipsaws - false crossovers)
- Low volatility periods (lags behind price)

### Common Mistakes

1. **Acting on every crossover** - Many are false signals in choppy markets
2. **Using too short periods** - EMA-5/10 generates too many signals
3. **Ignoring the bigger trend** - Crossover works best when aligned with trend

---

## Combining RSI + EMA

### Signal Generation Logic

We combine both indicators to generate stronger signals:

```python
def generate_signal(df):
    """
    Generate trading signal based on RSI and EMA

    Args:
        df: DataFrame with OHLCV data

    Returns:
        dict with signal, strength, and reasoning
    """
    # Calculate indicators
    df['rsi'] = calculate_rsi(df['Close'], 14)
    df['ema_12'] = calculate_ema(df['Close'], 12)
    df['ema_26'] = calculate_ema(df['Close'], 26)

    # Get latest values
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None
    strength = 0
    reasoning = []

    # RSI Signal (oversold = BUY)
    if latest['rsi'] < 30:
        signal = 'BUY'
        strength = 100 - latest['rsi']  # Lower RSI = stronger signal
        reasoning.append(f"RSI oversold ({latest['rsi']:.1f})")

    # EMA Crossover (golden cross = BUY)
    if prev['ema_12'] <= prev['ema_26'] and latest['ema_12'] > latest['ema_26']:
        signal = 'BUY'
        strength = max(strength, 80)  # Strong signal
        reasoning.append("EMA-12 crossed above EMA-26 (golden cross)")

    # Both indicators agree = very strong signal
    if latest['rsi'] < 30 and latest['ema_12'] > latest['ema_26']:
        strength = 95
        reasoning.append("Both RSI and EMA confirm BUY")

    # No signal or weak signal = HOLD
    if signal is None or strength < 70:
        return {
            'signal': 'HOLD',
            'strength': strength,
            'reasoning': 'No strong setup detected'
        }

    return {
        'signal': signal,
        'strength': int(strength),
        'reasoning': ' • '.join(reasoning),
        'price': latest['Close'],
        'rsi': latest['rsi'],
        'ema_12': latest['ema_12'],
        'ema_26': latest['ema_26']
    }
```

### Signal Strength Scoring

We score signals from 0-100:

| Strength | Meaning | Action |
|----------|---------|--------|
| 90-100 | Very strong (both indicators agree) | Email user |
| 70-89 | Strong (one indicator very clear) | Email user |
| 50-69 | Moderate (borderline) | Save to DB, no email |
| 0-49 | Weak (unclear setup) | HOLD, don't save |

**Email Threshold**: Only send emails for strength >= 70

---

## Quality Checks

Before generating signals, we validate the data:

### 1. Staleness Check

```python
def check_data_freshness(timestamp, max_age_minutes=20):
    """
    Ensure data is fresh (not stale)

    Args:
        timestamp: datetime of latest bar
        max_age_minutes: max acceptable age

    Returns:
        bool: True if fresh, False if stale
    """
    from datetime import datetime, timezone

    age = (datetime.now(timezone.utc) - timestamp).seconds / 60

    if age > max_age_minutes:
        print(f"⚠️ Data is {age:.1f} minutes old (max: {max_age_minutes})")
        return False

    return True
```

### 2. Volume Check

```python
def check_volume(df, min_volume=1000):
    """
    Ensure volume is significant

    Args:
        df: DataFrame with 'Volume' column
        min_volume: minimum acceptable volume

    Returns:
        bool: True if volume OK, False if too low
    """
    avg_volume = df['Volume'].rolling(window=10).mean().iloc[-1]

    if avg_volume < min_volume:
        print(f"⚠️ Volume too low ({avg_volume:.0f})")
        return False

    return True
```

### 3. Price Spike Check

```python
def check_for_spike(df, max_change_pct=5):
    """
    Detect abnormal price spikes (fat-finger errors)

    Args:
        df: DataFrame with 'Close' column
        max_change_pct: max acceptable price change %

    Returns:
        bool: True if OK, False if spike detected
    """
    latest = df['Close'].iloc[-1]
    prev = df['Close'].iloc[-2]

    change_pct = abs((latest - prev) / prev * 100)

    if change_pct > max_change_pct:
        print(f"⚠️ Price spike detected ({change_pct:.1f}%)")
        return False

    return True
```

---

## Complete Signal Pipeline

Putting it all together:

```python
import yfinance as yf
from datetime import datetime, timezone

def run_signal_pipeline(symbol):
    """
    Complete pipeline: fetch data → validate → calculate → signal

    Args:
        symbol: e.g., 'BTC-USD', 'ETH-USD'

    Returns:
        dict with signal data or None
    """
    print(f"📊 Processing {symbol}...")

    # 1. Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="7d", interval="15m")

    if df.empty:
        print(f"❌ No data for {symbol}")
        return None

    # 2. Quality checks
    if not check_data_freshness(df.index[-1]):
        return None

    if not check_volume(df):
        return None

    if not check_for_spike(df):
        return None

    # 3. Calculate indicators
    df['rsi'] = calculate_rsi(df['Close'], 14)
    df['ema_12'] = calculate_ema(df['Close'], 12)
    df['ema_26'] = calculate_ema(df['Close'], 26)

    # 4. Generate signal
    signal = generate_signal(df)

    # 5. Add metadata
    signal['symbol'] = symbol
    signal['timestamp'] = datetime.now(timezone.utc)

    print(f"✅ {signal['signal']} signal (strength: {signal['strength']})")

    return signal


# Run for both assets
if __name__ == "__main__":
    for symbol in ['BTC-USD', 'ETH-USD']:
        signal = run_signal_pipeline(symbol)

        if signal and signal['strength'] >= 70:
            print(f"📧 Would send email for {symbol}")
            print(f"   {signal['reasoning']}")
```

---

## Testing Your Indicators

### 1. Visual Test (Chart)

```python
import matplotlib.pyplot as plt

def plot_indicators(symbol):
    """Plot price with RSI and EMA"""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="7d", interval="15m")

    df['rsi'] = calculate_rsi(df['Close'], 14)
    df['ema_12'] = calculate_ema(df['Close'], 12)
    df['ema_26'] = calculate_ema(df['Close'], 26)

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

    # Plot price and EMAs
    ax1.plot(df.index, df['Close'], label='Price', linewidth=2)
    ax1.plot(df.index, df['ema_12'], label='EMA-12', alpha=0.7)
    ax1.plot(df.index, df['ema_26'], label='EMA-26', alpha=0.7)
    ax1.set_title(f'{symbol} Price + EMA')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Plot RSI
    ax2.plot(df.index, df['rsi'], label='RSI', color='purple', linewidth=2)
    ax2.axhline(y=70, color='r', linestyle='--', alpha=0.5, label='Overbought')
    ax2.axhline(y=30, color='g', linestyle='--', alpha=0.5, label='Oversold')
    ax2.fill_between(df.index, 30, 70, alpha=0.1)
    ax2.set_title('RSI')
    ax2.set_ylim(0, 100)
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# Test
plot_indicators('BTC-USD')
```

### 2. Unit Tests

```python
import pytest
import pandas as pd

def test_rsi_calculation():
    """Test RSI calculation with known values"""
    # Create test data
    prices = pd.Series([100, 102, 101, 103, 105, 104, 106, 108, 107, 109, 110,
                        109, 111, 113, 112, 114, 116, 115, 117, 119])

    rsi = calculate_rsi(prices, period=14)

    # RSI should be between 0 and 100
    assert (rsi >= 0).all() and (rsi <= 100).all()

    # RSI should increase when price trends up
    assert rsi.iloc[-1] > 50


def test_ema_crossover():
    """Test EMA crossover detection"""
    # Create test data with clear crossover
    prices = pd.Series([100] * 10 + [102, 104, 106, 108, 110, 112])

    df = pd.DataFrame({'Close': prices})
    df['ema_12'] = calculate_ema(df['Close'], 12)
    df['ema_26'] = calculate_ema(df['Close'], 26)

    signal = detect_ema_crossover(df)

    # Should detect bullish crossover
    assert signal == 'BUY' or signal is None


def test_signal_generation():
    """Test complete signal generation"""
    # Create realistic test data
    ticker = yf.Ticker('BTC-USD')
    df = ticker.history(period='7d', interval='15m')

    signal = generate_signal(df)

    # Signal should have required keys
    assert 'signal' in signal
    assert 'strength' in signal
    assert 'reasoning' in signal

    # Strength should be 0-100
    assert 0 <= signal['strength'] <= 100
```

---

## Next Steps

1. **Implement in Prefect flow** - See [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Test locally** - Run `run_signal_pipeline()` and verify outputs
3. **Visualize results** - Use `plot_indicators()` to validate logic
4. **Add to database** - Save signals to Supabase
5. **Connect to email** - Trigger Resend notifications

---

## Resources for Learning More

### Technical Analysis Basics

- [Investopedia: RSI](https://www.investopedia.com/terms/r/rsi.asp)
- [Investopedia: EMA](https://www.investopedia.com/terms/e/ema.asp)

### Python Libraries

- [yfinance docs](https://github.com/ranaroussi/yfinance)
- [pandas docs](https://pandas.pydata.org/docs/)
- [TA-Lib alternative: pandas-ta](https://github.com/twopirllc/pandas-ta)

### Backtesting

- [Backtrader](https://www.backtrader.com/) - for testing strategies
- [VectorBT](https://vectorbt.dev/) - fast backtesting library

---

## FAQ

**Q: Why only 2 indicators?**
A: Simplicity. RSI + EMA cover the basics (oversold conditions + momentum). More indicators = more complexity for marginal gains.

**Q: Can I add MACD or Bollinger Bands?**
A: Yes! Follow the same pattern:

1. Implement calculation function
2. Add to `generate_signal()`
3. Update signal strength scoring
4. Test with real data

**Q: What if RSI and EMA disagree?**
A: We trust RSI < 30 more for BUY signals (mean reversion). EMA crossovers can be noisy in ranging markets.

**Q: How do I tune the thresholds?**
A: Run historical analysis (see archived docs) and find thresholds that balance signal frequency with accuracy. Start with RSI 30/70 and EMA 12/26 (industry standards).

---

**Version**: 1.0.0
**Last Updated**: 2025-01-20
**Status**: Ready for implementation

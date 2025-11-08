# Data Science Module

Pure Python functions for calculating indicators and generating signals. No database dependencies - works with Polars DataFrames for high performance.

## Structure

```bash
data/
├── indicators/
│   ├── rsi.py           # RSI calculation
│   ├── macd.py          # MACD (optional, not in MVP)
│   └── ema.py           # EMA calculation (add this)
├── signals/
│   ├── signal_generator.py  # Rule-based signal logic
│   └── signal_scorer.py     # Strength calculation
└── utils/
    └── data_validation.py   # Quality checks (Phase 2)
```

## MVP: RSI + EMA Only

Start with just 2 indicators. Add more later when you validate the system works.

### 1. RSI Implementation

**File:** `data/indicators/rsi.py`

```python
import pandas as pd

def calculate_rsi(df: pd.DataFrame, period: int = 14, price_column: str = "close") -> pd.Series:
    """
    Calculate RSI (Relative Strength Index).
    
    Formula:
        1. delta = price changes
        2. gain = positive changes, loss = negative changes (absolute)
        3. avg_gain = EMA of gains, avg_loss = EMA of losses
        4. RS = avg_gain / avg_loss
        5. RSI = 100 - (100 / (1 + RS))
    
    Returns:
        pd.Series: RSI values (0-100)
    """
    # Calculate price changes
    delta = df[price_column].diff()
    
    # Separate gains and losses
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    # Calculate average using EMA (Wilder's smoothing method)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi
```

**Usage:**

```python
import pandas as pd
from data.indicators.rsi import calculate_rsi

# Your OHLCV data
df = pd.DataFrame({
    'close': [100, 102, 101, 105, 107, 103, 108, 106, 110]
})

df['rsi'] = calculate_rsi(df, period=14)
print(df['rsi'].iloc[-1])  # Latest RSI value
```

### 2. EMA Implementation

**File:** `data/indicators/ema.py` (create this)

```python
import polars as pl

def calculate_ema(series: pl.Series, span: int) -> pl.Series:
    """
    Calculate EMA (Exponential Moving Average).
    
    Formula:
        EMA = price.ewm(span=period).mean()
    
    Args:
        df: DataFrame with price data
        period: EMA period (e.g., 12 or 26)
        price_column: Column to use (default: 'close')
    
    Returns:
        pd.Series: EMA values
    """
    return df[price_column].ewm(span=period, adjust=False).mean()


def detect_ema_crossover(ema_12: pl.Series, ema_26: pl.Series) -> tuple[str, bool]:
    """
    Detect EMA crossover (bullish or bearish).
    
    Returns:
        ('bullish' | 'bearish' | 'none', crossover_detected: bool)
    
    Example:
        >>> ema_12 = pl.Series([100, 101, 102, 103])
        >>> ema_26 = pl.Series([102, 102, 102, 102])
        >>> detect_ema_crossover(ema_12, ema_26)
        ('bullish', True)  # EMA-12 crossed above EMA-26
    """
    if len(ema_12) < 2 or len(ema_26) < 2:
        return "none", False
    
    # Current and previous values
    curr_12, curr_26 = ema_12[-1], ema_26[-1]
    prev_12, prev_26 = ema_12[-2], ema_26[-2]
    
    # Bullish crossover: EMA-12 crosses above EMA-26
    if prev_12 <= prev_26 and curr_12 > curr_26:
        return "bullish", True
    
    # Bearish crossover: EMA-12 crosses below EMA-26
    elif prev_12 >= prev_26 and curr_12 < curr_26:
        return "bearish", True
    
    return "none", False
```

### 3. Simple Signal Generation (MVP)

**File:** `data/signals/signal_generator.py`

Replace MACD logic with RSI + EMA:

```python
def generate_signal(rsi: float, ema_12: float, ema_26: float, price: float) -> dict:
    """
    Generate BUY/HOLD signal from RSI and EMA.
    
    MVP Rules:
        BUY:  RSI < 30 (oversold) OR EMA-12 > EMA-26 (bullish)
        HOLD: Otherwise
    
    Returns:
        {
            'signal_type': 'BUY' | 'HOLD',
            'strength': int (0-100),
            'reasoning': List[str],
            'price': float
        }
    """
    signal_type = "HOLD"
    reasoning = []
    strength = 0
    
    # Rule 1: RSI oversold
    if rsi < 30:
        signal_type = "BUY"
        strength = int(100 - rsi * 2)  # Lower RSI = stronger signal
        reasoning.append(f"RSI oversold ({rsi:.1f})")
    
    # Rule 2: EMA bullish alignment
    if ema_12 > ema_26:
        signal_type = "BUY"
        ema_diff = ((ema_12 - ema_26) / ema_26) * 100
        strength = max(strength, min(80, int(ema_diff * 10)))
        reasoning.append(f"EMA-12 above EMA-26 (bullish)")
    
    # Both indicators agree = stronger signal
    if rsi < 30 and ema_12 > ema_26:
        strength = min(95, strength + 20)
        reasoning.append("Both RSI and EMA confirm BUY")
    
    # Default reasoning if HOLD
    if not reasoning:
        reasoning.append("No strong setup detected")
    
    return {
        'signal_type': signal_type,
        'strength': strength,
        'reasoning': reasoning,
        'price': price
    }
```

### 4. Plain English Explanations

**Add to signal_generator.py:**

```python
EXPLANATION_TEMPLATES = {
    "rsi_oversold": "{symbol} is oversold (RSI {rsi:.1f}). Price often bounces back from these levels.",
    "ema_bullish": "{symbol} shows bullish momentum (EMA-12 above EMA-26).",
    "both_confirm": "{symbol} has a strong setup: oversold RSI and bullish EMA alignment.",
}

def generate_explanation(signal: dict, symbol: str, rsi: float) -> str:
    """Generate plain English explanation for email."""
    if "Both RSI and EMA confirm" in signal['reasoning']:
        return EXPLANATION_TEMPLATES["both_confirm"].format(symbol=symbol, rsi=rsi)
    elif "RSI oversold" in signal['reasoning'][0]:
        return EXPLANATION_TEMPLATES["rsi_oversold"].format(symbol=symbol, rsi=rsi)
    elif "EMA-12 above EMA-26" in signal['reasoning'][0]:
        return EXPLANATION_TEMPLATES["ema_bullish"].format(symbol=symbol)
    else:
        return "No strong signal at this time."
```

## Testing Your Indicators

### Quick Test

```python
# test_indicators.py
import polars as pl
from data.indicators.rsi import calculate_rsi
from data.indicators.ema import calculate_ema, detect_ema_crossover
from data.signals.signal_generator import generate_signal

# Sample data
df = pl.DataFrame({
    'close': [100, 102, 101, 105, 107, 103, 108, 106, 110, 109, 112, 115, 114, 116, 118]
})

# Calculate indicators
rsi = calculate_rsi(df, period=14)
ema_12 = calculate_ema(df["close"], span=12)
ema_26 = calculate_ema(df["close"], span=26)

# Get latest values
latest_rsi = rsi[-1]
latest_ema_12 = ema_12[-1]
latest_ema_26 = ema_26[-1]
latest_close = df["close"][-1]

# Generate signal
signal = generate_signal(
    rsi=latest_rsi,
    ema_12=latest_ema_12,
    ema_26=latest_ema_26,
    price=latest_close
)

print(f"Signal: {signal['signal_type']}")
print(f"Strength: {signal['strength']}/100")
print(f"Reasoning: {signal['reasoning']}")
```

### Visual Verification

```python
import matplotlib.pyplot as plt

def plot_indicators(df):
    """Quick visual check of indicators."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Price + EMA
    ax1.plot(df.index, df['close'], label='Price', linewidth=2)
    ax1.plot(df.index, df['ema_12'], label='EMA-12', alpha=0.7)
    ax1.plot(df.index, df['ema_26'], label='EMA-26', alpha=0.7)
    ax1.legend()
    ax1.set_title('Price + EMA')
    
    # RSI
    ax2.plot(df.index, df['rsi'], label='RSI', color='purple')
    ax2.axhline(70, color='r', linestyle='--', label='Overbought')
    ax2.axhline(30, color='g', linestyle='--', label='Oversold')
    ax2.fill_between(df.index, 30, 70, alpha=0.1)
    ax2.legend()
    ax2.set_title('RSI')
    ax2.set_ylim(0, 100)
    
    plt.tight_layout()
    plt.show()

# Use it
plot_indicators(df)
```

## When Indicators Work

### RSI (Best in ranging markets)

- ✅ RSI < 30 → Often bounces back up
- ✅ RSI > 70 → Often pulls back down
- ❌ In strong trends, RSI can stay extreme for long periods

### EMA Crossover (Best in trending markets)

- ✅ EMA-12 > EMA-26 → Bullish momentum
- ✅ EMA-12 < EMA-26 → Bearish momentum
- ❌ In ranging markets, generates many false crossovers

### MVP Strategy (Simple)

Use both indicators together:

- Strong BUY: RSI < 30 AND EMA-12 > EMA-26
- Moderate BUY: Either condition alone
- HOLD: None of the above

## Phase 2: Advanced Features

See `docs/TODOs.md` for backlog:

- **ADX regime detection**: Use ADX to determine trend vs range, then pick RSI or EMA
- **Cooldown enforcement**: Max 1 signal per symbol per 8 hours
- **Strength tuning**: Calibrate thresholds based on historical data
- **More indicators**: MACD, Bollinger Bands (after validating RSI+EMA works)

## Troubleshooting

**RSI is NaN:**

- Need at least `period + 1` bars (15 for RSI-14)
- Check: `df['rsi'].isna().sum()` to count NaN values

**EMA crossover not detecting:**

- Need at least 2 bars to compare current vs previous
- Check: `print(ema_12.iloc[-2:], ema_26.iloc[-2:])`

**Signal strength always 0:**

- Check indicator values: `print(f"RSI: {rsi}, EMA-12: {ema_12}, EMA-26: {ema_26}")`
- Verify conditions are being met

## Next Steps

1. ✅ Implement `calculate_rsi()` in `data/indicators/rsi.py`
2. ✅ Create `data/indicators/ema.py` with `calculate_ema()` and `detect_ema_crossover()`
3. ✅ Update `signal_generator.py` to use RSI + EMA (remove MACD)
4. ✅ Test locally with sample data
5. ✅ Integrate into Prefect flow (see `pipe/README.md`)

Keep it simple, get it working, iterate! 🚀

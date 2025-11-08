# Glossary

Quick reference for key terms used throughout the documentation.

## Trading Terms

**RSI (Relative Strength Index)**: 0-100 oscillator measuring momentum. RSI < 30 indicates oversold conditions (potential bounce), RSI > 70 indicates overbought (potential pullback).

**EMA (Exponential Moving Average)**: Trend-following indicator that weights recent prices more heavily. EMA-12 crossing above EMA-26 signals bullish momentum.

**OHLCV**: Open, High, Low, Close, Volume - the five data points that make up a price bar/candle.

**Signal Strength**: 0-100 confidence score calculated from indicator alignment. Only signals ≥ `SIGNAL_NOTIFY_THRESHOLD` (currently 60) are considered for notifications.

**Mean Reversion**: Trading strategy assuming price returns to average after extreme movements. Works best in ranging markets.

## Signal Terms

**Idempotency**: Prevents duplicate signals when pipeline jobs rerun. Achieved via unique key: `{symbol}:{rule_version}:{timestamp}`.

**Double Opt-In**: Two-step email subscription: 1) Subscribe → 2) Confirm via email link → 3) Receive notifications. Improves deliverability.

**Cooldown** (Future): Time buffer between signals for the same symbol to prevent alert fatigue during choppy sessions. Not yet implemented.

**Regime** (Future): Market context classification—trending (EMA-led) vs. ranging (RSI-led)—used to pick strategies automatically.

## System Terms

**Flow**: Prefect workflow orchestrating data pipeline tasks (fetch → calculate → generate → notify).

**Task**: Unit of work within a flow (e.g., `fetch_market_data`, `send_notifications`).

**Backfill**: Loading multi-year *daily* OHLCV history (up to ~10y) before running nightly automation so indicators and backtests have enough context.

**Daily Bars**: 1-day OHLCV candles fetched from Yahoo Finance. They are the canonical timeframe for the MVP pipeline.

**Fat-Finger** (Future): Detection rule for >5% price spikes/drops that flags bad provider data before indicators are recomputed.

---

**For detailed explanations**, see:

- MVP scope: `docs/MVP.md`
- System architecture: `docs/ARCHITECTURE.md`
- Technical indicators: `docs/resources/TECHNICAL-ANALYSIS.md`

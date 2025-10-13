# Glossary

Quick reference for key terms used throughout the documentation.

## Trading Terms

**RSI (Relative Strength Index)**: 0-100 oscillator measuring momentum. RSI < 30 indicates oversold conditions (potential bounce), RSI > 70 indicates overbought (potential pullback).

**EMA (Exponential Moving Average)**: Trend-following indicator that weights recent prices more heavily. EMA-12 crossing above EMA-26 signals bullish momentum.

**OHLCV**: Open, High, Low, Close, Volume - the five data points that make up a price bar/candle.

**Signal Strength**: 0-100 confidence score calculated from indicator values. Only signals ≥70 trigger email notifications.

**Mean Reversion**: Trading strategy assuming price returns to average after extreme movements. Works best in ranging markets.

## Signal Terms

**Idempotency**: Prevents duplicate signals when pipeline jobs rerun. Achieved via unique key: `{symbol}:{rule_version}:{timestamp}`.

**Double Opt-In**: Two-step email subscription: 1) Subscribe → 2) Confirm via email link → 3) Receive notifications. Improves deliverability.

**Cooldown** (Phase 2): Time between signals for same symbol (e.g., 8 hours). Prevents alert fatigue in choppy markets.

**Regime** (Phase 2): Market context classification - trending (use EMA) or ranging (use RSI). Determined by ADX indicator.

## System Terms

**Flow**: Prefect workflow orchestrating data pipeline tasks (fetch → calculate → generate → notify).

**Task**: Unit of work within a flow (e.g., `fetch_market_data`, `send_notifications`).

**Backfill**: Loading historical data into database before starting live pipeline. MVP uses ~60 days of 15-minute bars.

**15m Bars**: 15-minute price candles (OHLCV data points). Yahoo Finance limit for 15m interval is ~60 days.

**Fat-Finger** (Phase 2): Data error detected by >5% price spike. Flagged as invalid to prevent false signals.

---

**For detailed explanations**, see:
- Technical indicators: `docs/DATA-SCIENCE.md`
- System architecture: `docs/ARCHITECTURE.md`
- MVP scope: `docs/MVP.md`

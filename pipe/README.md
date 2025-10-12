# Prefect Data Pipeline

Automated workflows for fetching market data, calculating indicators, generating signals, and sending notifications.

## Flows

1. **market_data_ingestion** - Fetch OHLCV data from Yahoo Finance
2. **indicator_calculation** - Calculate RSI + MACD indicators
3. **signal_generation** - Generate BUY/SELL/HOLD signals
4. **notification_sender** - Send email alerts for strong signals

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your DATABASE_URL and RESEND_API_KEY

# Log in to Prefect Cloud (optional)
prefect cloud login

# Deploy flows
python schedules.py
```

## Running Flows Manually

```bash
# Test individual flows
python -m flows.market_data_ingestion
python -m flows.indicator_calculation
python -m flows.signal_generation
python -m flows.notification_sender
```

## Schedule

All flows run hourly:

- **00:05** - Market data ingestion
- **00:10** - Indicator calculation
- **00:15** - Signal generation
- **00:20** - Notification sender

## Development

To add a new flow:

1. Create flow file in `flows/`
2. Add schedule in `schedules.py`
3. Deploy with `python schedules.py`

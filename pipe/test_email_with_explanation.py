#!/usr/bin/env python3
"""Test email sending with explanation"""

from tasks.email_sending import send_signal_notification

# Test signal with explanation
signal = {
    "id": "3c20256d-b4c6-4c11-9b61-71ce5502bb33",
    "symbol": "BTC-USD",
    "signal_type": "BUY",
    "strength": 85.5,
    "reasoning": [
        "MACD histogram showing strong bullish momentum",
        "EMA fast crossed above EMA slow",
        "RSI at 38 indicates room to run"
    ],
    "price": 102500.00,
    "at": "2025-11-12T23:21:00+00:00",
    "explanation": "Bitcoin is showing strong bullish momentum with a MACD histogram surge indicating growing buying pressure. The fast exponential moving average has crossed above the slow EMA, a classic technical signal that suggests the start of an uptrend. This crossover pattern historically precedes significant price appreciation.\n\nWith the RSI indicator at 38, Bitcoin is not yet overbought, meaning there is substantial room for the rally to continue before hitting resistance levels. This combination of momentum indicators and positioning suggests a favorable entry point for long positions, though investors should always manage risk appropriately with stop-loss orders."
}

print("Testing email with explanation...")
print(f"Signal explanation length: {len(signal['explanation'])} chars")
print(f"Signal explanation preview: {signal['explanation'][:100]}...")

result = send_signal_notification(
    to_email="diegovfeder@gmail.com",
    signal=signal,
    unsubscribe_token="test-token-123"
)

print(f"\nResult: {'✅ Success' if result else '❌ Failed'}")

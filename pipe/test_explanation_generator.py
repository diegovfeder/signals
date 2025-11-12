#!/usr/bin/env python3
"""
Test script for LLM explanation generator.

Usage:
    # Test with DeepSeek (free/cheap)
    DEEPSEEK_API_KEY=your_key LLM_PROVIDER=deepseek python test_explanation_generator.py

    # Test with OpenRouter (free tier)
    OPENROUTER_API_KEY=your_key LLM_PROVIDER=openrouter python test_explanation_generator.py

    # Test with OpenAI
    OPENAI_API_KEY=your_key LLM_PROVIDER=openai python test_explanation_generator.py
"""

from lib.explanation_generator import ExplanationGenerator, generate_explanation

# Sample signal data (BTC-USD BUY signal)
btc_buy_signal = {
    "symbol": "BTC-USD",
    "signal_type": "BUY",
    "strength": 85.5,
    "reasoning": [
        "MACD histogram 0.52 >= 0.5",
        "EMA fast above EMA slow (bullish momentum)",
        "RSI 38.2 still below 40 (room to run)",
    ],
    "price": 43250.75,
    "indicators": {
        "rsi": 38.2,
        "ema_fast": 43100.50,
        "ema_slow": 42800.25,
        "macd_hist": 0.52,
    },
}

# Sample signal data (AAPL SELL signal)
aapl_sell_signal = {
    "symbol": "AAPL",
    "signal_type": "SELL",
    "strength": 72.3,
    "reasoning": [
        "RSI 71.5 > 70 (overbought)",
        "Price $185.50 > EMA26 $182.30 by 1.7%",
        "Mean reversion expected",
    ],
    "price": 185.50,
    "indicators": {
        "rsi": 71.5,
        "ema_fast": 184.20,
        "ema_slow": 182.30,
        "macd_hist": -0.15,
    },
}

# Sample HOLD signal
hold_signal = {
    "symbol": "AAPL",
    "signal_type": "HOLD",
    "strength": 45.0,
    "reasoning": ["Market conditions neutral; holding position"],
    "price": 178.25,
    "indicators": {
        "rsi": 52.3,
        "ema_fast": 178.00,
        "ema_slow": 177.80,
        "macd_hist": 0.05,
    },
}


def test_explanation_generator():
    """Test the explanation generator with sample signals."""

    print("=" * 80)
    print("Testing LLM Explanation Generator")
    print("=" * 80)

    try:
        generator = ExplanationGenerator()
        print(f"\n✓ Initialized {generator.provider.value} provider")
        print(f"  Model: {generator.model}")
        print(f"  Timeout: {generator.timeout}s")
    except Exception as e:
        print(f"\n✗ Failed to initialize: {e}")
        print("\nMake sure you have set the appropriate API key:")
        print("  - DEEPSEEK_API_KEY for DeepSeek")
        print("  - OPENROUTER_API_KEY for OpenRouter")
        print("  - OPENAI_API_KEY for OpenAI")
        print("  - ANTHROPIC_API_KEY for Claude")
        return

    # Test 1: BTC BUY signal
    print("\n" + "-" * 80)
    print("Test 1: BTC-USD BUY Signal (High Confidence)")
    print("-" * 80)
    print(f"Signal: {btc_buy_signal['signal_type']} @ ${btc_buy_signal['price']:,.2f}")
    print(f"Strength: {btc_buy_signal['strength']}/100")
    print(f"Reasoning: {', '.join(btc_buy_signal['reasoning'])}")

    print("\n🤖 Generating explanation...")
    explanation = generator.generate(btc_buy_signal)

    if explanation:
        print("\n✅ Generated Explanation:")
        print("-" * 80)
        print(explanation)
        print("-" * 80)
        word_count = len(explanation.split())
        print(f"\nWord count: {word_count}")
    else:
        print("\n❌ Failed to generate explanation")

    # Test 2: AAPL SELL signal
    print("\n" + "-" * 80)
    print("Test 2: AAPL SELL Signal (Moderate Confidence)")
    print("-" * 80)
    print(
        f"Signal: {aapl_sell_signal['signal_type']} @ ${aapl_sell_signal['price']:,.2f}"
    )
    print(f"Strength: {aapl_sell_signal['strength']}/100")
    print(f"Reasoning: {', '.join(aapl_sell_signal['reasoning'])}")

    print("\n🤖 Generating explanation...")
    explanation = generator.generate(aapl_sell_signal)

    if explanation:
        print("\n✅ Generated Explanation:")
        print("-" * 80)
        print(explanation)
        print("-" * 80)
        word_count = len(explanation.split())
        print(f"\nWord count: {word_count}")
    else:
        print("\n❌ Failed to generate explanation")

    # Test 3: HOLD signal (should be brief)
    print("\n" + "-" * 80)
    print("Test 3: AAPL HOLD Signal (Low Confidence)")
    print("-" * 80)
    print(f"Signal: {hold_signal['signal_type']} @ ${hold_signal['price']:,.2f}")
    print(f"Strength: {hold_signal['strength']}/100")
    print(f"Reasoning: {', '.join(hold_signal['reasoning'])}")

    print("\n🤖 Generating explanation...")
    explanation = generator.generate(hold_signal)

    if explanation:
        print("\n✅ Generated Explanation:")
        print("-" * 80)
        print(explanation)
        print("-" * 80)
        word_count = len(explanation.split())
        print(f"\nWord count: {word_count}")
    else:
        print("\n❌ Failed to generate explanation")

    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)


def test_convenience_function():
    """Test the convenience generate_explanation() function."""

    print("\n" + "=" * 80)
    print("Testing Convenience Function")
    print("=" * 80)

    print("\nGenerating explanation using generate_explanation()...")
    explanation = generate_explanation(btc_buy_signal)

    if explanation:
        print("\n✅ Success!")
        print(explanation[:100] + "...")
    else:
        print("\n❌ Failed (check API key and provider settings)")


if __name__ == "__main__":
    test_explanation_generator()
    test_convenience_function()

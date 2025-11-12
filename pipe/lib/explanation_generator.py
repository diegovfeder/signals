"""
LLM-powered explanation generator for trading signals.

Converts technical signal data into natural language explanations for users.
Supports multiple LLM providers: DeepSeek, OpenRouter (Kiwi), OpenAI, Claude.
"""

from __future__ import annotations

import os
from typing import Dict, Optional
from enum import Enum

import httpx
from dotenv import load_dotenv

load_dotenv()


class LLMProvider(str, Enum):
    """Supported LLM providers for explanation generation."""

    DEEPSEEK = "deepseek"  # Free/cheap option
    OPENROUTER = "openrouter"  # Access to many models including free ones
    OPENAI = "openai"  # Paid, high quality
    CLAUDE = "claude"  # Paid, high quality


class ExplanationGenerator:
    """
    Generate natural language explanations for trading signals using LLMs.

    Environment variables:
        LLM_PROVIDER: Provider to use (deepseek, openrouter, openai, claude)
        DEEPSEEK_API_KEY: DeepSeek API key
        OPENROUTER_API_KEY: OpenRouter API key
        OPENAI_API_KEY: OpenAI API key
        ANTHROPIC_API_KEY: Claude API key
        LLM_MODEL: Optional model override (e.g., "deepseek-chat", "gpt-4o-mini")
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        timeout: int = 30,
    ):
        self.provider = LLMProvider(provider or os.getenv("LLM_PROVIDER", "deepseek"))
        self.timeout = timeout

        # Model selection with sensible defaults
        self.model = model or self._get_default_model()

        # Get API key for selected provider
        self.api_key = self._get_api_key()
        if not self.api_key:
            raise RuntimeError(
                f"No API key found for provider '{self.provider}'. "
                f"Set {self._get_env_key_name()} environment variable."
            )

    def _get_default_model(self) -> str:
        """Get default model for the selected provider."""
        defaults = {
            LLMProvider.DEEPSEEK: "deepseek-chat",
            LLMProvider.OPENROUTER: "qwen/qwq-32b-preview",  # Free tier
            LLMProvider.OPENAI: "gpt-4o-mini",
            LLMProvider.CLAUDE: "claude-3-5-haiku-20241022",
        }
        return os.getenv("LLM_MODEL", defaults[self.provider])

    def _get_env_key_name(self) -> str:
        """Get environment variable name for API key."""
        key_names = {
            LLMProvider.DEEPSEEK: "DEEPSEEK_API_KEY",
            LLMProvider.OPENROUTER: "OPENROUTER_API_KEY",
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.CLAUDE: "ANTHROPIC_API_KEY",
        }
        return key_names[self.provider]

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment."""
        return os.getenv(self._get_env_key_name())

    def _get_api_endpoint(self) -> str:
        """Get API endpoint URL for the provider."""
        endpoints = {
            LLMProvider.DEEPSEEK: "https://api.deepseek.com/chat/completions",  # Native format per docs
            LLMProvider.OPENROUTER: "https://openrouter.ai/api/v1/chat/completions",
            LLMProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
            LLMProvider.CLAUDE: "https://api.anthropic.com/v1/messages",
        }
        return endpoints[self.provider]

    def _build_prompt(self, signal_data: Dict) -> str:
        """
        Build the system prompt for explanation generation.

        Args:
            signal_data: Signal information (symbol, type, strength, reasoning, indicators)

        Returns:
            Formatted prompt string
        """
        symbol = signal_data.get("symbol", "ASSET")
        signal_type = signal_data.get("signal_type", "HOLD")
        strength = signal_data.get("strength", 0)
        reasoning = signal_data.get("reasoning", [])

        # Extract indicator values if available
        indicators = signal_data.get("indicators", {})
        rsi = indicators.get("rsi")
        ema_fast = indicators.get("ema_fast")
        ema_slow = indicators.get("ema_slow")
        macd_hist = indicators.get("macd_hist")
        price = signal_data.get("price")

        # Build context about indicators
        indicator_context = []
        if rsi is not None:
            indicator_context.append(f"RSI: {rsi:.1f}")
        if ema_fast is not None and ema_slow is not None:
            indicator_context.append(f"EMA Fast/Slow: {ema_fast:.2f}/{ema_slow:.2f}")
        if macd_hist is not None:
            indicator_context.append(f"MACD Histogram: {macd_hist:.4f}")
        if price is not None:
            indicator_context.append(f"Current Price: ${price:,.2f}")

        indicator_text = (
            "\n".join(indicator_context)
            if indicator_context
            else "No indicator data available"
        )
        reasoning_text = (
            "\n".join(f"- {r}" for r in reasoning)
            if reasoning
            else "No reasoning provided"
        )

        prompt = f"""You are a professional financial analyst writing a brief market analysis for retail investors.

Signal Details:
- Asset: {symbol}
- Signal Type: {signal_type}
- Confidence: {strength}/100

Technical Indicators:
{indicator_text}

Key Factors:
{reasoning_text}

Your task:
Write a clear, concise explanation (2 paragraphs max, ~100-150 words total) that:
1. Explains what this {signal_type} signal means in plain English
2. Describes the market conditions that led to this signal
3. Provides context about what investors should understand

Tone: Professional but accessible. Avoid jargon. Be direct and actionable.
Format: Two paragraphs, no bullet points, no markdown formatting.

Write the analysis now:"""

        return prompt

    def _call_openai_compatible(self, prompt: str) -> Optional[str]:
        """
        Call OpenAI-compatible API (DeepSeek, OpenRouter, OpenAI).

        Args:
            prompt: The prompt to send

        Returns:
            Generated explanation or None if failed
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # OpenRouter needs extra headers
        if self.provider == LLMProvider.OPENROUTER:
            headers["HTTP-Referer"] = os.getenv(
                "APP_BASE_URL", "https://signals-dvf.vercel.app"
            )
            headers["X-Title"] = "Signals Trading Platform"

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300,
            "temperature": 0.7,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self._get_api_endpoint(),
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                return data["choices"][0]["message"]["content"].strip()

        except Exception as e:
            print(f"[explanation] LLM API call failed ({self.provider}): {e}")
            return None

    def _call_claude(self, prompt: str) -> Optional[str]:
        """
        Call Claude API (different format than OpenAI).

        Args:
            prompt: The prompt to send

        Returns:
            Generated explanation or None if failed
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "max_tokens": 300,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self._get_api_endpoint(),
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()

                data = response.json()
                return data["content"][0]["text"].strip()

        except Exception as e:
            print(f"[explanation] Claude API call failed: {e}")
            return None

    def generate(self, signal_data: Dict) -> Optional[str]:
        """
        Generate natural language explanation for a trading signal.

        Args:
            signal_data: Dictionary containing:
                - symbol: Asset symbol (e.g., "BTC-USD", "AAPL")
                - signal_type: "BUY", "SELL", or "HOLD"
                - strength: Confidence score (0-100)
                - reasoning: List of reasoning points
                - indicators: Dict of indicator values (rsi, ema_fast, ema_slow, macd_hist)
                - price: Current price

        Returns:
            Natural language explanation (2 paragraphs) or None if generation failed
        """
        prompt = self._build_prompt(signal_data)

        if self.provider == LLMProvider.CLAUDE:
            return self._call_claude(prompt)
        else:
            return self._call_openai_compatible(prompt)


def generate_explanation(signal_data: Dict) -> Optional[str]:
    """
    Convenience function to generate explanation with default settings.

    Args:
        signal_data: Signal information dict

    Returns:
        Generated explanation or None
    """
    try:
        generator = ExplanationGenerator()
        return generator.generate(signal_data)
    except Exception as e:
        print(f"[explanation] Failed to generate explanation: {e}")
        return None

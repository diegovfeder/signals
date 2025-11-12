# LLM-Powered Signal Explanations

Generate natural language explanations for trading signals using various LLM providers.

## Overview

The explanation generator converts technical signal data into readable 2-paragraph analyses for your users. It supports multiple providers with free and paid options.

## Supported Providers

### 1. DeepSeek (Recommended - Cheap/Free)
- **Cost**: Very cheap (~$0.14 per 1M input tokens, $0.28 per 1M output tokens)
- **Model**: `deepseek-chat`
- **Quality**: Good for technical analysis
- **Setup**: Get API key from https://platform.deepseek.com/

```bash
export DEEPSEEK_API_KEY="sk-..."
export LLM_PROVIDER="deepseek"
```

### 2. OpenRouter (Free Tier Available)
- **Cost**: Free tier available (Qwen models)
- **Model**: `qwen/qwq-32b-preview` (default)
- **Quality**: Good, supports many models
- **Setup**: Get API key from https://openrouter.ai/

```bash
export OPENROUTER_API_KEY="sk-or-..."
export LLM_PROVIDER="openrouter"
export LLM_MODEL="qwen/qwq-32b-preview"  # or any OpenRouter model
```

### 3. OpenAI
- **Cost**: Paid (~$0.15 per 1M input tokens for gpt-4o-mini)
- **Model**: `gpt-4o-mini` (default)
- **Quality**: Excellent
- **Setup**: Get API key from https://platform.openai.com/

```bash
export OPENAI_API_KEY="sk-..."
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"  # or gpt-4o, gpt-3.5-turbo
```

### 4. Claude (Anthropic)
- **Cost**: Paid (~$0.80 per 1M input tokens for Haiku)
- **Model**: `claude-3-5-haiku-20241022` (default)
- **Quality**: Excellent
- **Setup**: Get API key from https://console.anthropic.com/

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export LLM_PROVIDER="claude"
export LLM_MODEL="claude-3-5-haiku-20241022"  # or claude-3-5-sonnet-20241022
```

## Enabling in Pipeline

### Environment Variables

```bash
# Required: Enable LLM explanations
export ENABLE_LLM_EXPLANATIONS="true"

# Required: Choose provider and set API key
export LLM_PROVIDER="deepseek"  # or openrouter, openai, claude
export DEEPSEEK_API_KEY="sk-..."

# Optional: Override default model
export LLM_MODEL="deepseek-chat"
```

### Running Flows with Explanations

```bash
# Run signal analyzer with explanations
cd pipe
ENABLE_LLM_EXPLANATIONS=true \
DEEPSEEK_API_KEY=your_key \
LLM_PROVIDER=deepseek \
uv run python -m pipe.flows.signal_analyzer --symbols AAPL,BTC-USD
```

## Testing

Test the explanation generator before running in production:

```bash
cd pipe

# Test with DeepSeek
DEEPSEEK_API_KEY=your_key \
LLM_PROVIDER=deepseek \
uv run python test_explanation_generator.py

# Test with OpenRouter
OPENROUTER_API_KEY=your_key \
LLM_PROVIDER=openrouter \
uv run python test_explanation_generator.py
```

## How It Works

1. **Signal Generated**: Strategy creates signal with reasoning points
2. **LLM Called** (if enabled): Sends technical data to LLM with prompt
3. **Explanation Formatted**: LLM generates 2-paragraph natural language explanation
4. **Stored in DB**: Explanation saved in `signals.explanation` column
5. **Emailed**: Explanation appears in signal notification emails (optional section)

## Email Template Integration

The explanation appears as an optional "Analysis" section in signal notification emails:

- **Without explanation**: Email shows "Key Factors" (bullet points) only
- **With explanation**: Email adds highlighted "Analysis" section with natural language review

## Cost Estimates

Assuming ~400 tokens per explanation (input + output):

| Provider | Cost per Signal | Cost per 1000 Signals |
|----------|----------------|---------------------|
| DeepSeek | ~$0.0001 | ~$0.10 |
| OpenRouter (free) | $0 | $0 |
| OpenAI (gpt-4o-mini) | ~$0.0001 | ~$0.10 |
| Claude (Haiku) | ~$0.0004 | ~$0.40 |

**Recommendation**: Start with DeepSeek or OpenRouter free tier for testing, then switch to OpenAI/Claude if you need higher quality.

## Example Output

**Input** (BTC-USD BUY signal):
- MACD histogram 0.52 >= 0.5
- EMA fast above EMA slow (bullish momentum)
- RSI 38.2 still below 40 (room to run)

**Generated Explanation**:
> Bitcoin is showing strong bullish momentum with MACD histogram at 0.52. The fast EMA has crossed above the slow EMA, indicating upward price pressure. This setup historically precedes significant price increases.
>
> With RSI at 38.2, there's still room for the rally to continue before reaching overbought territory. Consider this a favorable entry point for long positions, though always manage risk appropriately.

## Troubleshooting

### "No API key found for provider"
- Ensure you've set the correct environment variable for your chosen provider
- Check that the variable is exported in your shell session

### "LLM API call failed"
- Check your API key is valid
- Verify you have credits/quota remaining
- Test your API key directly with the provider's playground

### Explanations not appearing in emails
- Confirm `ENABLE_LLM_EXPLANATIONS=true` is set when running signal_analyzer
- Check database: `SELECT explanation FROM signals WHERE explanation IS NOT NULL LIMIT 5;`
- Verify email templates are published (they include EXPLANATION_HTML/EXPLANATION_TEXT variables)

### Slow generation
- DeepSeek/OpenRouter can be slower than OpenAI
- Consider increasing timeout: Edit `ExplanationGenerator(timeout=60)`
- Run signal_analyzer less frequently (current: nightly at 22:15 UTC)

## Disabling Explanations

To disable LLM explanations:

```bash
# Don't set ENABLE_LLM_EXPLANATIONS, or set it to false
export ENABLE_LLM_EXPLANATIONS="false"

# Or remove the variable entirely
unset ENABLE_LLM_EXPLANATIONS
```

Signals will still be generated, just without the explanation field.

## Future Enhancements

- [ ] Add caching to avoid regenerating explanations for similar signals
- [ ] Support custom prompts per symbol/strategy
- [ ] Add explanation quality scoring
- [ ] Multi-language support (Portuguese, Spanish, etc.)
- [ ] Retry logic with fallback providers

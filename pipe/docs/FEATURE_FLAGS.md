# Feature Flags & PostHog Integration

Centralized notes for working with `pipe/lib/posthog_client.py`, the helper that powers feature flag checks (`is_feature_enabled`) and analytics events (`capture_event`).

## Overview

1. **PostHog first** – Flags live in PostHog and are referenced with kebab-case keys (e.g., `llm-signal-explanations`). That key is what you toggle in the PostHog UI to roll a feature out by symbol/cohort without redeploying.
2. **Env fallback** – When PostHog is unreachable or the SDK is not configured, `is_feature_enabled` automatically falls back to an environment variable (currently `ENABLE_LLM_EXPLANATIONS`). This keeps nightly flows deterministic.
3. **Shared client** – `pipe/lib/posthog_client.py` lazy-loads the PostHog SDK once per process and exposes `is_feature_enabled`, `capture_event`, and `shutdown`.

## Configuration

| Variable | Purpose | Notes |
| --- | --- | --- |
| `POSTHOG_PROJECT_API_KEY` | Required to talk to PostHog. | Without it, all flags will be resolved via the env fallback. |
| `POSTHOG_HOST` | Override for EU/US instances. Defaults to `https://us.i.posthog.com`. | Optional. |
| `POSTHOG_DEBUG` | Set to `"true"` to enable verbose SDK logging. | Optional. |
| `ENABLE_LLM_EXPLANATIONS` | Boolean fallback used when PostHog is unavailable. | Uppercase on purpose because it is an env var, not the PostHog flag key. |

Set these in `pipe/.env` (or root `.env`) so Prefect flows and local runs share the same behavior:

```bash
POSTHOG_PROJECT_API_KEY="phc_xxx"
POSTHOG_HOST="https://us.i.posthog.com" # optional
POSTHOG_DEBUG="false"
ENABLE_LLM_EXPLANATIONS="true"
```

## How `is_feature_enabled` Works

File: `pipe/lib/posthog_client.py`

1. `_get_posthog_client()` lazily instantiates the SDK using the env vars above.
2. `is_feature_enabled(...)` delegates to `posthog.feature_enabled` using the provided `flag_key`, `distinct_id`, `person_properties`, and `groups`.
3. If PostHog cannot be initialized or a runtime error occurs, the helper logs the failure and returns the value of `ENABLE_LLM_EXPLANATIONS` (default `false`).

### Naming conventions

- **PostHog**: use kebab-case keys (`llm-signal-explanations`). These keys must match what you configure inside the PostHog feature flag UI.
- **Env fallback**: use SCREAMING_SNAKE_CASE (`ENABLE_LLM_EXPLANATIONS`). This is intentionally different so it is obvious when a value is being injected via environment instead of the remote flag.

## Example Usage (`pipe/tasks/email_sending.py`)

```python
from ..lib.posthog_client import is_feature_enabled, capture_event

symbol = signal.get("symbol", "unknown")
if not is_feature_enabled(
    flag_key="llm-signal-explanations",
    distinct_id=symbol,
    groups={"symbol": symbol},
):
    return ""  # skip LLM work when flag is off

explanation = generate_explanation(signal_payload)
if explanation:
    capture_event(
        distinct_id=symbol,
        event_name="llm_explanation_generated",
        properties={...},
        groups={"symbol": symbol},
    )
```

Key takeaways:

- `flag_key` stays kebab-case because it references the PostHog flag.
- The helper already prints the resolved value and falls back to `ENABLE_LLM_EXPLANATIONS` when PostHog is down.
- Use group targeting (`groups={"symbol": symbol}`) so we can dark-launch features by symbol, exchange, etc.

## Adding New Flags

1. **Create flag in PostHog** – Name it in kebab-case and configure default rules.
2. **Add optional fallback** – If you need deterministic behavior without PostHog, introduce an env var (e.g., `ENABLE_<NAME>`) and use it in the fallback branch of `is_feature_enabled`. Keep naming consistent.
3. **Instrument code** – Call `is_feature_enabled` near the expensive work and gate the functionality.
4. **Capture telemetry** – Use `capture_event` to log flag-driven flows (e.g., when a feature generates an LLM explanation).
5. **Document the flag** – Update this doc with owner, usage, and rollout expectations.

## Testing & Troubleshooting

- **Local without PostHog**: Leave `POSTHOG_PROJECT_API_KEY` unset and flip `ENABLE_LLM_EXPLANATIONS=true` to simulate the “flag on” state. Set it to `false` to simulate “flag off”.
- **Runtime logs**: `is_feature_enabled` prints `[posthog] Feature '<flag>' for '<distinct_id>': <bool>` when PostHog is active or `[posthog] PostHog unavailable…` when falling back.
- **Prefect flows**: When running `notification_dispatcher`, combine `ENABLE_LLM_EXPLANATIONS=true` with the `--window-minutes` override to test email backfills end-to-end.
- **Graceful shutdown**: Long-running workers can call `pipe.lib.posthog_client.shutdown()` on exit to flush buffered analytics (not required for Prefect’s short-lived tasks).

## Current Flags

| Flag | Fallback Env | Purpose | Usage |
| --- | --- | --- | --- |
| `llm-signal-explanations` | `ENABLE_LLM_EXPLANATIONS` | Controls whether we (re)generate LLM-based explanations during email sends and other flows. | `_maybe_backfill_explanation` in `pipe/tasks/email_sending.py`, future strategy-level consumers. |

Update this table whenever new feature flags are introduced.

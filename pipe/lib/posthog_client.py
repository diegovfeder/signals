"""
PostHog client for feature flags and analytics.

Provides centralized PostHog initialization and feature flag checking.
"""

from __future__ import annotations

import os
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Lazy import to avoid initialization issues
_posthog_client = None


def _get_posthog_client():
    """Get or initialize the PostHog client."""
    global _posthog_client

    if _posthog_client is not None:
        return _posthog_client

    api_key = os.getenv("POSTHOG_PROJECT_API_KEY")
    if not api_key:
        print("[posthog] No API key configured, feature flags disabled")
        return None

    try:
        import posthog

        posthog.project_api_key = api_key
        posthog.host = os.getenv("POSTHOG_HOST", "https://us.i.posthog.com")

        # Disable verbose debug logging
        posthog.debug = os.getenv("POSTHOG_DEBUG", "false").lower() == "true"

        _posthog_client = posthog
        print(f"[posthog] Initialized with host: {posthog.host}")
        return _posthog_client
    except Exception as exc:
        print(f"[posthog] Failed to initialize: {exc}")
        return None


def is_feature_enabled(
    flag_key: str,
    distinct_id: str,
    person_properties: Optional[dict] = None,
    groups: Optional[dict] = None,
    group_properties: Optional[dict] = None,
    only_evaluate_locally: bool = False,
    send_feature_flag_events: bool = True,
) -> bool:
    """
    Check if a feature flag is enabled for the given user/context.

    Args:
        flag_key: Feature flag key (e.g., "llm-signal-explanations")
        distinct_id: Unique identifier for the context (e.g., signal symbol)
        person_properties: Additional properties for targeting (optional)
        groups: Group identifiers for group-based flags (optional)
        group_properties: Properties for the groups (optional)
        only_evaluate_locally: If True, only use locally cached flags
        send_feature_flag_events: If True, send events to PostHog for flag evaluation

    Returns:
        True if feature is enabled, False otherwise
    """
    client = _get_posthog_client()

    if client is None:
        # Fallback to ENABLE_LLM_EXPLANATIONS env var
        fallback = os.getenv("ENABLE_LLM_EXPLANATIONS", "false").lower() == "true"
        print(
            f"[posthog] PostHog unavailable, using fallback for '{flag_key}': {fallback}"
        )
        return fallback

    try:
        is_enabled = client.feature_enabled(
            flag_key,
            distinct_id,
            person_properties=person_properties,
            groups=groups,
            group_properties=group_properties,
            only_evaluate_locally=only_evaluate_locally,
            send_feature_flag_events=send_feature_flag_events,
        )

        print(f"[posthog] Feature '{flag_key}' for '{distinct_id}': {is_enabled}")
        return is_enabled
    except Exception as exc:
        print(f"[posthog] Error checking feature '{flag_key}': {exc}")
        # Fallback on error
        fallback = os.getenv("ENABLE_LLM_EXPLANATIONS", "false").lower() == "true"
        print(f"[posthog] Using fallback: {fallback}")
        return fallback


def capture_event(
    distinct_id: str,
    event_name: str,
    properties: Optional[dict] = None,
    groups: Optional[dict] = None,
    group_properties: Optional[dict] = None,
) -> None:
    """
    Capture an analytics event in PostHog.

    Args:
        distinct_id: Unique identifier for the user/context
        event_name: Name of the event (e.g., "llm_explanation_generated")
        properties: Event properties (optional)
        groups: Group identifiers (optional)
        group_properties: Properties for the groups (optional)
    """
    client = _get_posthog_client()

    if client is None:
        print(f"[posthog] PostHog unavailable, skipping event '{event_name}'")
        return

    try:
        client.capture(
            distinct_id,
            event_name,
            properties=properties,
            groups=groups,
            group_properties=group_properties,
        )
        print(f"[posthog] Captured event '{event_name}' for '{distinct_id}'")
    except Exception as exc:
        print(f"[posthog] Error capturing event '{event_name}': {exc}")


def shutdown() -> None:
    """Flush and shutdown the PostHog client."""
    global _posthog_client

    if _posthog_client is not None:
        try:
            _posthog_client.flush()
            print("[posthog] Client flushed and shut down")
        except Exception as exc:
            print(f"[posthog] Error during shutdown: {exc}")
        finally:
            _posthog_client = None

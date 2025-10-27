"""Common runtime settings with environment overrides."""

from __future__ import annotations

import os


def _get_float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"Invalid float for {name}: {value}")


def signal_notify_threshold(default: float = 60.0) -> float:
    """Return the minimum strength required to notify users."""
    return _get_float_env("SIGNAL_NOTIFY_THRESHOLD", default)

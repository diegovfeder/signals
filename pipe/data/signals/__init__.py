"""
Signal Generation Module

Rule-based trading signal generation from technical indicators.
"""

from .signal_generator import generate_signal
from .signal_scorer import calculate_signal_strength

__all__ = ["generate_signal", "calculate_signal_strength"]

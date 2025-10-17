"""
Data Validation Utilities

Quality checks for market data before processing.
"""

import pandas as pd
from typing import List, Dict, Any


def validate_ohlcv_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate OHLCV data quality.

    Checks:
        - Required columns present
        - No missing values in critical columns
        - OHLC relationships valid (high >= low, etc.)
        - Volume is non-negative
        - Timestamps are sorted

    Args:
        df: DataFrame with OHLCV data

    Returns:
        dict: {
            'is_valid': bool,
            'errors': List[str],
            'warnings': List[str]
        }

    Example:
        >>> df = pd.DataFrame({...})
        >>> result = validate_ohlcv_data(df)
        >>> if not result['is_valid']:
        ...     print(result['errors'])
    """
    errors = []
    warnings = []

    # TODO: Implement validation checks
    # 1. Check required columns exist
    # 2. Check for missing values
    # 3. Validate OHLC relationships (high >= low, etc.)
    # 4. Check volume is non-negative
    # 5. Check timestamps are sorted and unique

    required_columns = ['open', 'high', 'low', 'close', 'volume', 'timestamp']

    return {
        'is_valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }


def check_missing_values(df: pd.DataFrame) -> List[str]:
    """
    Check for missing values in critical columns.

    Returns:
        List of error messages if missing values found
    """
    errors = []

    critical_columns = ['open', 'high', 'low', 'close', 'volume']
    for col in critical_columns:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            if missing_count > 0:
                errors.append(f"Column '{col}' has {missing_count} missing values")

    return errors


def check_ohlc_relationships(df: pd.DataFrame) -> List[str]:
    """
    Validate OHLC price relationships.

    Rules:
        - high >= open, close, low
        - low <= open, close, high
        - All prices > 0

    Returns:
        List of error messages if relationships violated
    """
    errors = []

    # TODO: Implement OHLC relationship checks

    return errors

"""
Conversion Helper Functions
==========================

Centralized data conversion utilities for the FinanceHub application.
Consolidated from conversion_ops and conversion_utils modules.
"""

from __future__ import annotations

import logging
import math
import re
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

DEFAULT_NA = "N/A"


# --- Conversion Operations Section ---


def _clean_value(value: Any, *, context: str = "") -> Any | None:
    """
    Cleans and validates an input value. Removes placeholder values like None, NaN,
    Inf, and common placeholder strings. Returns a stripped string if the input is a string.
    """
    if value is None or pd.isna(value):
        return None

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None
        return value

    if isinstance(value, str):
        stripped_value = value.strip()
        if not stripped_value:
            return None

        placeholder_strings = {
            "none",
            "na",
            "n/a",
            "-",
            "",
            "#n/a",
            "null",
            "nan",
            "nat",
            "undefined",
            "nil",
            "(blank)",
            "<na>",
        }
        if stripped_value.lower() in placeholder_strings:
            return None

        return stripped_value

    return value


def safe_format_value(
    value: Any,
    *,
    prefix: str = "",
    suffix: str = "",
    decimals: int | None = None,
    multiplier: float = 1.0,
    na_value: str = DEFAULT_NA,
) -> str:
    """
    Safely formats a value into a string with various options, returning a
    fallback value if the input cannot be processed.
    """
    cleaned = _clean_value(value)
    if cleaned is None:
        return na_value

    try:
        if isinstance(cleaned, (int, float)):
            numeric_value = float(cleaned) * multiplier
            if decimals is not None:
                formatted = f"{numeric_value:.{decimals}f}"
            else:
                formatted = str(numeric_value)
        elif isinstance(cleaned, str):
            # Try to convert string to number first
            try:
                numeric_value = float(cleaned.replace(",", "")) * multiplier
                if decimals is not None:
                    formatted = f"{numeric_value:.{decimals}f}"
                else:
                    formatted = str(numeric_value)
            except (ValueError, TypeError):
                formatted = str(cleaned)
        else:
            formatted = str(cleaned)

        return f"{prefix}{formatted}{suffix}"

    except Exception as e:
        logger.warning(f"Error formatting value {value}: {e}")
        return na_value


# --- Conversion Utilities Section ---


def parse_percentage(value: Any) -> float | None:
    """
    Parses a percentage value from various formats (e.g., "5.2%", "5.2", "0.052").
    Returns the percentage as a decimal (e.g., 0.052 for 5.2%).
    """
    if value is None:
        return None

    try:
        if isinstance(value, (int, float)):
            # If it's already a number, assume it's a percentage
            return float(value) / 100.0

        if isinstance(value, str):
            # Remove percentage sign and whitespace
            cleaned = value.strip().replace("%", "")

            # Handle negative percentages
            is_negative = cleaned.startswith("-")
            if is_negative:
                cleaned = cleaned[1:]

            # Parse the number
            numeric_value = float(cleaned)
            if is_negative:
                numeric_value = -numeric_value

            # If the original string had a % sign, it's already a percentage
            if "%" in value:
                return numeric_value / 100.0
            else:
                # If no % sign, assume it's already a decimal
                return numeric_value

        return None

    except (ValueError, TypeError):
        logger.warning(f"Could not parse percentage from: {value}")
        return None


def parse_currency(value: Any) -> float | None:
    """
    Parses a currency value, removing currency symbols and formatting.
    """
    if value is None:
        return None

    try:
        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            # Remove common currency symbols and formatting
            cleaned = re.sub(r"[$€£¥₹,\s]", "", value.strip())

            # Handle negative values
            is_negative = cleaned.startswith("-")
            if is_negative:
                cleaned = cleaned[1:]

            numeric_value = float(cleaned)
            if is_negative:
                numeric_value = -numeric_value

            return numeric_value

        return None

    except (ValueError, TypeError):
        logger.warning(f"Could not parse currency from: {value}")
        return None


def format_currency(value: Any, currency_symbol: str = "$", decimals: int = 2) -> str:
    """
    Formats a numeric value as currency.
    """
    if value is None:
        return "N/A"

    try:
        numeric_value = float(value)
        formatted = f"{numeric_value:,.{decimals}f}"
        return f"{currency_symbol}{formatted}"
    except (ValueError, TypeError):
        logger.warning(f"Could not format currency from: {value}")
        return "N/A"

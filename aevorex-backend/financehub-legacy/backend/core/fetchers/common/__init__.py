"""
Common fetcher utilities and constants.

This module provides shared constants and utilities for all fetcher modules.
"""

# Public exports from _fetcher_constants
from backend.core.fetchers.common._fetcher_constants import (
    FETCH_FAILED_MARKER,
    DEFAULT_NA_VALUE,
    OHLCV_REQUIRED_COLS,
    MARKETAUX_BASE_URL,
    FMP_BASE_URL,
    NEWSAPI_BASE_URL,
    ALPHA_VANTAGE_BASE_URL,
    EODHD_BASE_URL,
    EODHD_BASE_URL_EOD,
    EODHD_BASE_URL_INTRADAY,
    EODHD_BASE_URL_FUNDAMENTALS,
)

__all__ = [
    "FETCH_FAILED_MARKER",
    "DEFAULT_NA_VALUE",
    "OHLCV_REQUIRED_COLS",
    "MARKETAUX_BASE_URL",
    "FMP_BASE_URL",
    "NEWSAPI_BASE_URL",
    "ALPHA_VANTAGE_BASE_URL",
    "EODHD_BASE_URL",
    "EODHD_BASE_URL_EOD",
    "EODHD_BASE_URL_INTRADAY",
    "EODHD_BASE_URL_FUNDAMENTALS",
]

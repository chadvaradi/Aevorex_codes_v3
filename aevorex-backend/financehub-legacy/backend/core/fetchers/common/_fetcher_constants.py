# backend/core/fetchers/common/_fetcher_constants.py
"""
Aevorex FinBot - Fetcher Shared Static Constants (v2.0 - Consolidated)

This module provides shared, static constants for all fetcher submodules
to prevent circular dependencies. It should NOT have complex imports.
"""

from typing import Final, List

# --- Common Markers and Values ---
# A konstans neve, amit a többi modul (pl. _base_helpers.py) importálni fog.
# Az értéke ("FETCH_FAILED_PERSISTENTLY") az, amit a cache-be írunk.
FETCH_FAILED_MARKER: Final[str] = "FETCH_FAILED_PERSISTENTLY"

DEFAULT_NA_VALUE: Final[str] = "N/A"

# --- Cache TTLs (in seconds) ---
# Hardcoded fallback values to ensure simplicity and avoid circular imports from settings.
FETCH_FAILURE_CACHE_TTL: Final[int] = 600  # 10 minutes
EODHD_DAILY_TTL: Final[int] = 86400  # 24 hours
EODHD_INTRADAY_TTL: Final[int] = 3600  # 1 hour
EODHD_FUNDAMENTALS_TTL: Final[int] = 86400  # 24 hours
EODHD_NEWS_TTL: Final[int] = 3600  # 1 hour
FMP_DEFAULT_TTL: Final[int] = 86400  # 24 hours

# --- Column Definitions ---
# Elsősorban a yfinance és az általános OHLCV feldolgozáshoz használt oszlopnevek.
# Az EODHD fetcher saját, specifikusabb oszlopnév definíciókat használhat.
OHLCV_REQUIRED_COLS: Final[List[str]] = ["open", "high", "low", "close", "volume"]

# --- API Base URLs (Static strings) ---
MARKETAUX_BASE_URL: Final[str] = "https://api.marketaux.com"
FMP_BASE_URL: Final[str] = (
    "https://financialmodelingprep.com/api"  # /v3, /v4 a konkrét URL-ben lesz
)
NEWSAPI_BASE_URL: Final[str] = "https://newsapi.org/v2"
ALPHA_VANTAGE_BASE_URL: Final[str] = "https://www.alphavantage.co/query"
EODHD_BASE_URL: Final[str] = "https://eodhistoricaldata.com/api"

# Specific EODHD endpoints derived from the base
EODHD_BASE_URL_EOD: Final[str] = f"{EODHD_BASE_URL}/eod"
EODHD_BASE_URL_INTRADAY: Final[str] = f"{EODHD_BASE_URL}/intraday"
EODHD_BASE_URL_FUNDAMENTALS: Final[str] = f"{EODHD_BASE_URL}/fundamentals"
EODHD_BASE_URL_NEWS: Final[str] = f"{EODHD_BASE_URL}/news"

__all__ = [
    "FETCH_FAILED_MARKER",
    "DEFAULT_NA_VALUE",
    "FETCH_FAILURE_CACHE_TTL",
    "EODHD_DAILY_TTL",
    "EODHD_INTRADAY_TTL",
    "EODHD_FUNDAMENTALS_TTL",
    "EODHD_NEWS_TTL",
    "FMP_DEFAULT_TTL",
    "OHLCV_REQUIRED_COLS",
    "MARKETAUX_BASE_URL",
    "FMP_BASE_URL",
    "NEWSAPI_BASE_URL",
    "ALPHA_VANTAGE_BASE_URL",
    "EODHD_BASE_URL",
    "EODHD_BASE_URL_EOD",
    "EODHD_BASE_URL_INTRADAY",
    "EODHD_BASE_URL_FUNDAMENTALS",
    "EODHD_BASE_URL_NEWS",
]

# Add other truly static, shared constants here as needed.
# For example, if EODHD_FETCHER_LOGGER in eodhd.py needs TARGET_OHLCV_COLS and other fetchers might too,
# they could also be moved here. For now, keeping them in eodhd.py is fine if not broadly shared.

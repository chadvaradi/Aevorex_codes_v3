"""
Core Helpers Package
====================

Unified namespace for all helper functions in the FinanceHub application.
Consolidated from various utils/helpers modules to eliminate duplication and drift.

Usage:
    from backend.core.helpers import text, cache, network, conversion, datetime

    # Text processing
    value = text.parse_optional_float("1,234.56")

    # Cache operations
    key = cache.generate_cache_key("user", user_id=123)

    # Network utilities
    data = await network.make_api_request(client, "GET", url)

    # Conversion utilities
    formatted = conversion.safe_format_value(123.45, decimals=2)
"""

# Import all helper modules
from . import datetime
from . import text
from . import network
from . import cache
from . import conversion

# Re-export commonly used functions for convenience
from .datetime import (
    parse_string_to_aware_datetime,
    parse_timestamp_to_iso_utc,
    format_datetime_for_api,
    get_current_utc,
)
from .text import (
    _clean_value,
    parse_optional_float,
    parse_optional_int,
    _validate_date_string,
    normalize_url,
    validate_http_url,
    clean_url_params,
    build_url_with_params,
)
from .network import make_api_request, get_request_id, get_user_id, get_default_headers

# Constants
FETCH_FAILED_MARKER = "FETCH_FAILED"
from .cache import (
    get_api_key,
    generate_cache_key,
    get_from_cache_or_fetch,
    safe_get,
    _ensure_datetime_index,
)
from .conversion import (
    safe_format_value,
    parse_percentage,
    parse_currency,
    format_currency,
)

__all__ = [
    # Modules
    "datetime",
    "text",
    "network",
    "cache",
    "conversion",
    # Common functions
    "parse_string_to_aware_datetime",
    "parse_timestamp_to_iso_utc",
    "format_datetime_for_api",
    "get_current_utc",
    "_clean_value",
    "parse_optional_float",
    "parse_optional_int",
    "_validate_date_string",
    "normalize_url",
    "validate_http_url",
    "clean_url_params",
    "build_url_with_params",
    "make_api_request",
    "get_request_id",
    "get_user_id",
    "get_default_headers",
    "get_api_key",
    "generate_cache_key",
    "get_from_cache_or_fetch",
    "safe_get",
    "_ensure_datetime_index",
    "safe_format_value",
    "parse_percentage",
    "parse_currency",
    "format_currency",
    "FETCH_FAILED_MARKER",
]

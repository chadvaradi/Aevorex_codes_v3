"""
Base helper functions for fetcher modules.

This module provides common utility functions needed by all fetcher modules,
including API key retrieval, cache key generation, and HTTP request handling.
"""

# Import from the main utils package
from backend.core.helpers import (
    get_api_key,
    generate_cache_key,
    get_from_cache_or_fetch,
    make_api_request,
    FETCH_FAILED_MARKER,
)

__all__ = [
    "get_api_key",
    "generate_cache_key",
    "make_api_request",
    "get_from_cache_or_fetch",
    "FETCH_FAILED_MARKER",
]

# modules/financehub/backend/core/fetchers/__init__.py
"""
This package contains the data fetching modules for various financial data providers.

The public API of this module is the `get_fetcher` factory function, which returns
a data fetcher for a specific provider.
"""

from .factory import get_fetcher
from .common.base_fetcher import BaseFetcher

__all__ = [
    "get_fetcher",
    "BaseFetcher",
]

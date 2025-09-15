

"""
Euribor Service

Provides methods to fetch and cache Euribor data from ECB/DBnomics sources.
"""

import logging
from typing import Optional, Dict, Any

from backend.utils.cache_service import CacheService
from backend.core.fetchers.macro.ecb_client.specials.euribor_client import (
    fetch_euribor_rate,
    fetch_euribor_curve,
)

logger = logging.getLogger(__name__)


class EuriborService:
    """
    Service class for handling Euribor data retrieval and caching.
    """

    def __init__(self, cache: Optional[CacheService] = None):
        self.cache = cache or CacheService()

    async def get_euribor_rate(self, tenor: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get a single Euribor rate for the specified tenor.

        Args:
            tenor: The Euribor tenor (e.g., '1M', '3M', '6M', '12M')
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            Dict containing metadata and rate
        """
        cache_key = f"euribor_rate:{tenor}"
        if not force_refresh:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Returning cached Euribor rate for tenor {tenor}")
                return {"cached": True, "tenor": tenor, "data": cached}

        rate = await fetch_euribor_rate(tenor)
        await self.cache.set(cache_key, rate, expire=3600)  # 1 hour
        return {"cached": False, "tenor": tenor, "data": rate}

    async def get_euribor_curve(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Get Euribor curve for a date range.

        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            force_refresh: If True, bypass cache and fetch fresh data

        Returns:
            Dict containing metadata and curve data
        """
        cache_key = f"euribor_curve:{start_date}:{end_date}"
        if not force_refresh:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.info(f"Returning cached Euribor curve {start_date} → {end_date}")
                return {"cached": True, "data": cached}

        curve = await fetch_euribor_curve(start_date=start_date, end_date=end_date)
        await self.cache.set(cache_key, curve, expire=3600)  # 1 hour
        return {"cached": False, "data": curve}
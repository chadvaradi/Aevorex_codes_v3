"""
Fundamentals Cache Service

Cache wrapper for fundamentals data with TTL support.
Provides caching capabilities for fundamental analysis data to improve performance.
"""

from typing import Dict, Any, Optional
from backend.utils.cache_service import CacheService
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class FundamentalsCacheService:
    """Cache service specifically for fundamentals data."""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.default_ttl = 3600  # 1 hour default TTL
        self.overview_ttl = 1800  # 30 minutes for overview (changes less frequently)
        self.financials_ttl = 7200  # 2 hours for financials (changes quarterly)
        self.ratios_ttl = 1800  # 30 minutes for ratios
        self.earnings_ttl = 3600  # 1 hour for earnings
    
    async def get_cached_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached company overview data."""
        cache_key = f"fundamentals:overview:{symbol}"
        try:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for overview: {symbol}")
            return cached_data
        except Exception as e:
            logger.warning(f"Failed to get cached overview for {symbol}: {e}")
            return None
    
    async def set_cached_overview(self, symbol: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache company overview data."""
        cache_key = f"fundamentals:overview:{symbol}"
        try:
            await self.cache_service.set(cache_key, data, ttl or self.overview_ttl)
            logger.debug(f"Cached overview data for {symbol}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache overview for {symbol}: {e}")
            return False
    
    async def get_cached_financials(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached financial statements data."""
        cache_key = f"fundamentals:financials:{symbol}"
        try:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for financials: {symbol}")
            return cached_data
        except Exception as e:
            logger.warning(f"Failed to get cached financials for {symbol}: {e}")
            return None
    
    async def set_cached_financials(self, symbol: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache financial statements data."""
        cache_key = f"fundamentals:financials:{symbol}"
        try:
            await self.cache_service.set(cache_key, data, ttl or self.financials_ttl)
            logger.debug(f"Cached financials data for {symbol}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache financials for {symbol}: {e}")
            return False
    
    async def get_cached_ratios(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached financial ratios data."""
        cache_key = f"fundamentals:ratios:{symbol}"
        try:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for ratios: {symbol}")
            return cached_data
        except Exception as e:
            logger.warning(f"Failed to get cached ratios for {symbol}: {e}")
            return None
    
    async def set_cached_ratios(self, symbol: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache financial ratios data."""
        cache_key = f"fundamentals:ratios:{symbol}"
        try:
            await self.cache_service.set(cache_key, data, ttl or self.ratios_ttl)
            logger.debug(f"Cached ratios data for {symbol}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache ratios for {symbol}: {e}")
            return False
    
    async def get_cached_earnings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached earnings data."""
        cache_key = f"fundamentals:earnings:{symbol}"
        try:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for earnings: {symbol}")
            return cached_data
        except Exception as e:
            logger.warning(f"Failed to get cached earnings for {symbol}: {e}")
            return None
    
    async def set_cached_earnings(self, symbol: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache earnings data."""
        cache_key = f"fundamentals:earnings:{symbol}"
        try:
            await self.cache_service.set(cache_key, data, ttl or self.earnings_ttl)
            logger.debug(f"Cached earnings data for {symbol}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache earnings for {symbol}: {e}")
            return False
    
    async def get_cached_baseline(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached baseline data."""
        cache_key = f"fundamentals:baseline:{symbol}"
        try:
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for baseline: {symbol}")
            return cached_data
        except Exception as e:
            logger.warning(f"Failed to get cached baseline for {symbol}: {e}")
            return None
    
    async def set_cached_baseline(self, symbol: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Cache baseline data."""
        cache_key = f"fundamentals:baseline:{symbol}"
        try:
            await self.cache_service.set(cache_key, data, ttl or self.overview_ttl)
            logger.debug(f"Cached baseline data for {symbol}")
            return True
        except Exception as e:
            logger.warning(f"Failed to cache baseline for {symbol}: {e}")
            return False
    
    async def invalidate_cache(self, symbol: str) -> bool:
        """Invalidate all cached data for a symbol."""
        cache_keys = [
            f"fundamentals:overview:{symbol}",
            f"fundamentals:financials:{symbol}",
            f"fundamentals:ratios:{symbol}",
            f"fundamentals:earnings:{symbol}",
            f"fundamentals:baseline:{symbol}",
        ]
        
        success = True
        for cache_key in cache_keys:
            try:
                await self.cache_service.delete(cache_key)
                logger.debug(f"Invalidated cache: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to invalidate cache {cache_key}: {e}")
                success = False
        
        return success


__all__ = ["FundamentalsCacheService"]

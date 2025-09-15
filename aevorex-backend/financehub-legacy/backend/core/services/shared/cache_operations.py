"""
Cache Operations - Basic Cache Operations

Split from cache_manager.py (224 LOC) to follow 160 LOC rule.
Handles basic cache operations and key generation.

Responsibilities:
- Cache key generation
- Basic cache get/set operations
- Cache data validation
- Cache metadata handling
"""

import time
import json
from typing import Any

from backend.utils.cache_service import CacheService
from backend.models.stock import FinBotStockResponse
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.CacheOperations")


class CacheOperations:
    """Service for basic cache operations."""

    def __init__(self):
        self.aggregated_response_ttl = 900  # 15 minutes

    def generate_cache_key(
        self,
        symbol: str,
        data_type: str,
        period: str | None = None,
        interval: str | None = None,
        **kwargs,
    ) -> str:
        """Generate standardized cache key for stock data."""
        key_parts = [f"stock:{symbol}:{data_type}"]

        if period:
            key_parts.append(f"period:{period}")
        if interval:
            key_parts.append(f"interval:{interval}")

        # Add additional parameters
        for key, value in sorted(kwargs.items()):
            if value is not None:
                key_parts.append(f"{key}:{value}")

        return ":".join(key_parts)

    async def check_aggregate_cache(
        self, cache_key: str, request_id: str, cache: CacheService
    ) -> FinBotStockResponse | None:
        """Check if aggregated response exists in cache."""
        try:
            cached_data = await cache.get(cache_key)

            if cached_data:
                logger.debug(f"[{request_id}] Cache HIT for key: {cache_key}")

                # Parse cached data
                if isinstance(cached_data, str):
                    data_dict = json.loads(cached_data)
                elif isinstance(cached_data, dict):
                    data_dict = cached_data
                else:
                    logger.warning(
                        f"[{request_id}] Invalid cached data type: {type(cached_data)}"
                    )
                    return None

                # Convert to FinBotStockResponse
                return FinBotStockResponse(**data_dict)

            logger.debug(f"[{request_id}] Cache MISS for key: {cache_key}")
            return None

        except Exception as e:
            logger.error(f"[{request_id}] Cache check error for key {cache_key}: {e}")
            return None

    async def cache_final_response(
        self,
        cache_key: str,
        response_model: FinBotStockResponse,
        request_id: str,
        cache: CacheService,
    ) -> bool:
        """Cache the final aggregated response."""
        try:
            # Convert to dict for caching
            response_dict = response_model.model_dump()

            # Add metadata
            response_dict["cached_at"] = time.time()
            response_dict["cache_key"] = cache_key

            # Cache the response
            await cache.set(
                cache_key,
                json.dumps(response_dict, default=str),
                ttl=self.aggregated_response_ttl,
            )

            logger.debug(f"[{request_id}] Cached response for key: {cache_key}")
            return True

        except Exception as e:
            logger.error(
                f"[{request_id}] Failed to cache response for key {cache_key}: {e}"
            )
            return False

    async def invalidate_cache(
        self, symbol: str, cache: CacheService, request_id: str
    ) -> bool:
        """Invalidate all cached data for a symbol."""
        try:
            # Pattern to match all cache keys for this symbol
            pattern = f"stock:{symbol}:*"

            # Get all matching keys
            keys = await cache.redis_client.keys(pattern)

            if keys:
                # Delete all matching keys
                await cache.redis_client.delete(*keys)
                logger.info(
                    f"[{request_id}] Invalidated {len(keys)} cache entries for {symbol}"
                )
            else:
                logger.debug(
                    f"[{request_id}] No cache entries to invalidate for {symbol}"
                )

            return True

        except Exception as e:
            logger.error(f"[{request_id}] Failed to invalidate cache for {symbol}: {e}")
            return False

    async def get_cache_stats(self, cache: CacheService) -> dict[str, Any]:
        """Get cache statistics."""
        try:
            info = await cache.redis_client.info()

            return {
                "used_memory": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0), info.get("keyspace_misses", 0)
                ),
            }

        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {"error": str(e)}

    def _calculate_hit_rate(self, hits: int, misses: int) -> float:
        """Calculate cache hit rate percentage."""
        total = hits + misses
        if total == 0:
            return 0.0
        return (hits / total) * 100

    async def cached_fetch(
        self, fetch_function, cache: CacheService, key: str, ttl: int, *args, **kwargs
    ):
        """
        Wraps a fetch function to cache its result.

        Args:
            fetch_function: The function to wrap.
            cache: The cache service instance.
            key: The cache key to use.
            ttl: Time to live for the cached data.
            *args: Positional arguments to pass to the fetch function.
            **kwargs: Keyword arguments to pass to the fetch function.

        Returns:
            The result of the fetch function.
        """
        # Ensure cache object is not passed down to the fetch_function if it doesn't expect it
        kwargs.pop("cache", None)

        try:
            data = await fetch_function(*args, **kwargs)
            if data is not None:
                await cache.set(key, data, ttl=ttl)
                logger.info(f"CACHE SET: Key='{key}' | TTL={ttl}s")
            return data
        except Exception as e:
            logger.error(f"Failed to fetch data: {e}")
            return None

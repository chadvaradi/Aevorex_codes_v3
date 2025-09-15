"""
Cache Manager Service - Caching Operations

Extracted from stock_service.py (3,774 LOC) to follow 160 LOC rule.
Handles all caching operations for stock data.

Responsibilities:
- Cache key generation and management
- Cache hit/miss logic
- Cache expiration handling
- Redis lock management
"""

import time
import json
from redis.exceptions import LockError
from redis.asyncio.lock import Lock as AsyncLock

from backend.utils.cache_service import CacheService
from backend.models.stock import FinBotStockResponse
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.CacheManager")


class CacheManager:
    """Service for managing stock data caching operations."""

    def __init__(self):
        self.aggregated_response_ttl = 900  # 15 minutes
        self.lock_ttl_seconds = 60
        self.lock_blocking_timeout = 5.0

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

    async def with_cache_lock(
        self,
        cache_key: str,
        request_id: str,
        cache: CacheService,
        operation_func,
        *args,
        **kwargs,
    ):
        """Execute operation with Redis lock to prevent cache stampede."""
        lock_key = f"lock:{cache_key}"

        # Try to acquire lock
        lock = AsyncLock(
            cache.redis_client,
            lock_key,
            timeout=self.lock_ttl_seconds,
            blocking_timeout=self.lock_blocking_timeout,
        )

        try:
            async with lock:
                logger.debug(f"[{request_id}] Acquired lock for: {lock_key}")

                # Double-check cache after acquiring lock
                cached_result = await self.check_aggregate_cache(
                    cache_key, request_id, cache
                )
                if cached_result:
                    logger.debug(
                        f"[{request_id}] Found cached result after lock acquisition"
                    )
                    return cached_result

                # Execute the operation
                result = await operation_func(*args, **kwargs)

                # Cache the result if successful
                if result:
                    await self.cache_final_response(
                        cache_key, result, request_id, cache
                    )

                return result

        except LockError as e:
            logger.warning(f"[{request_id}] Failed to acquire lock for {lock_key}: {e}")
            # Fallback: execute without lock
            return await operation_func(*args, **kwargs)

        except Exception as e:
            logger.error(
                f"[{request_id}] Error in locked operation for {lock_key}: {e}"
            )
            raise

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

    # Cache stats moved to cache_operations.py

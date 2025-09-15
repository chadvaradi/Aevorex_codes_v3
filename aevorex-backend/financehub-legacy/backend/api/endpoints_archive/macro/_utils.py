from __future__ import annotations

import asyncio

import structlog
from backend.utils.cache_service import CacheService

logger = structlog.get_logger()

# Cache configuration
CACHE_SETTINGS: dict[str, int] = {
    "ecb_policy_rates": 3600,  # 1 hour
    "bubor_curve": 1800,  # 30 minutes
    "ecb_fx_rates": 3600,  # 1 hour
    "ecb_historical": 86400,  # 24 hours
    "bubor_historical": 86400,  # 24 hours for historical BUBOR
    "ecb_generic_dataflow": 86400,  # 24 hours for generic ECB data
}


async def cached_fetch(
    cache_key: str, fetch_func, cache: CacheService, *args, **kwargs
):
    """Redis cache wrapper with structured logging."""
    # Cache lookup
    cached_data = await cache.get(cache_key)
    if cached_data:
        logger.info("cache_hit", key=cache_key)
        return cached_data

    # Real API fetch
    start_time = asyncio.get_event_loop().time()
    fresh_data = await fetch_func(*args, **kwargs)
    duration = asyncio.get_event_loop().time() - start_time

    # Cache store
    cache_type = cache_key.split(":")[0]
    ttl = CACHE_SETTINGS.get(cache_type, 3600)
    await cache.set(cache_key, fresh_data, ttl=ttl)

    logger.info("cache_miss_filled", key=cache_key, duration=duration, ttl=ttl)
    return fresh_data

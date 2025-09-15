"""
Rate Limiter Factory
===================

Factory functions for creating rate limiter instances.
"""

import logging
from typing import Optional
import redis.asyncio as redis

from .middleware import RateLimiterMiddleware
from .limiter import SlidingWindowLimiter

logger = logging.getLogger("aevorex_finbot_api.middleware.rate_limiter.factory")


def create_rate_limiter(
    app, redis_url: Optional[str] = None, enable_redis: bool = True
) -> RateLimiterMiddleware:
    """
    Factory function to create rate limiter middleware

    Args:
        app: FastAPI application instance
        redis_url: Redis connection URL (optional)
        enable_redis: Whether to enable Redis for rate limiting

    Returns:
        Configured RateLimiterMiddleware instance
    """
    redis_client = None

    if enable_redis and redis_url:
        try:
            redis_client = redis.from_url(redis_url)
            logger.info("Redis client configured for rate limiter")
        except Exception as e:
            logger.warning(f"Failed to configure Redis for rate limiter: {str(e)}")
            redis_client = None

    middleware = RateLimiterMiddleware(app=app, redis_client=redis_client)

    logger.info("Rate limiter middleware created successfully")
    return middleware


def create_sliding_window_limiter(
    redis_client: Optional[redis.Redis] = None,
) -> SlidingWindowLimiter:
    """
    Factory function to create sliding window limiter

    Args:
        redis_client: Redis client instance (optional)

    Returns:
        Configured SlidingWindowLimiter instance
    """
    limiter = SlidingWindowLimiter(redis_client=redis_client)

    logger.info("Sliding window limiter created successfully")
    return limiter


async def configure_redis_for_rate_limiter(redis_url: str) -> Optional[redis.Redis]:
    """
    Configure Redis client for rate limiter

    Args:
        redis_url: Redis connection URL

    Returns:
        Redis client instance or None if failed
    """
    try:
        client = redis.from_url(redis_url)

        # Test connection
        await client.ping()

        logger.info(f"Redis connection established for rate limiter: {redis_url}")
        return client

    except Exception as e:
        logger.error(f"Failed to connect to Redis for rate limiter: {str(e)}")
        return None

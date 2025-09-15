"""
Sliding Window Rate Limiter
===========================

Redis-based sliding window rate limiter implementation.
"""

import time
import logging
from typing import Optional, Tuple
import redis.asyncio as redis

logger = logging.getLogger("aevorex_finbot_api.middleware.rate_limiter.limiter")


class SlidingWindowLimiter:
    """
    Redis-based sliding window rate limiter

    Uses Redis sorted sets to implement a sliding window counter.
    """

    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.script_sha = None

        # Lua script for atomic sliding window operations
        self.lua_script = """
        local key = KEYS[1]
        local window = tonumber(ARGV[1])
        local limit = tonumber(ARGV[2])
        local now = tonumber(ARGV[3])
        local ttl = tonumber(ARGV[4])
        
        -- Remove expired entries
        redis.call('ZREMRANGEBYSCORE', key, 0, now - window)
        
        -- Count current entries
        local current = redis.call('ZCARD', key)
        
        if current < limit then
            -- Add current request
            redis.call('ZADD', key, now, now)
            -- Set expiration
            redis.call('EXPIRE', key, ttl)
            return {1, limit - current - 1, now + window}
        else
            -- Rate limit exceeded
            local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
            local reset_time = oldest[2] and (oldest[2] + window) or (now + window)
            return {0, 0, reset_time}
        end
        """

    async def check_rate_limit(
        self, identifier: str, limit: int, window: int
    ) -> Tuple[bool, int, int]:
        """
        Check if request is within rate limit

        Args:
            identifier: Client identifier (user ID or IP)
            limit: Maximum requests allowed in window
            window: Time window in seconds

        Returns:
            Tuple of (allowed, remaining, reset_time)
        """
        if not self.redis_client:
            # If Redis is not available, allow all requests
            logger.warning("Redis not available for rate limiting, allowing request")
            return True, limit - 1, int(time.time()) + window

        try:
            now = int(time.time() * 1000)  # Use milliseconds for precision
            key = f"rate_limit:{identifier}"
            ttl = window + 60  # Keep data slightly longer than window

            # Load script if not already loaded
            if not self.script_sha:
                self.script_sha = await self.redis_client.script_load(self.lua_script)

            # Execute atomic sliding window check
            result = await self.redis_client.evalsha(
                self.script_sha,
                1,
                key,
                window * 1000,  # Convert to milliseconds
                limit,
                now,
                ttl,
            )

            allowed = bool(result[0])
            remaining = int(result[1])
            reset_time = int(result[2] / 1000)  # Convert back to seconds

            if not allowed:
                logger.info(
                    f"Rate limit exceeded for {identifier}: {limit} requests per {window}s"
                )

            return allowed, remaining, reset_time

        except Exception as e:
            logger.error(f"Error checking rate limit: {str(e)}")
            # On error, allow the request to avoid blocking legitimate traffic
            return True, limit - 1, int(time.time()) + window

    async def get_current_usage(self, identifier: str, window: int) -> int:
        """
        Get current usage count for identifier
        """
        if not self.redis_client:
            return 0

        try:
            now = int(time.time() * 1000)
            key = f"rate_limit:{identifier}"

            # Remove expired entries
            await self.redis_client.zremrangebyscore(key, 0, now - (window * 1000))

            # Get current count
            count = await self.redis_client.zcard(key)
            return count

        except Exception as e:
            logger.error(f"Error getting rate limit usage: {str(e)}")
            return 0

    async def reset_limit(self, identifier: str) -> bool:
        """
        Reset rate limit for identifier
        """
        if not self.redis_client:
            return False

        try:
            key = f"rate_limit:{identifier}"
            await self.redis_client.delete(key)
            logger.info(f"Rate limit reset for {identifier}")
            return True

        except Exception as e:
            logger.error(f"Error resetting rate limit: {str(e)}")
            return False

    async def get_stats(self) -> dict:
        """
        Get rate limiter statistics
        """
        if not self.redis_client:
            return {"active_limits": 0, "redis_available": False}

        try:
            # Get all rate limit keys
            keys = await self.redis_client.keys("rate_limit:*")

            stats = {
                "active_limits": len(keys),
                "redis_available": True,
                "total_requests_tracked": 0,
            }

            # Count total requests being tracked
            for key in keys:
                count = await self.redis_client.zcard(key)
                stats["total_requests_tracked"] += count

            return stats

        except Exception as e:
            logger.error(f"Error getting rate limiter stats: {str(e)}")
            return {"active_limits": 0, "redis_available": False, "error": str(e)}

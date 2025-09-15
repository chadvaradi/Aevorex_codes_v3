"""
Rate Limiting Middleware for FinanceHub Backend
"""

import time
from typing import Optional, Tuple
from fastapi import Request, status
from fastapi.responses import JSONResponse
from backend.utils.cache_service import cache_service
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class RateLimiter:
    """Redis-based rate limiter with sliding window"""

    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        requests_per_day: int = 10000,
        burst_limit: int = 10,
    ):
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.burst_limit = burst_limit

    def _get_client_id(self, request: Request) -> str:
        """Get unique client identifier"""
        # Try to get user ID from JWT token
        user_id = getattr(request.state, "user", {}).get("user_id")
        if user_id:
            return f"user:{user_id}"

        # Fall back to IP address
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()

        return f"ip:{client_ip}"

    def _get_rate_limit_key(self, client_id: str, window: str) -> str:
        """Generate rate limit key for Redis"""
        return f"rate_limit:{client_id}:{window}"

    async def _check_rate_limit(
        self, client_id: str, window: str, limit: int, window_seconds: int
    ) -> Tuple[bool, int, int]:
        """Check rate limit for a specific window"""
        key = self._get_rate_limit_key(client_id, window)
        current_time = int(time.time())
        window_start = current_time - window_seconds

        try:
            if not cache_service.redis_client:
                # If Redis is not available, allow the request
                logger.warning(
                    "Redis not available for rate limiting, allowing request"
                )
                return True, limit, limit

            # Use Redis pipeline for atomic operations
            pipe = cache_service.redis_client.pipeline()

            # Remove old entries
            pipe.zremrangebyscore(key, 0, window_start)

            # Count current requests
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(current_time): current_time})

            # Set expiration
            pipe.expire(key, window_seconds + 60)  # Add buffer

            results = await pipe.execute()
            current_requests = results[1] + 1  # +1 for the current request

            remaining = max(0, limit - current_requests)
            return current_requests <= limit, current_requests, remaining

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            # If rate limiting fails, allow the request
            return True, 0, limit

    async def check_limits(self, request: Request) -> Optional[JSONResponse]:
        """Check all rate limits for the request"""
        client_id = self._get_client_id(request)
        current_time = int(time.time())

        # Check burst limit (10 requests per 10 seconds)
        burst_allowed, burst_used, burst_remaining = await self._check_rate_limit(
            client_id, "burst", self.burst_limit, 10
        )

        if not burst_allowed:
            logger.warning(f"Burst rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": "Too many requests in a short time",
                    "retry_after": 10,
                    "limit": self.burst_limit,
                    "used": burst_used,
                    "remaining": 0,
                    "window": "10 seconds",
                },
                headers={
                    "X-RateLimit-Limit": str(self.burst_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(current_time + 10),
                    "Retry-After": "10",
                },
            )

        # Check minute limit
        minute_allowed, minute_used, minute_remaining = await self._check_rate_limit(
            client_id, "minute", self.requests_per_minute, 60
        )

        if not minute_allowed:
            logger.warning(f"Minute rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": "Too many requests per minute",
                    "retry_after": 60,
                    "limit": self.requests_per_minute,
                    "used": minute_used,
                    "remaining": 0,
                    "window": "1 minute",
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(current_time + 60),
                    "Retry-After": "60",
                },
            )

        # Check hour limit
        hour_allowed, hour_used, hour_remaining = await self._check_rate_limit(
            client_id, "hour", self.requests_per_hour, 3600
        )

        if not hour_allowed:
            logger.warning(f"Hour rate limit exceeded for {client_id}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": "Too many requests per hour",
                    "retry_after": 3600,
                    "limit": self.requests_per_hour,
                    "used": hour_used,
                    "remaining": 0,
                    "window": "1 hour",
                },
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(current_time + 3600),
                    "Retry-After": "3600",
                },
            )

        # Add rate limit headers to successful responses
        request.state.rate_limit_headers = {
            "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
            "X-RateLimit-Remaining-Minute": str(minute_remaining),
            "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
            "X-RateLimit-Remaining-Hour": str(hour_remaining),
            "X-RateLimit-Reset-Minute": str(current_time + 60),
            "X-RateLimit-Reset-Hour": str(current_time + 3600),
        }

        return None  # No rate limit exceeded


# Global rate limiter instances
default_rate_limiter = RateLimiter()
strict_rate_limiter = RateLimiter(
    requests_per_minute=30, requests_per_hour=500, requests_per_day=5000, burst_limit=5
)

# Rate limiter for external API endpoints (ECB, etc.)
external_api_rate_limiter = RateLimiter(
    requests_per_minute=10, requests_per_hour=100, requests_per_day=1000, burst_limit=3
)

"""
Rate Limiter Middleware
=======================

FastAPI middleware for rate limiting using sliding window algorithm.
"""

import time
import logging
from typing import Optional
from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

from .config import get_rate_limit_for_path, is_exempt_endpoint, get_client_identifier
from .limiter import SlidingWindowLimiter

logger = logging.getLogger("aevorex_finbot_api.middleware.rate_limiter")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Rate Limiting Middleware

    Implements sliding window rate limiting with Redis backend.
    """

    def __init__(self, app, redis_client: Optional[redis.Redis] = None):
        super().__init__(app)
        self.redis_client = redis_client
        self.limiter = SlidingWindowLimiter(redis_client)

        logger.info("Rate Limiter Middleware initialized")

    async def dispatch(self, request: Request, call_next):
        """
        Process request with rate limiting
        """
        start_time = time.time()

        try:
            # Check if endpoint is exempt
            path = request.url.path
            if is_exempt_endpoint(path):
                response = await call_next(request)
                self._add_timing_header(response, start_time)
                return response

            # Get rate limit configuration for this path
            limit, window = get_rate_limit_for_path(path)

            # Get client identifier
            client_id = get_client_identifier(request)

            # Check rate limit
            allowed, remaining, reset_time = await self.limiter.check_rate_limit(
                client_id, limit, window
            )

            if not allowed:
                # Rate limit exceeded
                logger.warning(f"Rate limit exceeded for {client_id} on {path}")
                return self._create_rate_limit_response(
                    limit, remaining, reset_time, window
                )

            # Process request
            response = await call_next(request)

            # Add rate limit headers
            self._add_rate_limit_headers(response, limit, remaining, reset_time, window)
            self._add_timing_header(response, start_time)

            return response

        except Exception as e:
            logger.error(f"Error in rate limiter middleware: {str(e)}")
            # On error, allow request to proceed
            response = await call_next(request)
            self._add_timing_header(response, start_time)
            return response

    def _create_rate_limit_response(
        self, limit: int, remaining: int, reset_time: int, window: int
    ) -> JSONResponse:
        """
        Create rate limit exceeded response
        """
        retry_after = max(1, reset_time - int(time.time()))

        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(reset_time),
            "X-RateLimit-Window": str(window),
            "Retry-After": str(retry_after),
        }

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "detail": "Rate limit exceeded",
                "limit": limit,
                "window": window,
                "retry_after": retry_after,
            },
            headers=headers,
        )

    def _add_rate_limit_headers(
        self,
        response: Response,
        limit: int,
        remaining: int,
        reset_time: int,
        window: int,
    ):
        """
        Add rate limit headers to response
        """
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_time)
        response.headers["X-RateLimit-Window"] = str(window)

    def _add_timing_header(self, response: Response, start_time: float):
        """
        Add request timing header
        """
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

    async def get_client_stats(self, client_id: str) -> dict:
        """
        Get rate limiting stats for a specific client
        """
        try:
            stats = {}

            # Get usage for different time windows
            for window in [60, 300, 3600]:  # 1 min, 5 min, 1 hour
                usage = await self.limiter.get_current_usage(client_id, window)
                stats[f"usage_{window}s"] = usage

            return stats

        except Exception as e:
            logger.error(f"Error getting client stats: {str(e)}")
            return {}

    async def reset_client_limit(self, client_id: str) -> bool:
        """
        Reset rate limit for a specific client
        """
        return await self.limiter.reset_limit(client_id)

    async def get_overall_stats(self) -> dict:
        """
        Get overall rate limiter statistics
        """
        return await self.limiter.get_stats()

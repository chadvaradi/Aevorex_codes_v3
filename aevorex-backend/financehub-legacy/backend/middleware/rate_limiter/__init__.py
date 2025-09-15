"""
Rate Limiting Middleware for FinanceHub
=======================================

Modular rate limiting system with Redis sliding window implementation.
"""

from .middleware import RateLimiterMiddleware
from .limiter import SlidingWindowLimiter
from .config import RATE_LIMIT_RULES, DEFAULT_LIMITS
from .factory import create_rate_limiter

__all__ = [
    "RateLimiterMiddleware",
    "SlidingWindowLimiter",
    "RATE_LIMIT_RULES",
    "DEFAULT_LIMITS",
    "create_rate_limiter",
]

__version__ = "1.0.0"

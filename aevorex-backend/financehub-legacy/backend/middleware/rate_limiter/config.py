"""
Rate Limiter Configuration
==========================

Configuration for rate limiting rules and defaults.
"""

import logging
from typing import Dict, Tuple

logger = logging.getLogger("aevorex_finbot_api.middleware.rate_limiter.config")

# Rate limiting rules: (requests_per_window, window_seconds)
RATE_LIMIT_RULES: Dict[str, Tuple[int, int]] = {
    # API endpoints
    "/api/v1/stock/": (100, 60),  # 100 requests per minute
    "/api/v1/macro/": (200, 60),  # 200 requests per minute
    "/api/v1/auth/": (10, 60),  # 10 requests per minute
    "/api/v1/stock/chat/": (
        20,
        60,
    ),  # 20 requests per minute (align to actual chat path)
    # Specific endpoints with stricter limits
    "/api/v1/auth/login": (5, 300),  # 5 attempts per 5 minutes
    "/api/v1/auth/refresh": (10, 60),  # 10 refreshes per minute
    # Default for all other endpoints
    "default": (1000, 60),  # 1000 requests per minute
}

# Default limits if no specific rule matches
DEFAULT_LIMITS = {
    "requests": 1000,
    "window": 60,  # seconds
    "burst": 50,  # burst allowance
}

# Rate limit headers to include in responses
RATE_LIMIT_HEADERS = {
    "X-RateLimit-Limit": "limit",
    "X-RateLimit-Remaining": "remaining",
    "X-RateLimit-Reset": "reset_time",
    "X-RateLimit-Window": "window",
}

# Exempt endpoints from rate limiting
EXEMPT_ENDPOINTS = {"/api/v1/health", "/docs", "/openapi.json", "/redoc", "/metrics"}


def get_rate_limit_for_path(path: str) -> Tuple[int, int]:
    """
    Get rate limit configuration for a specific path

    Returns:
        Tuple of (requests_per_window, window_seconds)
    """
    # Check for exact matches first
    if path in RATE_LIMIT_RULES:
        return RATE_LIMIT_RULES[path]

    # Check for prefix matches
    for pattern, limits in RATE_LIMIT_RULES.items():
        if pattern != "default" and path.startswith(pattern):
            return limits

    # Return default limits
    return RATE_LIMIT_RULES["default"]


def is_exempt_endpoint(path: str) -> bool:
    """
    Check if endpoint is exempt from rate limiting
    """
    return (
        path in EXEMPT_ENDPOINTS
        or path.startswith("/docs")
        or path.startswith("/redoc")
    )


def get_client_identifier(request) -> str:
    """
    Get client identifier for rate limiting

    Uses user ID if authenticated, otherwise falls back to IP address
    """
    # Try to get user ID from authenticated request
    if hasattr(request.state, "user") and request.state.user:
        user_id = request.state.user.get("user_id")
        if user_id:
            return f"user:{user_id}"

    # Fall back to IP address
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Get first IP in case of multiple proxies
        client_ip = forwarded_for.split(",")[0].strip()
    else:
        client_ip = request.client.host if request.client else "unknown"

    return f"ip:{client_ip}"

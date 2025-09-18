"""
JWT Authentication Configuration
===============================

Security headers, constants, and configuration for JWT authentication.
"""

import logging
from typing import Set

logger = logging.getLogger("aevorex_finbot_api.middleware.jwt_auth.config")

# Security headers to be added to all responses
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; img-src 'self' https://fastapi.tiangolo.com; font-src 'self' https://cdn.jsdelivr.net;",
}

# Public endpoints that don't require authentication
PUBLIC_ENDPOINTS: Set[str] = {
    "/",
    "/docs",
    "/openapi.json",
    "/redoc",
    "/api/v1/health",
    "/api/v1/auth/login",
    "/api/v1/auth/start",
    "/api/v1/auth/callback",
    "/api/v1/chat/models",  # Chat models endpoint - public
    "/api/v1/macro/bubor/",
    "/api/v1/macro/curve/ecb",
    "/api/v1/macro/curve/ust",
    "/api/v1/macro/curve/compare",
    "/api/v1/macro/fixing/estr",
    "/api/v1/macro/fixing/euribor/",
    "/api/v1/eodhd/",
    "/api/v1/ticker-tape/",  # Ticker tape endpoint - public
    "/api/v1/billing/lemonsqueezy",  # LemonSqueezy webhook endpoint - public
    "/.well-known/ai-plugin.json",  # MCP manifest endpoint - public
    "/.well-known/openapi.yaml",  # MCP OpenAPI spec endpoint - public
    "/.well-known/health",  # MCP health check endpoint - public
    "/api/v1/.well-known/ai-plugin.json",  # MCP manifest endpoint with API prefix - public
    "/api/v1/.well-known/openapi.yaml",  # MCP OpenAPI spec endpoint with API prefix - public
    "/api/v1/.well-known/health",  # MCP health check endpoint with API prefix - public
    "/metrics",
}

# JWT Configuration defaults
JWT_DEFAULTS = {
    "algorithm": "HS256",
    "token_expiration": 900,  # 15 minutes
    "max_refresh_age": 3600,  # 1 hour
    "blacklist_ttl": 3600,  # 1 hour
}

# JWT Configuration from environment
import os

JWT_SECRET_KEY = os.getenv(
    "GOOGLE_AUTH_SECRET_KEY", "default-secret-key-change-in-production"
)
JWT_ALGORITHM = os.getenv("JWT_ALG", "HS256")

# Required JWT payload fields
REQUIRED_JWT_FIELDS = ["user_id", "email", "exp", "iat"]


def is_public_endpoint(path: str) -> bool:
    """
    Check if the endpoint is public (doesn't require authentication)
    """
    # Exact match
    if path in PUBLIC_ENDPOINTS:
        return True

    # Pattern matching for API documentation
    if path.startswith("/docs") or path.startswith("/redoc"):
        return True

    # EODHD endpoint patterns
    if path.startswith("/api/v1/eodhd/"):
        return True

    # Ticker tape endpoint patterns
    if path.startswith("/api/v1/ticker-tape/"):
        return True

    # Macro endpoint patterns
    if path.startswith("/api/v1/macro/"):
        return True

    # Fundamentals endpoint patterns
    if path.startswith("/api/v1/fundamentals/"):
        return True


    # TradingView endpoint patterns
    if path.startswith("/api/v1/tradingview/"):
        return True

    # Search endpoint patterns
    if path.startswith("/api/v1/search/"):
        return True

    # Summary endpoint patterns
    if path.startswith("/api/v1/summary/"):
        return True

    # Chat endpoint patterns
    if path.startswith("/api/v1/chat/"):
        return True

    # Billing endpoint patterns (webhooks)
    if path.startswith("/api/v1/billing/"):
        return True

    # Health check patterns
    if path.startswith("/health") or path.startswith("/ping"):
        return True

    return False

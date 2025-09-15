"""
JWT Middleware Factory
=====================

Factory functions for creating JWT middleware instances with different configurations.
"""

import logging
from typing import Optional
import redis.asyncio as redis

from .middleware import JWTAuthMiddleware
from .token_service import JWTTokenService
from .config import JWT_DEFAULTS

logger = logging.getLogger("aevorex_finbot_api.middleware.jwt_auth.factory")


def create_jwt_middleware(
    app,
    secret_key: str,
    redis_url: Optional[str] = None,
    algorithm: str = "HS256",
    token_expiration: int = None,
    enable_redis: bool = True,
) -> JWTAuthMiddleware:
    """
    Factory function to create JWT middleware with Redis support

    Args:
        app: FastAPI application instance
        secret_key: JWT secret key for token signing
        redis_url: Redis connection URL (optional)
        algorithm: JWT algorithm (default: HS256)
        token_expiration: Token expiration in seconds
        enable_redis: Whether to enable Redis for session management

    Returns:
        Configured JWTAuthMiddleware instance
    """
    if token_expiration is None:
        token_expiration = JWT_DEFAULTS["token_expiration"]

    redis_client = None

    if enable_redis and redis_url:
        try:
            redis_client = redis.from_url(redis_url)
            logger.info("Redis client configured for JWT middleware")
        except Exception as e:
            logger.warning(f"Failed to configure Redis for JWT: {str(e)}")
            redis_client = None

    middleware = JWTAuthMiddleware(
        app=app,
        secret_key=secret_key,
        redis_client=redis_client,
        algorithm=algorithm,
        token_expiration=token_expiration,
    )

    logger.info("JWT middleware created successfully")
    return middleware


def create_jwt_service(
    secret_key: str,
    redis_client: Optional[redis.Redis] = None,
    algorithm: str = "HS256",
    token_expiration: int = None,
) -> JWTTokenService:
    """
    Factory function to create JWT token service

    Args:
        secret_key: JWT secret key for token signing
        redis_client: Redis client instance (optional)
        algorithm: JWT algorithm (default: HS256)
        token_expiration: Token expiration in seconds

    Returns:
        Configured JWTTokenService instance
    """
    if token_expiration is None:
        token_expiration = JWT_DEFAULTS["token_expiration"]

    service = JWTTokenService(
        secret_key=secret_key,
        redis_client=redis_client,
        algorithm=algorithm,
        token_expiration=token_expiration,
    )

    logger.info("JWT token service created successfully")
    return service


async def configure_redis_for_jwt(redis_url: str) -> Optional[redis.Redis]:
    """
    Configure Redis client for JWT middleware

    Args:
        redis_url: Redis connection URL

    Returns:
        Redis client instance or None if failed
    """
    try:
        client = redis.from_url(redis_url)

        # Test connection
        await client.ping()

        logger.info(f"Redis connection established for JWT: {redis_url}")
        return client

    except Exception as e:
        logger.error(f"Failed to connect to Redis for JWT: {str(e)}")
        return None

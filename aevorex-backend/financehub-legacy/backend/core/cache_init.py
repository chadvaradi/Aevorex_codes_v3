from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

try:
    import redis.asyncio as aioredis
    from redis.exceptions import RedisError, ConnectionError as RedisConnectionError
except ImportError:
    print("FATAL ERROR: 'redis' library not found.", file=sys.stderr)
    sys.exit(1)

from backend.config import settings

if TYPE_CHECKING:
    from ..utils.cache_service import CacheService

logger = logging.getLogger(__name__)
MODULE_PREFIX = "[CacheService(Redis)]"


async def initialize_cache_service(cls: type[CacheService]) -> CacheService:
    """
    Asynchronous factory function to create and initialize a CacheService instance.
    This was extracted from the `create` classmethod.
    """
    logger.info(f"{MODULE_PREFIX} Initializing Redis connection...")
    try:
        redis_host = settings.REDIS.HOST
        redis_port = settings.REDIS.PORT
        redis_db = settings.REDIS.DB_CACHE
        connect_timeout = settings.REDIS.CONNECT_TIMEOUT_SECONDS
        socket_op_timeout = settings.REDIS.SOCKET_TIMEOUT_SECONDS

        pool = aioredis.ConnectionPool(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
            max_connections=50,
            socket_connect_timeout=connect_timeout,
            socket_timeout=socket_op_timeout,
        )
        redis_client = aioredis.Redis(connection_pool=pool)

        await redis_client.ping()
        logger.info(
            f"{MODULE_PREFIX} Redis connection successful to {redis_host}:{redis_port} (DB: {redis_db})."
        )

        return cls(redis_client, pool)

    except RedisConnectionError as e:
        logger.critical(
            f"{MODULE_PREFIX} FATAL: Could not connect to Redis: {e}", exc_info=True
        )
        raise RuntimeError(f"Failed to connect to Redis backend: {e}") from e
    except RedisError as e:
        logger.critical(
            f"{MODULE_PREFIX} FATAL: Redis error during initialization: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Redis backend initialization failed: {e}") from e
    except AttributeError as e:
        logger.critical(
            f"{MODULE_PREFIX} FATAL: Missing Redis configuration in settings: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Missing Redis configuration: {e}") from e
    except Exception as e:
        logger.critical(
            f"{MODULE_PREFIX} FATAL: Unexpected error during initialization: {e}",
            exc_info=True,
        )
        raise RuntimeError(f"Unexpected error initializing CacheService: {e}") from e


async def close_cache_connection(pool: aioredis.ConnectionPool):
    """Closes the Redis connection pool."""
    logger.info(f"{MODULE_PREFIX} Closing Redis connection pool...")
    try:
        await pool.disconnect()
        logger.info(f"{MODULE_PREFIX} Redis connection pool closed successfully.")
    except Exception as e:
        logger.error(
            f"{MODULE_PREFIX} Error closing Redis connection pool: {e}", exc_info=True
        )

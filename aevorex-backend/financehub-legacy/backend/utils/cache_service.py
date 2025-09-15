"""
Enhanced Redis Cache Service with improved connection handling
"""

import json
import time
from typing import Optional, Union
import redis.asyncio as redis
from redis.exceptions import ConnectionError
from backend.utils.logger_config import get_logger

# -----------------------------------------------------------------------------
# Conditional CacheService implementation (Redis vs. in-memory)
# -----------------------------------------------------------------------------
import os

# NOTE: we evaluate the desired cache mode *before* importing heavy Redis deps.
_CACHE_MODE = os.getenv("FINANCEHUB_CACHE_MODE", "redis").lower().strip()

if _CACHE_MODE == "memory":
    # ---------------------------------------------------------------------
    # Lightweight in-memory fallback – avoids Redis dependency for dev setups
    # ---------------------------------------------------------------------

    class CacheService:  # type: ignore[override]  # noqa: D401 – simple stub
        """Very thin in-memory cache replacement for local dev."""

        @classmethod
        async def create(cls, *args, **kwargs):
            """Factory method for parity with the Redis-backed implementation."""
            return cls()

        def __init__(self):
            self._store: dict[str, str] = {}

        async def get(self, key: str):
            return self._store.get(key)

        async def set(self, key: str, value, ttl: int = 300):  # noqa: D401
            # TTL ignored in simple dict cache
            self._store[key] = value
            return True

        async def delete(self, key: str):
            self._store.pop(key, None)
            return True

        async def exists(self, key: str):
            return key in self._store

        async def close(self):  # noqa: D401
            self._store.clear()

        # -----------------------------------------------------------------
        # Compatibility helpers – mimic subset of redis.Redis interface
        # -----------------------------------------------------------------
        async def keys(self, pattern: str):  # noqa: D401 – dev helper
            # Very naive glob implementation (sufficient for dev/demo)
            import fnmatch

            return [k for k in self._store.keys() if fnmatch.fnmatch(k, pattern)]

        # Duplicate definitions removed – method aliases below keep API parity

        async def delete_many(self, *keys):  # noqa: D401 – explicit name
            """Delete multiple keys (compat replacement for duplicate method)."""
            deleted = 0
            for k in keys:
                if k in self._store:
                    self._store.pop(k, None)
                    deleted += 1
            return deleted

        # Provide `redis_client` attr expected by CacheManager & others
        @property
        def redis_client(self):  # type: ignore
            return self

    # Nothing else in this module is required for the in-memory variant.
    # Down-stream imports referencing `CacheService` will receive this stub.

else:
    # ---------------------------------------------------------------------
    # Redis implementation (original heavy-duty cache service)
    # ---------------------------------------------------------------------
    from redis.exceptions import ConnectionError
    import redis.asyncio as redis
    from backend.utils.logger_config import get_logger

    logger = get_logger(__name__)

    class CacheService:
        """Enhanced Redis cache service with connection pooling and auto-reconnection"""

        def __init__(
            self,
            host: str = "localhost",
            port: int = 6379,
            db: int = 0,
            default_ttl: int = 300,
            lock_ttl: int = 120,
            lock_retry_delay: float = 0.5,
            max_connections: int = 20,
            retry_on_timeout: bool = True,
            socket_keepalive: bool = True,
            socket_keepalive_options: dict = None,
        ):
            self.host = host
            self.port = port
            self.db = db
            self.default_ttl = default_ttl
            self.lock_ttl = lock_ttl
            self.lock_retry_delay = lock_retry_delay
            self.max_connections = max_connections
            self.retry_on_timeout = retry_on_timeout

            # Enhanced connection options for stability
            self.connection_kwargs = {
                "socket_keepalive": socket_keepalive,
                "socket_keepalive_options": socket_keepalive_options
                or {
                    1: 1,  # TCP_KEEPIDLE
                    2: 3,  # TCP_KEEPINTVL
                    3: 5,  # TCP_KEEPCNT
                },
                "health_check_interval": 30,
                "retry_on_timeout": retry_on_timeout,
                "socket_connect_timeout": 5,
                "socket_timeout": 5,
            }

            self.redis_client: Optional[redis.Redis] = None
            self._connection_pool: Optional[redis.ConnectionPool] = None
            self._last_ping_time = 0
            self._ping_interval = 30  # Ping every 30 seconds
            self._reconnecting = False  # Guard against recursive reconnection

            logger.info(
                f"[CacheService(Redis)] Instance configured with "
                f"Default TTL: {default_ttl}s, Lock TTL: {lock_ttl}s, "
                f"Lock Retry Delay: {lock_retry_delay}s."
            )

        @classmethod
        async def create(
            cls,
            redis_host: str = "localhost",
            redis_port: int = 6379,
            redis_db: int = 0,
            connect_timeout: int = 5,
            socket_op_timeout: int = 5,
            default_ttl: int = 300,
            lock_ttl: int = 120,
            lock_retry_delay: float = 0.5,
            **kwargs,
        ) -> "CacheService":
            """
            Factory method to create and initialize a CacheService instance.

            Args:
                redis_host: Redis server hostname (use 'memory' for in-memory cache)
                redis_port: Redis server port
                redis_db: Redis database number
                connect_timeout: Connection timeout in seconds
                socket_op_timeout: Socket operation timeout in seconds
                default_ttl: Default TTL for cache entries
                lock_ttl: TTL for cache locks
                lock_retry_delay: Delay between lock retry attempts
                **kwargs: Additional connection parameters

            Returns:
                Initialized CacheService instance
            """
            # Special case: return memory cache for development
            if redis_host == "memory":
                logger.info("[CacheService.create] Creating memory cache instance")
                # Import the memory cache implementation
                # Force the import to get the memory version
                import os

                old_env = os.environ.get("FINBOT_CACHE_MODE")
                os.environ["FINBOT_CACHE_MODE"] = "memory"
                try:
                    # Re-import to get memory version
                    import importlib
                    import backend.utils.cache_service as cache_module

                    importlib.reload(cache_module)
                    return await cache_module.CacheService.create()
                finally:
                    if old_env:
                        os.environ["FINBOT_CACHE_MODE"] = old_env
                    else:
                        os.environ.pop("FINBOT_CACHE_MODE", None)

            logger.info(
                f"[CacheService.create] Creating instance for {redis_host}:{redis_port}"
            )

            # Create instance with provided parameters
            instance = cls(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                default_ttl=default_ttl,
                lock_ttl=lock_ttl,
                lock_retry_delay=lock_retry_delay,
                **kwargs,
            )

            # Initialize the connection
            await instance.initialize()

            logger.info(
                "[CacheService.create] Successfully created and initialized instance"
            )
            return instance

        async def initialize(self) -> None:
            """Initialize Redis connection pool with enhanced stability"""
            try:
                logger.info("[CacheService(Redis)] Initializing Redis connection...")

                # Create connection pool with enhanced settings
                self._connection_pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    max_connections=self.max_connections,
                    decode_responses=True,
                    **self.connection_kwargs,
                )

                # Create Redis client with the pool
                self.redis_client = redis.Redis(
                    connection_pool=self._connection_pool, decode_responses=True
                )

                # --- HOTFIX: Disable write stop on RDB snapshot error to avoid MISCONF issues in dev ---
                try:
                    await self.redis_client.config_set(
                        "stop-writes-on-bgsave-error", "no"
                    )
                    logger.info(
                        "[CacheService(Redis)] Applied config: stop-writes-on-bgsave-error=no"
                    )
                except Exception as e:
                    logger.warning(
                        f"[CacheService(Redis)] Could not apply config hotfix: {e}"
                    )

                # Test connection WITHOUT triggering reconnection logic
                await self._test_connection_simple()

                logger.info(
                    f"[CacheService(Redis)] Redis connection successful to "
                    f"{self.host}:{self.port} (DB: {self.db})."
                )

            except Exception as e:
                logger.error(f"[CacheService(Redis)] Failed to initialize: {e}")
                raise

        async def _test_connection_simple(self) -> bool:
            """Simple connection test without reconnection logic"""
            try:
                if self.redis_client:
                    await self.redis_client.ping()
                    return True
            except Exception as e:
                logger.warning(f"[CacheService(Redis)] Connection test failed: {e}")
                return False
            return False

        async def _test_connection(self) -> bool:
            """Test Redis connection"""
            try:
                if self.redis_client:
                    try:
                        await self.redis_client.ping()
                    except AttributeError:
                        logger.warning(
                            "[CacheService(Redis)] AttributeError during ping – treating as connection lost"
                        )
                        raise ConnectionError("Ping AttributeError")
                    return True
            except Exception:
                pass
            return False

        async def _ensure_connection(self) -> bool:
            """Ensure Redis connection is alive with automatic reconnection"""
            current_time = time.time()

            # Check if we need to ping (avoid excessive pings)
            if current_time - self._last_ping_time < self._ping_interval:
                return True

            try:
                if self.redis_client:
                    try:
                        await self.redis_client.ping()
                    except AttributeError as attr_err:
                        # Known bug in redis.asyncio parser object when connection lost
                        logger.warning(
                            f"[CacheService(Redis)] AttributeError during ping: {attr_err}. Reconnecting..."
                        )
                        return False
                    self._last_ping_time = current_time
                    return True
            except Exception as e:
                logger.warning(
                    f"[CacheService(Redis)] Connection lost, attempting reconnection: {e}"
                )
                if not self._reconnecting:
                    await self._reconnect()
                    return await self._test_connection()
                else:
                    logger.warning(
                        "[CacheService(Redis)] Already reconnecting, skipping duplicate attempt"
                    )
                    return False
            except Exception as e:
                logger.error(f"[CacheService(Redis)] Unexpected error during ping: {e}")
                return False

        async def _reconnect(self) -> None:
            """Attempt to reconnect to Redis with guard against recursion"""
            if self._reconnecting:
                logger.warning(
                    "[CacheService(Redis)] Reconnection already in progress, skipping"
                )
                return

            self._reconnecting = True
            try:
                logger.info("[CacheService(Redis)] Starting reconnection process...")

                if self.redis_client:
                    await self.redis_client.close()

                # Recreate connection pool
                if self._connection_pool:
                    await self._connection_pool.disconnect()

                # Reinitialize without triggering _ensure_connection
                self._connection_pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    max_connections=self.max_connections,
                    decode_responses=True,
                    **self.connection_kwargs,
                )

                self.redis_client = redis.Redis(
                    connection_pool=self._connection_pool, decode_responses=True
                )

                # Simple test without reconnection logic
                await self._test_connection_simple()

                logger.info("[CacheService(Redis)] Successfully reconnected to Redis")

            except Exception as e:
                logger.error(f"[CacheService(Redis)] Failed to reconnect: {e}")
                raise
            finally:
                self._reconnecting = False

        async def get(self, key: str) -> Optional[str]:
            """Get value from Redis with automatic reconnection"""
            try:
                await self._ensure_connection()
                if not self.redis_client:
                    return None

                result_str: str | None = await self.redis_client.get(key)
                return result_str

            except Exception as e:
                logger.error(f"[CacheService(Redis)] [GET:{key}] Connection error: {e}")
                # Attempt one reconnection
                try:
                    await self._reconnect()
                    if self.redis_client:
                        result_str = await self.redis_client.get(key)
                        return result_str
                except Exception as reconnect_error:
                    logger.error(
                        f"[CacheService(Redis)] [GET:{key}] Reconnection failed: {reconnect_error}"
                    )
                return None

            except Exception as e:
                logger.error(f"[CacheService(Redis)] [GET:{key}] Error: {e}")
                return None

        async def set(
            self, key: str, value: Union[str, dict, list], ttl: Optional[int] = None
        ) -> bool:
            """Set value in Redis with automatic reconnection"""
            try:
                await self._ensure_connection()
                if not self.redis_client:
                    return False

                ttl = ttl or self.default_ttl

                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, ensure_ascii=False)
                else:
                    value_str = str(value)

                await self.redis_client.setex(key, ttl, value_str)
                return True

            except Exception as e:
                logger.error(f"[CacheService(Redis)] [SET:{key}] Connection error: {e}")
                # Attempt one reconnection
                try:
                    await self._reconnect()
                    if self.redis_client:
                        if isinstance(value, (dict, list)):
                            value_str = json.dumps(value, ensure_ascii=False)
                        else:
                            value_str = str(value)
                        await self.redis_client.setex(
                            key, ttl or self.default_ttl, value_str
                        )
                        return True
                except Exception as reconnect_error:
                    logger.error(
                        f"[CacheService(Redis)] [SET:{key}] Reconnection failed: {reconnect_error}"
                    )
                return False

            except Exception as e:
                logger.error(f"[CacheService(Redis)] [SET:{key}] Error: {e}")
                return False

        async def delete(self, key: str) -> bool:
            """Delete key from Redis"""
            try:
                await self._ensure_connection()
                if not self.redis_client:
                    return False

                result = await self.redis_client.delete(key)
                return bool(result)

            except Exception as e:
                logger.error(f"[CacheService(Redis)] [DELETE:{key}] Error: {e}")
                return False

        async def exists(self, key: str) -> bool:
            """Check if key exists in Redis"""
            try:
                await self._ensure_connection()
                if not self.redis_client:
                    return False

                result = await self.redis_client.exists(key)
                return bool(result)

            except Exception as e:
                logger.error(f"[CacheService(Redis)] [EXISTS:{key}] Error: {e}")
                return False

        async def close(self) -> None:
            """Close Redis connection"""
            try:
                logger.info("[CacheService(Redis)] Closing Redis connection pool...")
                if self.redis_client:
                    await self.redis_client.close()
                if self._connection_pool:
                    await self._connection_pool.disconnect()
            except Exception as e:
                logger.error(f"[CacheService(Redis)] Error closing connection: {e}")


# Global cache instance
cache_service = CacheService()

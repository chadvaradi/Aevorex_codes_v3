"""
Database Connection Pool Manager for FinanceHub
Provides efficient database connections with automatic scaling
"""

import time
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
import asyncpg
from backend.config import settings
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class DatabasePool:
    """Enhanced database connection pool with monitoring and auto-scaling"""

    def __init__(
        self,
        dsn: str,
        min_size: int = 10,
        max_size: int = 50,
        command_timeout: int = 30,
        server_settings: Optional[Dict[str, str]] = None,
    ):
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        self.command_timeout = command_timeout
        self.server_settings = server_settings or {
            "application_name": "financehub_backend",
            "tcp_keepalives_idle": "600",
            "tcp_keepalives_interval": "30",
            "tcp_keepalives_count": "3",
            "statement_timeout": "30000",  # 30 seconds
            "idle_in_transaction_session_timeout": "60000",  # 1 minute
        }

        self.pool: Optional[asyncpg.Pool] = None
        self._stats = {
            "connections_created": 0,
            "connections_closed": 0,
            "queries_executed": 0,
            "total_query_time": 0.0,
            "failed_queries": 0,
            "pool_exhausted_count": 0,
        }

    async def initialize(self) -> None:
        """Initialize the database connection pool"""
        try:
            logger.info(
                f"[DatabasePool] Initializing pool (min: {self.min_size}, max: {self.max_size})"
            )

            self.pool = await asyncpg.create_pool(
                self.dsn,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=self.command_timeout,
                server_settings=self.server_settings,
                init=self._init_connection,
                statement_cache_size=0,  # Disable statement cache for pgBouncer compatibility
            )

            logger.info("[DatabasePool] Pool initialized successfully")

        except Exception as e:
            logger.error(f"[DatabasePool] Failed to initialize: {e}")
            raise

    async def _init_connection(self, connection: asyncpg.Connection) -> None:
        """Initialize new database connections"""
        try:
            # Set up connection-specific settings
            await connection.execute("SET timezone = 'UTC'")
            await connection.execute("SET statement_timeout = '30s'")

            self._stats["connections_created"] += 1
            logger.debug("[DatabasePool] New connection initialized")

        except Exception as e:
            logger.error(f"[DatabasePool] Failed to initialize connection: {e}")
            raise

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a connection from the pool with automatic cleanup"""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")

        start_time = time.time()
        connection = None

        try:
            connection = await self.pool.acquire()
            yield connection

        except asyncpg.exceptions.TooManyConnectionsError:
            self._stats["pool_exhausted_count"] += 1
            logger.warning(
                "[DatabasePool] Pool exhausted, waiting for available connection"
            )
            raise

        except Exception as e:
            logger.error(f"[DatabasePool] Connection error: {e}")
            raise

        finally:
            if connection:
                try:
                    await self.pool.release(connection)
                except Exception as e:
                    logger.error(f"[DatabasePool] Failed to release connection: {e}")

            elapsed = time.time() - start_time
            self._stats["total_query_time"] += elapsed

    async def execute_query(
        self, query: str, *args, timeout: Optional[int] = None
    ) -> Any:
        """Execute a query with connection pooling and error handling"""
        start_time = time.time()

        try:
            async with self.get_connection() as conn:
                result = await conn.fetch(query, *args, timeout=timeout)

            self._stats["queries_executed"] += 1
            elapsed = time.time() - start_time

            if elapsed > 1.0:  # Log slow queries
                logger.warning(
                    f"[DatabasePool] Slow query ({elapsed:.2f}s): {query[:100]}..."
                )

            return result

        except Exception as e:
            self._stats["failed_queries"] += 1
            logger.error(f"[DatabasePool] Query failed: {e}")
            raise

    async def execute_transaction(
        self, queries: list, timeout: Optional[int] = None
    ) -> list:
        """Execute multiple queries in a transaction"""
        start_time = time.time()
        results = []

        try:
            async with self.get_connection() as conn:
                async with conn.transaction():
                    for query, args in queries:
                        result = await conn.fetch(query, *args, timeout=timeout)
                        results.append(result)

            self._stats["queries_executed"] += len(queries)
            elapsed = time.time() - start_time

            logger.debug(
                f"[DatabasePool] Transaction completed ({elapsed:.2f}s, {len(queries)} queries)"
            )
            return results

        except Exception as e:
            self._stats["failed_queries"] += len(queries)
            logger.error(f"[DatabasePool] Transaction failed: {e}")
            raise

    async def get_pool_stats(self) -> Dict[str, Any]:
        """Get connection pool statistics"""
        if not self.pool:
            return {}

        pool_stats = {
            "size": self.pool.get_size(),
            "min_size": self.pool.get_min_size(),
            "max_size": self.pool.get_max_size(),
            "idle_connections": self.pool.get_idle_size(),
            "connections_in_use": self.pool.get_size() - self.pool.get_idle_size(),
        }

        # Add custom stats
        pool_stats.update(self._stats)

        # Calculate averages
        if self._stats["queries_executed"] > 0:
            pool_stats["avg_query_time"] = (
                self._stats["total_query_time"] / self._stats["queries_executed"]
            )
            pool_stats["success_rate"] = (
                (self._stats["queries_executed"] - self._stats["failed_queries"])
                / self._stats["queries_executed"]
            ) * 100
        else:
            pool_stats["avg_query_time"] = 0
            pool_stats["success_rate"] = 100

        return pool_stats

    async def health_check(self) -> bool:
        """Check database connectivity and pool health"""
        try:
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return True

        except Exception as e:
            logger.error(f"[DatabasePool] Health check failed: {e}")
            return False

    async def close(self) -> None:
        """Close all connections in the pool"""
        try:
            if self.pool:
                await self.pool.close()
                self._stats["connections_closed"] = self._stats["connections_created"]
                logger.info("[DatabasePool] Pool closed successfully")

        except Exception as e:
            logger.error(f"[DatabasePool] Error closing pool: {e}")


class TimescaleDBPool(DatabasePool):
    """Specialized pool for TimescaleDB with time-series optimizations"""

    def __init__(self, dsn: str, **kwargs):
        # TimescaleDB specific settings
        timescale_settings = {
            "application_name": "financehub_timescale",
            "tcp_keepalives_idle": "600",
            "tcp_keepalives_interval": "30",
            "tcp_keepalives_count": "3",
            "statement_timeout": "60000",  # Longer timeout for analytical queries
            "work_mem": "256MB",  # More memory for complex queries
            "effective_cache_size": "1GB",
        }

        kwargs["server_settings"] = timescale_settings
        super().__init__(dsn, **kwargs)

    async def _init_connection(self, connection: asyncpg.Connection) -> None:
        """Initialize TimescaleDB connection with optimizations"""
        await super()._init_connection(connection)

        # Enable TimescaleDB specific optimizations
        await connection.execute("SET timescaledb.telemetry_level = 'off'")
        await connection.execute("SET max_parallel_workers_per_gather = 4")

    async def insert_time_series_data(
        self, table: str, data: list, batch_size: int = 1000
    ) -> int:
        """Optimized batch insert for time-series data"""
        total_inserted = 0

        try:
            async with self.get_connection() as conn:
                for i in range(0, len(data), batch_size):
                    batch = data[i : i + batch_size]

                    # Use COPY for better performance
                    await conn.copy_records_to_table(
                        table,
                        records=batch,
                        columns=list(batch[0].keys()) if batch else [],
                    )

                    total_inserted += len(batch)

            logger.info(f"[TimescaleDB] Inserted {total_inserted} records into {table}")
            return total_inserted

        except Exception as e:
            logger.error(f"[TimescaleDB] Batch insert failed: {e}")
            raise


# Global pool instances
main_db_pool = DatabasePool(dsn=settings.DATABASE_URL, min_size=10, max_size=50)

# TimescaleDB pool for time-series data
timescale_pool = (
    TimescaleDBPool(dsn=settings.TIMESCALE_URL, min_size=5, max_size=20)
    if hasattr(settings, "TIMESCALE_URL")
    else None
)

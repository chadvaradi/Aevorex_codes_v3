"""
Redis Cluster Management for FinanceHub
Provides high availability and horizontal scaling for cache layer
"""

import asyncio
import json
import pickle
import zlib
from typing import Any, Optional, List, Dict
from redis.asyncio.cluster import RedisCluster
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class RedisClusterManager:
    """Enhanced Redis Cluster manager with compression and failover"""

    def __init__(
        self,
        cluster_nodes: List[Dict[str, Any]],
        max_connections_per_node: int = 20,
        retry_on_cluster_down: bool = True,
        health_check_interval: int = 30,
        compression_threshold: int = 1024,  # Compress data larger than 1KB
    ):
        self.cluster_nodes = cluster_nodes
        self.max_connections_per_node = max_connections_per_node
        self.retry_on_cluster_down = retry_on_cluster_down
        self.health_check_interval = health_check_interval
        self.compression_threshold = compression_threshold

        self.cluster: Optional[RedisCluster] = None
        self._health_check_task: Optional[asyncio.Task] = None

    async def initialize(self) -> None:
        """Initialize Redis cluster connection"""
        try:
            logger.info(
                f"[RedisCluster] Initializing cluster with {len(self.cluster_nodes)} nodes"
            )

            self.cluster = RedisCluster(
                startup_nodes=self.cluster_nodes,
                decode_responses=False,  # We handle encoding manually
                skip_full_coverage_check=True,
                max_connections_per_node=self.max_connections_per_node,
                retry_on_cluster_down=self.retry_on_cluster_down,
                health_check_interval=self.health_check_interval,
                socket_keepalive=True,
                socket_keepalive_options={1: 1, 2: 3, 3: 5},
                retry_on_timeout=True,
            )

            # Test cluster connectivity
            await self.cluster.ping()
            logger.info("[RedisCluster] Successfully connected to Redis cluster")

            # Start health monitoring
            self._health_check_task = asyncio.create_task(self._health_monitor())

        except Exception as e:
            logger.error(f"[RedisCluster] Failed to initialize: {e}")
            raise

    async def _health_monitor(self) -> None:
        """Background task to monitor cluster health"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                if self.cluster:
                    await self.cluster.ping()
                    logger.debug("[RedisCluster] Health check passed")
            except Exception as e:
                logger.warning(f"[RedisCluster] Health check failed: {e}")

    def _should_compress(self, data: bytes) -> bool:
        """Determine if data should be compressed"""
        return len(data) > self.compression_threshold

    def _serialize_and_compress(self, value: Any) -> bytes:
        """Serialize value and optionally compress"""
        # Serialize
        if isinstance(value, (dict, list)):
            serialized = json.dumps(value, ensure_ascii=False).encode("utf-8")
        elif isinstance(value, str):
            serialized = value.encode("utf-8")
        else:
            serialized = pickle.dumps(value)

        # Compress if beneficial
        if self._should_compress(serialized):
            compressed = zlib.compress(serialized, level=6)
            # Only use compression if it actually reduces size
            if len(compressed) < len(serialized):
                return b"COMPRESSED:" + compressed

        return b"RAW:" + serialized

    def _decompress_and_deserialize(self, data: bytes) -> Any:
        """Decompress and deserialize value"""
        if data.startswith(b"COMPRESSED:"):
            # Decompress
            compressed_data = data[11:]  # Remove 'COMPRESSED:' prefix
            decompressed = zlib.decompress(compressed_data)
        elif data.startswith(b"RAW:"):
            decompressed = data[4:]  # Remove 'RAW:' prefix
        else:
            # Legacy data without prefix
            decompressed = data

        # Deserialize
        try:
            # Try JSON first
            return json.loads(decompressed.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            try:
                # Try pickle
                return pickle.loads(decompressed)
            except Exception:
                # Return as string
                return decompressed.decode("utf-8", errors="ignore")

    async def set_with_compression(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value with automatic compression for large objects"""
        try:
            if not self.cluster:
                logger.error("[RedisCluster] Cluster not initialized")
                return False

            processed_data = self._serialize_and_compress(value)
            await self.cluster.setex(key, ttl, processed_data)

            logger.debug(
                f"[RedisCluster] SET {key} (size: {len(processed_data)} bytes)"
            )
            return True

        except Exception as e:
            logger.error(f"[RedisCluster] SET failed for {key}: {e}")
            return False

    async def get_with_decompression(self, key: str) -> Optional[Any]:
        """Get and automatically decompress value"""
        try:
            if not self.cluster:
                logger.error("[RedisCluster] Cluster not initialized")
                return None

            data = await self.cluster.get(key)
            if not data:
                return None

            result = self._decompress_and_deserialize(data)
            logger.debug(f"[RedisCluster] GET {key} (size: {len(data)} bytes)")
            return result

        except Exception as e:
            logger.error(f"[RedisCluster] GET failed for {key}: {e}")
            return None

    async def mget_with_decompression(self, keys: List[str]) -> Dict[str, Any]:
        """Multi-get with decompression"""
        try:
            if not self.cluster:
                return {}

            values = await self.cluster.mget(keys)
            result = {}

            for key, data in zip(keys, values):
                if data:
                    try:
                        result[key] = self._decompress_and_deserialize(data)
                    except Exception as e:
                        logger.warning(
                            f"[RedisCluster] Failed to deserialize {key}: {e}"
                        )

            return result

        except Exception as e:
            logger.error(f"[RedisCluster] MGET failed: {e}")
            return {}

    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern across cluster"""
        try:
            if not self.cluster:
                return 0

            # Get all keys matching pattern from all nodes
            keys = []
            for node in self.cluster.get_nodes():
                try:
                    node_keys = await node.keys(pattern)
                    keys.extend(node_keys)
                except Exception as e:
                    logger.warning(f"[RedisCluster] Failed to get keys from node: {e}")

            if keys:
                deleted = await self.cluster.delete(*keys)
                logger.info(f"[RedisCluster] Deleted {deleted} keys matching {pattern}")
                return deleted

            return 0

        except Exception as e:
            logger.error(f"[RedisCluster] DELETE pattern failed: {e}")
            return 0

    async def get_cluster_info(self) -> Dict[str, Any]:
        """Get cluster information and statistics"""
        try:
            if not self.cluster:
                return {}

            info = {}
            nodes = self.cluster.get_nodes()

            for i, node in enumerate(nodes):
                try:
                    node_info = await node.info()
                    info[f"node_{i}"] = {
                        "host": node.host,
                        "port": node.port,
                        "used_memory": node_info.get("used_memory_human"),
                        "connected_clients": node_info.get("connected_clients"),
                        "total_commands_processed": node_info.get(
                            "total_commands_processed"
                        ),
                        "keyspace_hits": node_info.get("keyspace_hits"),
                        "keyspace_misses": node_info.get("keyspace_misses"),
                    }
                except Exception as e:
                    logger.warning(
                        f"[RedisCluster] Failed to get info from node {i}: {e}"
                    )

            return info

        except Exception as e:
            logger.error(f"[RedisCluster] Failed to get cluster info: {e}")
            return {}

    async def close(self) -> None:
        """Close cluster connections"""
        try:
            if self._health_check_task:
                self._health_check_task.cancel()

            if self.cluster:
                await self.cluster.close()
                logger.info("[RedisCluster] Cluster connections closed")

        except Exception as e:
            logger.error(f"[RedisCluster] Error closing cluster: {e}")


# Example cluster configuration
REDIS_CLUSTER_NODES = [
    {"host": "redis-node-1", "port": 7000},
    {"host": "redis-node-2", "port": 7001},
    {"host": "redis-node-3", "port": 7002},
    {"host": "redis-node-4", "port": 7003},
    {"host": "redis-node-5", "port": 7004},
    {"host": "redis-node-6", "port": 7005},
]

# Global cluster instance
cluster_manager = RedisClusterManager(REDIS_CLUSTER_NODES)

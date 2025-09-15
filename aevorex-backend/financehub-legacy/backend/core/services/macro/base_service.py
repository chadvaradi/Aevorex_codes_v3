"""Base service class providing cache-aware helper and common clients.
Keeps LOC ~80, no business fetch logic here.
"""

from __future__ import annotations

import json
from typing import Callable, Dict

from backend.utils.cache_service import CacheService
from backend.core.fetchers.macro.ecb_client import (
    ECBSDMXClient,
    ECBAPIError,
)
from backend.core.fetchers.macro.ecb_client.specials.bubor_client import (
    BUBORClient,
    BUBORAPIError,
)
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class BaseMacroService:
    """Common constructor + cache-aware fetch wrapper used by mixins."""

    def __init__(self, cache_service: CacheService | None = None):
        self._cache: CacheService | None = cache_service
        self.ecb_client = ECBSDMXClient(cache_service)
        self.bubor_client = BUBORClient(cache_service)

    # -----------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------
    async def _get_with_cache_fallback(
        self,
        fetch_func: Callable[[], Dict],
        cache_key: str,
    ) -> Dict:
        """Run *fetch_func*; on API-error serve cached copy if available."""
        try:
            return await fetch_func()
        except (ECBAPIError, BUBORAPIError) as exc:
            logger.error("API fetch failed for %s: %s", cache_key, exc, exc_info=True)
            try:
                from backend.config import settings

                prod = settings.ENVIRONMENT.NODE_ENV == "production"
            except Exception:
                prod = False
            if not prod and self._cache:
                cached = await self._cache.get(cache_key)
                if cached:
                    logger.warning("Serving stale data for %s (dev only)", cache_key)
                    return json.loads(cached)
            logger.error("No cache available for %s", cache_key)
            return {}

    # convenience import for public typing
    from typing import Dict as _DictAlias  # noqa: F401

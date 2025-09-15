"""
Macro Cache Service
===================

Központi cache wrapper a makrogazdasági adatokhoz.
Az egyes adatforrásokhoz (ECB, FRED, BUBOR, Euribor) külön TTL szabályokat definiál.
"""

from __future__ import annotations
from typing import Any, Optional
import structlog
from backend.utils.cache_service import CacheService

logger = structlog.get_logger()


class MacroCacheService:
    """
    Cache service a makrogazdasági modulhoz.
    TTL szabályokat biztosít forrásonként.
    """

    # Default TTL beállítások másodpercben
    TTL_SETTINGS: dict[str, int] = {
        "ecb_policy_rates": 3600,      # 1 óra
        "ecb_fx_rates": 3600,          # 1 óra
        "ecb_historical": 86400,       # 24 óra
        "bubor_curve": 1800,           # 30 perc
        "bubor_historical": 86400,     # 24 óra
        "euribor_rates": 86400,        # 24 óra (mert T-1 delay van)
        "fred_series": 43200,          # 12 óra
        "fred_search": 43200,          # 12 óra
        "generic_macro": 3600,         # fallback TTL
    }

    def __init__(self, cache: CacheService):
        self.cache = cache

    async def get(self, key: str) -> Optional[Any]:
        """Olvasás cache-ből, logolással."""
        value = await self.cache.get(key)
        if value is not None:
            logger.info("macro_cache_hit", key=key)
        return value

    async def set(self, key: str, value: Any) -> None:
        """Mentés cache-be, TTL szabállyal."""
        prefix = key.split(":")[0]
        ttl = self.TTL_SETTINGS.get(prefix, self.TTL_SETTINGS["generic_macro"])
        await self.cache.set(key, value, ttl=ttl)
        logger.info("macro_cache_set", key=key, ttl=ttl)

    async def cached_fetch(self, key: str, fetch_func, *args, **kwargs) -> Any:
        """
        Wrapper: először cache-ből próbál olvasni, ha nincs,
        meghívja a fetch_func-ot és elmenti az eredményt.
        """
        cached = await self.get(key)
        if cached:
            return cached

        fresh = await fetch_func(*args, **kwargs)
        await self.set(key, fresh)
        return fresh
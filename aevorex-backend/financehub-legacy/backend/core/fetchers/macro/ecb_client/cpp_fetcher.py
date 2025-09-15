"""ECB Central Bank Operations (CPP) fetcher – thin wrapper to generic fetcher."""

from __future__ import annotations

from datetime import date
from typing import Dict, Optional

from backend.utils.cache_service import CacheService
from .config import ECB_DATAFLOWS
from .generic_fetcher import fetch_ecb_data


async def fetch_ecb_cpp_data(
    cache: CacheService | None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """Fetch ECB CPP data via generic fetcher."""
    config = ECB_DATAFLOWS["cpp"]
    return await fetch_ecb_data(
        cache=cache,
        dataflow=config["dataflow"],
        series=config["series"],
        start=start_date,
        end=end_date,
        cache_ttl=86400,
    )

"""Generic multi-series ECB SDMX fetcher.

Avoids code duplication for new dataflows (SEC, IVF, CBD ...). Strictly live –
no mock or static fallbacks.  Returns `{date: {label: value}}` aggregated across
all requested series.
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from typing import Dict, List, Tuple, Optional

import structlog

from .client import ECBSDMXClient
from .exceptions import ECBAPIError
from backend.utils.cache_service import CacheService

logger = structlog.get_logger(__name__)


async def fetch_multi_series(
    cache: CacheService | None,
    dataflow: str,
    series_list: List[Tuple[str, str]],
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    cache_ttl: int = 3600,
) -> Dict[str, Dict[str, float]]:
    """Download multiple series in parallel and merge into `{date: {label: val}}`.

    Args:
        cache: optional cache backend
        dataflow: ECB SDMX dataflow code (e.g. "SEC")
        series_list: list of (label, series_key)
        start_date: defaults 5Y window
        end_date: defaults today
        cache_ttl: seconds
    """
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=365 * 5)

    cache_key = f"ecb:{dataflow}:{start_date}:{end_date}"
    if cache:
        cached = await cache.get(cache_key)
        if cached:
            logger.debug("%s cache HIT", dataflow)
            return cached  # type: ignore[return-value]

    client = ECBSDMXClient(cache)
    combined: Dict[str, Dict[str, float]] = {}
    try:
        from .parsers import parse_ecb_comprehensive_json  # local import

        for label, key in series_list:
            try:
                payload = await client.http_client.download_ecb_sdmx(
                    dataflow,
                    key,
                    start_date,
                    end_date,
                )
                parsed = parse_ecb_comprehensive_json(payload, label)
                for d, val in parsed.items():
                    combined.setdefault(d, {})[label] = val
            except Exception as exc:
                logger.warning("%s series fetch failed: %s", dataflow, exc)
                # continue with other series instead of total failure
            await asyncio.sleep(0.15)

        if cache and combined:
            await cache.set(cache_key, combined, ttl=cache_ttl)
        return combined
    except Exception as exc:
        logger.error("Generic fetch error for %s: %s", dataflow, exc)
        raise ECBAPIError(f"Failed to fetch {dataflow} data: {exc}") from exc
    finally:
        await client.close()


async def fetch_ecb_data(
    cache: CacheService | None,
    dataflow: str,
    series: List[Tuple[str, str]],
    start: Optional[date] = None,
    end: Optional[date] = None,
    cache_ttl: int = 3600,
) -> Dict[str, Dict[str, float]]:
    """
    Generic ECB data fetcher using configuration-driven approach.

    Args:
        cache: Cache service instance
        dataflow: ECB dataflow name (e.g., 'hicp', 'bls', 'cbd')
        series: List of (label, series_key) tuples
        start: Start date for data
        end: End date for data
        cache_ttl: Cache TTL in seconds

    Returns:
        Dictionary with data by date and series
    """
    return await fetch_multi_series(
        cache=cache,
        dataflow=dataflow,
        series_list=series,
        start_date=start,
        end_date=end,
        cache_ttl=cache_ttl,
    )

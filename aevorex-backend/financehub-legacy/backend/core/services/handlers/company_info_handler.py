"""
Company Info Handler (real EODHD implementation)
===============================================

Valós céginformáció-lekérés az EODHD API-ból.
"""

import httpx
from typing import Dict, Any, Optional
from ....utils.cache_service import CacheService
from ....utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.CompanyInfoHandler")

EODHD_BASE_URL = "https://eodhd.com/api"


async def fetch_company_info(
    symbol: str,
    client: httpx.AsyncClient,
    cache: CacheService,
    request_id: str | None = None,
    api_key: str | None = None,
) -> Optional[Dict[str, Any]]:
    """
    Fetch company information from EODHD.

    Args:
        symbol: Stock ticker (e.g. "AAPL.US")
        client: Shared httpx.AsyncClient
        cache: CacheService instance
        request_id: Optional request trace ID
        api_key: Your EODHD API key (required)

    Returns:
        Dictionary with company information, or None if unavailable
    """
    log_prefix = f"[CompanyInfo:{symbol}]"
    cache_key = f"company_info_{symbol}"

    # Try cache first
    cached = await cache.get(cache_key)
    if cached:
        logger.info(f"{log_prefix} Cache HIT")
        return cached

    if not api_key:
        logger.error(f"{log_prefix} No API key provided.")
        return None

    url = f"{EODHD_BASE_URL}/fundamentals/{symbol}"
    params = {"api_token": api_key, "fmt": "json"}

    try:
        logger.info(f"{log_prefix} Fetching from EODHD...")
        resp = await client.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()

        # Extract relevant fields
        overview = data.get("General", {})
        company_info = {
            "symbol": symbol,
            "name": overview.get("Name"),
            "description": overview.get("Description"),
            "industry": overview.get("Industry"),
            "sector": overview.get("Sector"),
            "country": overview.get("CountryName"),
            "website": overview.get("WebURL"),
            "employees": overview.get("FullTimeEmployees"),
            "market_cap": overview.get("MarketCapitalization"),
            "status": "ok",
        }

        # Cache for 1 hour
        await cache.set(cache_key, company_info, ttl=3600)

        logger.info(f"{log_prefix} Success")
        return company_info

    except Exception as e:
        logger.error(f"{log_prefix} Failed to fetch company info: {e}")
        return None

"""
Technical Calculation Service
"""

import logging

import httpx
from backend.utils.cache_service import CacheService
from backend.core.orchestrator import StockOrchestrator

logger = logging.getLogger(__name__)


async def calculate_technical_analysis(
    symbol: str,
    cache: CacheService,
    http_client: httpx.AsyncClient,
    orchestrator: StockOrchestrator,
    force_refresh: bool,
    request_id: str,
):
    """
    Calculates technical analysis data with parallel fetching and caching.
    """
    cache_key = f"indicators:v2:{symbol}:optimized"
    if not force_refresh:
        cached_result = await cache.get(cache_key)
        if cached_result:
            return cached_result, True

    logger.info(f"[{request_id}] 🔄 Cache MISS, using parallel fetch")
    _, technical_indicators, _, ohlcv_df = await orchestrator.fetch_parallel_data(
        symbol=symbol,
        client=http_client,
        cache=cache,
        request_id=request_id,
        force_refresh=force_refresh,
    )

    if not technical_indicators:
        logger.warning(
            f"[{request_id}] ⚠️ No technical indicators returned from parallel fetch"
        )
        technical_indicators = {}

    return technical_indicators, ohlcv_df

"""
Handler for fetching news data.
"""

import asyncio
from typing import Any
import httpx

from ....utils.cache_service import CacheService
from ....core import fetchers
from ....utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.handlers.news_data")


async def fetch_news_data(
    symbol: str,
    client: httpx.AsyncClient,
    cache: CacheService,
    request_id: str,
    limit: int = 10,
) -> list[dict[str, Any]] | None:
    """Fetch news data from multiple sources."""
    try:
        yfinance_fetcher = await fetchers.get_fetcher("yfinance", client, cache)
        # marketaux_fetcher = fetchers.get_fetcher("marketaux", cache)

        tasks = [
            yfinance_fetcher.fetch_news(ticker=symbol),
            # marketaux_fetcher.fetch_news(ticker=symbol),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results from successful fetches
        all_news = []
        for result in results:
            if isinstance(result, list) and result:
                all_news.extend(result)

        # Sort by date and limit
        if all_news:
            # Note: The sorting key might need to be standardized if different APIs use different keys
            sorted_news = sorted(
                all_news,
                key=lambda x: x.get("published_utc", x.get("publishedAt", "")),
                reverse=True,
            )
            return sorted_news[:limit]

        logger.warning(f"[{request_id}] No news data found for {symbol}")
        return None

    except Exception as e:
        logger.error(
            f"[{request_id}] News fetch error for {symbol}: {e}", exc_info=True
        )
        return None

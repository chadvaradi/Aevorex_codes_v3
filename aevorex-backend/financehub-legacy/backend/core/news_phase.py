"""
News Phase Module - News Data Fetching and Processing

This module handles all news-related data fetching and processing
that were previously part of the monolithic stock_data_service.py.
"""

import httpx
from typing import List
from backend.models import NewsItem
from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.core.fetchers.eodhd import EODHDFetcher

logger = get_logger("aevorex_finbot.NewsPhase")
__all__ = ["get_news_data"]


async def get_news_data(
    symbol: str, client: httpx.AsyncClient, cache: CacheService, limit: int = 10
) -> List[NewsItem]:
    """
    Fetches news from the primary provider and maps it to the NewsItem model.
    """
    log_prefix = f"[NewsPhase:{symbol}]"
    logger.info(f"{log_prefix} Fetching news data.")
    try:
        fetcher = EODHDFetcher(cache=cache, client=client)
        news_items = await fetcher.fetch_news(symbol=symbol, limit=limit)
        if not news_items:
            logger.info(f"{log_prefix} No news found.")
            return []
        logger.info(
            f"{log_prefix} Successfully processed {len(news_items)} news items."
        )
        return news_items
    except Exception as e:
        logger.error(
            f"{log_prefix} An error occurred while fetching or processing news: {e}",
            exc_info=True,
        )
        return []

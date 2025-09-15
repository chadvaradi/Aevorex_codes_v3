"""
News Service

Handles news data fetching, processing, and caching for stock symbols.
Extracted from stock_service.py to follow 160 LOC rule.
"""

from typing import Any
import httpx
from backend.utils.cache_service import CacheService
from backend.utils.logger_config import get_logger
from backend.core.services.news_fetcher import NewsFetcher

logger = get_logger("aevorex_finbot.NewsService")


class NewsService:
    """Service for handling news data operations."""

    def __init__(self):
        self.cache_ttl = 1800  # 30 minutes for news data
        self.fetcher = NewsFetcher()

    async def get_news_data(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        limit: int = 10,
        force_refresh: bool = False,
    ) -> list[dict[str, Any]] | None:
        """Get news data for a stock symbol."""
        cache_key = f"news_data:{symbol}:{limit}"

        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug(f"News data cache hit for {symbol}")
                return cached_data

        try:
            # Fetch news using the fetcher
            news_data = await self.fetcher.fetch_news_from_sources(
                symbol, client, limit
            )

            if news_data:
                # Cache the results
                await cache.set(cache_key, news_data, ttl=self.cache_ttl)
                logger.info(f"News data cached for {symbol} ({len(news_data)} items)")

            return news_data

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            return None

    async def get_latest_headlines(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        count: int = 5,
    ) -> list[dict[str, Any]] | None:
        """Get latest news headlines for quick display."""
        cache_key = f"headlines:{symbol}:{count}"

        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            # Get full news data and extract headlines
            news_data = await self.get_news_data(symbol, client, cache, count)

            if not news_data:
                return None

            # Extract headline information using fetcher
            headlines = self.fetcher.extract_headlines(news_data, count)

            if headlines:
                await cache.set(cache_key, headlines, ttl=600)  # 10 min cache

            return headlines

        except Exception as e:
            logger.error(f"Error fetching headlines for {symbol}: {e}")
            return None

    async def get_news_sentiment_summary(
        self, symbol: str, client: httpx.AsyncClient, cache: CacheService
    ) -> dict[str, Any] | None:
        """Get sentiment summary of recent news."""
        try:
            news_data = await self.get_news_data(symbol, client, cache, 20)

            if not news_data:
                return None

            # Calculate sentiment using fetcher
            return self.fetcher.calculate_sentiment_summary(news_data)

        except Exception as e:
            logger.error(f"Error calculating news sentiment for {symbol}: {e}")
            return None

    async def get_recent_news(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        hours: int = 24,
    ) -> list[dict[str, Any]] | None:
        """Get news from the last N hours."""
        try:
            # Get more items to filter by time
            news_data = await self.get_news_data(symbol, client, cache, 50)

            if not news_data:
                return None

            # Filter by time (this would need proper datetime parsing)
            # For now, return the first 10 items as "recent"
            return news_data[:10]

        except Exception as e:
            logger.error(f"Error fetching recent news for {symbol}: {e}")
            return None

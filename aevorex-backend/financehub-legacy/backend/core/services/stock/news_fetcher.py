"""
News Fetcher - Handles news data fetching from multiple sources.
Split from news_service.py to maintain 160 LOC limit.
"""

from typing import Any
import httpx
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.NewsFetcher")


class NewsFetcher:
    """Handles fetching news from multiple sources."""

    async def fetch_news_from_sources(
        self, symbol: str, client: httpx.AsyncClient, limit: int
    ) -> list[dict[str, Any]] | None:
        """Fetch news from multiple sources and aggregate results."""
        try:
            # Use existing news fetchers
            from ....core import fetchers

            # Try multiple sources and aggregate
            news_items = []

            # Try NewsAPI first
            try:
                newsapi_data = await fetchers.newsapi.fetch_news(symbol, client, limit)
                if newsapi_data:
                    news_items.extend(newsapi_data)
            except Exception as e:
                logger.warning(f"NewsAPI fetch failed for {symbol}: {e}")

            # Try MarketAux if we need more items
            if len(news_items) < limit:
                try:
                    marketaux_data = await fetchers.marketaux.fetch_news(
                        symbol, client, limit - len(news_items)
                    )
                    if marketaux_data:
                        news_items.extend(marketaux_data)
                except Exception as e:
                    logger.warning(f"MarketAux fetch failed for {symbol}: {e}")

            # Sort by published date (newest first)
            if news_items:
                news_items.sort(key=lambda x: x.get("published_at", ""), reverse=True)
                return news_items[:limit]

            return None

        except Exception as e:
            logger.error(f"Error fetching news from sources for {symbol}: {e}")
            return None

    def calculate_sentiment_summary(
        self, news_data: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Calculate sentiment summary from news data."""
        if not news_data:
            return {}

        # Calculate sentiment distribution
        sentiment_counts = {"positive": 0, "neutral": 0, "negative": 0}
        total_relevance = 0

        for item in news_data:
            sentiment = item.get("sentiment", "neutral")
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1

            relevance = item.get("relevance_score", 0.5)
            total_relevance += relevance

        total_items = len(news_data)
        avg_relevance = total_relevance / total_items if total_items > 0 else 0

        return {
            "sentiment_distribution": sentiment_counts,
            "total_articles": total_items,
            "average_relevance": avg_relevance,
            "dominant_sentiment": max(sentiment_counts, key=sentiment_counts.get),
        }

    def extract_headlines(
        self, news_data: list[dict[str, Any]], count: int
    ) -> list[dict[str, Any]]:
        """Extract headline information from news data."""
        headlines = []
        for item in news_data[:count]:
            headline = {
                "title": item.get("title", ""),
                "published_at": item.get("published_at", ""),
                "sentiment": item.get("sentiment", "neutral"),
                "source": item.get("source", ""),
                "url": item.get("url", ""),
            }
            headlines.append(headline)
        return headlines

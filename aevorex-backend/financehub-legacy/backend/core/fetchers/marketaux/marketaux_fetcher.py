"""
MarketAux API Fetcher Module.
This module is responsible for fetching news data from the MarketAux API,
caching responses, and performing basic response processing.
"""

from typing import List, Optional
import httpx
import structlog
from backend.core.fetchers.common.base_fetcher import BaseFetcher
from backend.models import stock as sm

# Use absolute imports for robustness and remove the try-except logic

MARKETAUX_FETCHER_LOGGER = structlog.get_logger(__name__)

DEFAULT_NEWS_RAW_FETCH_TTL = 900
DEFAULT_NEWS_FETCH_LIMIT = 25
MARKETAUX_API_KEY_NAME = "MARKETAUX"


class MarketAuxFetcher(BaseFetcher):
    """
    Fetcher for MarketAux API.
    """

    def __init__(self, http_client: httpx.AsyncClient, cache_service, api_key: str):
        super().__init__(http_client, cache_service, api_key)
        self.logger = MARKETAUX_FETCHER_LOGGER
        self.base_url = "https://api.marketaux.com"

    async def fetch_ohlcv(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[sm.CompanyPriceHistoryEntry]:
        raise NotImplementedError("MarketAux does not provide OHLCV data.")

    async def fetch_quote(self, symbol: str) -> Optional[sm.LatestOHLCV]:
        raise NotImplementedError("MarketAux does not provide quote data.")

    async def fetch_fundamentals(self, symbol: str) -> Optional[sm.CompanyOverview]:
        raise NotImplementedError("MarketAux does not provide fundamentals data.")

    async def fetch_news(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> List[sm.NewsItem]:
        log_prefix = f"[MarketAux-News:{symbol}]"
        self.logger.info(f"{log_prefix} Fetch request received.")

        cache_key = self._generate_cache_key(f"news_{symbol}_{limit}")

        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            self.logger.info(f"{log_prefix} Cache HIT.")
            return cached_data

        self.logger.info(f"{log_prefix} Cache MISS. Fetching live data.")

        api_params = {
            "api_token": self.api_key,
            "symbols": symbol.upper(),
            "language": "en",
            "limit": limit,
        }
        url = f"{self.base_url}/v1/news/all"

        response = await self._make_api_request(
            method="GET",
            url=url,
            params=api_params,
        )

        if (
            not response
            or "data" not in response
            or not isinstance(response["data"], list)
        ):
            self.logger.warning(
                f"{log_prefix} Invalid or empty response from MarketAux."
            )
            await self._set_failed_cache(cache_key)
            return []

        news_articles = self._parse_news(response["data"])

        await self._set_to_cache(cache_key, news_articles, ttl=900)

        return news_articles

    def _parse_news(self, feed: List[dict]) -> List[sm.NewsItem]:
        parsed_articles = []
        for item in feed:
            try:
                # MarketAux has a different structure
                article = sm.NewsItem(
                    id=item.get("uuid"),
                    title=item.get("title"),
                    publisher=item.get("source"),
                    link=item.get("url"),
                    published_utc=item.get("published_at"),
                    tickers=[e.get("symbol") for e in item.get("entities", [])],
                    summary=item.get("snippet"),
                    image_url=item.get("image_url"),
                )
                parsed_articles.append(article)
            except Exception as e:
                self.logger.warning(f"Failed to parse news item: {item}. Error: {e}")
        return parsed_articles

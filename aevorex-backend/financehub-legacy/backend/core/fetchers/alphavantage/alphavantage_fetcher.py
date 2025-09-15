from typing import List, Optional
import httpx
import structlog
from backend.core.fetchers.common.base_fetcher import BaseFetcher
from backend.models import stock as sm

ALPHAVANTAGE_FETCHER_LOGGER = structlog.get_logger(__name__)


class AlphaVantageFetcher(BaseFetcher):
    """
    Fetcher for Alpha Vantage API.
    """

    def __init__(self, http_client: httpx.AsyncClient, cache_service, api_key: str):
        super().__init__(http_client, cache_service, api_key)
        self.logger = ALPHAVANTAGE_FETCHER_LOGGER

    async def fetch_ohlcv(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[sm.CompanyPriceHistoryEntry]:
        raise NotImplementedError("AlphaVantage OHLCV fetching is not yet implemented.")

    async def fetch_quote(self, symbol: str) -> Optional[sm.LatestOHLCV]:
        raise NotImplementedError("AlphaVantage quote fetching is not yet implemented.")

    async def fetch_fundamentals(self, symbol: str) -> Optional[sm.CompanyOverview]:
        raise NotImplementedError(
            "AlphaVantage fundamentals fetching is not yet implemented."
        )

    async def fetch_news(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> List[sm.NewsItem]:
        """Fetches raw news and sentiment data from the Alpha Vantage API."""
        log_prefix = f"[AlphaVantage-News:{symbol}]"
        self.logger.info(f"{log_prefix} Fetch request received.")

        # This fetcher doesn't use from_date/to_date, but they are part of the interface
        cache_key = self._generate_cache_key(f"news_{symbol}_{limit}")

        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            self.logger.info(f"{log_prefix} Cache HIT.")
            # Assuming cached_data is already parsed into NewsItem models
            return cached_data

        self.logger.info(f"{log_prefix} Cache MISS. Fetching live data.")

        api_params = {
            "function": "NEWS_SENTIMENT",
            "tickers": symbol.upper(),
            "limit": limit,
            "apikey": self.api_key,
        }

        response = await self._make_api_request(
            method="GET",
            url="https://www.alphavantage.co/query",  # Using base URL directly
            params=api_params,
        )

        if (
            not response
            or "feed" not in response
            or not isinstance(response["feed"], list)
        ):
            self.logger.warning(f"{log_prefix} 'feed' key not found or not a list.")
            await self._set_failed_cache(cache_key)
            return []

        news_articles = self._parse_news(response["feed"])

        await self._set_to_cache(cache_key, news_articles, ttl=900)  # 15 min TTL

        return news_articles

    def _parse_news(self, feed: List[dict]) -> List[sm.NewsItem]:
        """Parses the 'feed' from Alpha Vantage into a list of NewsItem models."""
        parsed_articles = []
        for item in feed:
            try:
                # The 'authors' field is a list, we'll join it.
                publisher = ", ".join(item.get("authors", []))

                # Convert ticker_sentiment to our model if needed, for now just extracting summary
                summary = item.get("summary")

                article = sm.NewsItem(
                    id=None,  # Alpha Vantage doesn't provide a stable ID
                    title=item.get("title"),
                    publisher=publisher,
                    link=item.get("url"),
                    published_utc=item.get(
                        "time_published"
                    ),  # Assuming this is in a format Pydantic can handle
                    tickers=[ts["ticker"] for ts in item.get("ticker_sentiment", [])],
                    summary=summary,
                    image_url=item.get("banner_image"),
                )
                parsed_articles.append(article)
            except Exception as e:
                self.logger.warning(f"Failed to parse news item: {item}. Error: {e}")
        return parsed_articles

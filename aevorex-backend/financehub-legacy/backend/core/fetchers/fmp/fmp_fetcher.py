from typing import List, Optional
import httpx
import structlog
from backend.core.fetchers.common.base_fetcher import BaseFetcher
from backend.models import stock as sm

FMP_FETCHER_LOGGER = structlog.get_logger(__name__)


class FMPFetcher(BaseFetcher):
    """
    Fetcher for Financial Modeling Prep API.
    """

    def __init__(self, http_client: httpx.AsyncClient, cache_service, api_key: str):
        super().__init__(http_client, cache_service, api_key)
        self.logger = FMP_FETCHER_LOGGER
        self.base_url = "https://financialmodelingprep.com/api/v3"

    async def fetch_ohlcv(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
    ) -> List[sm.CompanyPriceHistoryEntry]:
        raise NotImplementedError("FMP OHLCV fetching is not yet implemented.")

    async def fetch_quote(self, symbol: str) -> Optional[sm.LatestOHLCV]:
        raise NotImplementedError("FMP quote fetching is not yet implemented.")

    async def fetch_fundamentals(self, symbol: str) -> Optional[sm.CompanyOverview]:
        raise NotImplementedError("FMP fundamentals fetching is not yet implemented.")

    async def fetch_news(
        self,
        symbol: str,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> List[sm.NewsItem]:
        log_prefix = f"[FMP-News:{symbol}]"
        self.logger.info(f"{log_prefix} Fetch request received.")

        cache_key = self._generate_cache_key(f"news_{symbol}_{limit}")

        cached_data = await self._get_from_cache(cache_key)
        if cached_data:
            self.logger.info(f"{log_prefix} Cache HIT.")
            return cached_data

        self.logger.info(f"{log_prefix} Cache MISS. Fetching live data.")

        api_params = {"tickers": symbol.upper(), "limit": limit, "apikey": self.api_key}
        url = f"{self.base_url}/stock_news"

        response = await self._make_api_request(
            method="GET",
            url=url,
            params=api_params,
        )

        if not isinstance(response, list):
            self.logger.warning(f"{log_prefix} FMP API did not return a list.")
            await self._set_failed_cache(cache_key)
            return []

        news_articles = self._parse_news(response)

        await self._set_to_cache(cache_key, news_articles, ttl=900)

        return news_articles

    def _parse_news(self, feed: List[dict]) -> List[sm.NewsItem]:
        parsed_articles = []
        for item in feed:
            try:
                article = sm.NewsItem(
                    id=None,  # FMP doesn't provide a stable ID
                    title=item.get("title"),
                    publisher=item.get("site"),
                    link=item.get("url"),
                    published_utc=item.get("publishedDate"),
                    tickers=[item.get("symbol")],
                    summary=item.get("text"),
                    image_url=item.get("image"),
                )
                parsed_articles.append(article)
            except Exception as e:
                self.logger.warning(f"Failed to parse news item: {item}. Error: {e}")
        return parsed_articles

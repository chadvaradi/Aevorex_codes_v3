"""
Stock Data Fetcher

Extracted from stock_data_service.py (3662 LOC) to follow 160 LOC rule.
Handles all external data fetching operations for stock data.

Responsibilities:
- Company information fetching
- OHLCV data fetching
- News data fetching
- Technical indicators fetching
- Cache management for fetched data
"""

import asyncio
import uuid
from typing import Any
import pandas as pd

from backend.utils.cache_service import CacheService
from backend.core.fetchers.yfinance.yfinance_fetcher import YFinanceFetcher
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.StockDataFetcher")


class StockDataFetcher:
    """Service for fetching stock data from external sources."""

    def __init__(self, cache: CacheService):
        self.timeout_seconds = 30
        # Instantiate YFinanceFetcher directly (factory requires async/http_client)
        self.yfinance_fetcher = YFinanceFetcher(cache)

    async def fetch_company_info(
        self, symbol: str, request_id: str
    ) -> dict[str, Any] | None:
        """Fetch company information from yfinance."""
        try:
            result = await self.yfinance_fetcher.fetch_fundamentals(ticker=symbol)
            if result:
                logger.debug(f"[{request_id}] Company info fetched for {symbol}")
            return result
        except Exception as e:
            logger.error(
                f"[{request_id}] Error fetching company info for {symbol}: {e}"
            )
            return None

    async def fetch_ohlcv_data(
        self,
        symbol: str,
        period: str = "1y",
        interval: str = "1d",
        request_id: str = None,
    ) -> pd.DataFrame | None:
        """Fetch OHLCV data from available sources."""
        if not request_id:
            request_id = f"ohlcv-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            result = await self.yfinance_fetcher.fetch_ohlcv(
                ticker=symbol, period=period, interval=interval
            )

            if result is not None and not result.empty:
                logger.debug(f"[{request_id}] OHLCV data fetched for {symbol}")
                return result
            else:
                logger.warning(f"[{request_id}] No OHLCV data found for {symbol}")
                return None

        except Exception as e:
            logger.error(f"[{request_id}] Error fetching OHLCV for {symbol}: {e}")
            return None

    async def fetch_news_data(
        self, symbol: str, limit: int = 10, request_id: str = None
    ) -> list[Any]:
        """Fetch news data for the symbol."""
        if not request_id:
            request_id = f"news-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            news_items = await self.yfinance_fetcher.fetch_news(ticker=symbol)

            logger.debug(
                f"[{request_id}] Fetched {len(news_items)} news items for {symbol}"
            )
            return news_items[:limit]

        except Exception as e:
            logger.error(f"[{request_id}] Error fetching news for {symbol}: {e}")
            return []

    async def fetch_parallel_data(
        self,
        symbol: str,
        include_chart: bool = True,
        include_news: bool = True,
        request_id: str = None,
    ) -> dict[str, Any]:
        """Fetch multiple data sources in parallel for efficiency."""
        if not request_id:
            request_id = f"parallel-{symbol}-{uuid.uuid4().hex[:6]}"

        tasks = {"company_info": self.fetch_company_info(symbol, request_id)}

        if include_chart:
            tasks["ohlcv"] = self.fetch_ohlcv_data(symbol, request_id=request_id)

        if include_news:
            tasks["news"] = self.fetch_news_data(symbol, request_id=request_id)

        try:
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)

            # Process results
            processed_results = {}
            for i, (key, _) in enumerate(tasks.items()):
                result = results[i]
                if isinstance(result, Exception):
                    logger.error(
                        f"Task {key} failed for {symbol} with error: {result}",
                        exc_info=True,
                    )
                    processed_results[key] = None
                else:
                    processed_results[key] = result

            return processed_results

        except Exception as e:
            logger.error(f"[{request_id}] Error in parallel fetch for {symbol}: {e}")
            return {}

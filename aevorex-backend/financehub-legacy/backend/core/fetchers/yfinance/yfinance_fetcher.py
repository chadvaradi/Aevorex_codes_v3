# modules/financehub/backend/core/fetchers/yfinance/yfinance_fetcher.py
from __future__ import annotations
import pandas as pd
from typing import Any, Dict, List, Optional

import yfinance as yf
from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.core.fetchers.common.base_fetcher import BaseFetcher
from backend.core.fetchers.common._base_helpers import generate_cache_key

# Logger setup
logger = get_logger("aevorex_finbot.core.fetchers.yfinance")

# Cache TTL constants
YFINANCE_INFO_TTL = 3600  # 1 hour
YFINANCE_OHLCV_TTL = 900  # 15 minutes
YFINANCE_NEWS_TTL = 1800  # 30 minutes


class YFinanceFetcher(BaseFetcher):
    """
    Data fetcher for yfinance.
    """

    def __init__(self, cache: CacheService):
        self.cache = cache

    async def fetch_ohlcv(
        self, ticker: str, period: str, interval: str, force_refresh: bool = False
    ) -> Optional[pd.DataFrame]:
        log_prefix = f"[{ticker.upper()}][yfinance_ohlcv]"
        cache_key_params = {"period": period, "interval": interval}
        cache_key = generate_cache_key(
            "ohlcv", "yfinance", ticker.upper(), params=cache_key_params
        )

        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data is not None and isinstance(cached_data, pd.DataFrame):
                logger.info(f"{log_prefix} Cache HIT.")
                return cached_data

        logger.info(f"{log_prefix} Cache MISS. Fetching live data.")
        try:
            yf_ticker = yf.Ticker(ticker)
            history = yf_ticker.history(period=period, interval=interval)
            if not history.empty:
                await self.cache.set(cache_key, history, ttl=YFINANCE_OHLCV_TTL)
                logger.info(
                    f"{log_prefix} Successfully fetched {len(history)} rows and cached."
                )
                return history
            else:
                logger.warning(f"{log_prefix} No data returned from yfinance.")
                return None
        except Exception as e:
            logger.error(f"{log_prefix} An error occurred: {e}", exc_info=True)
            return None

    async def fetch_quote(
        self, ticker: str, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        return await self._fetch_info(ticker, force_refresh)

    async def fetch_fundamentals(
        self, ticker: str, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        return await self._fetch_info(ticker, force_refresh)

    async def fetch_news(
        self, ticker: str, force_refresh: bool = False
    ) -> Optional[List[Dict[str, Any]]]:
        log_prefix = f"[{ticker.upper()}][yfinance_news]"
        cache_key = generate_cache_key("news", "yfinance", ticker.upper())

        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"{log_prefix} Cache HIT.")
                return cached_data

        logger.info(f"{log_prefix} Cache MISS. Fetching live data.")
        try:
            yf_ticker = yf.Ticker(ticker)
            news = yf_ticker.news
            if news:
                await self.cache.set(cache_key, news, ttl=YFINANCE_NEWS_TTL)
                logger.info(
                    f"{log_prefix} Successfully fetched {len(news)} news articles and cached."
                )
                return news
            else:
                logger.warning(f"{log_prefix} No news returned from yfinance.")
                return None
        except Exception as e:
            logger.error(f"{log_prefix} An error occurred: {e}", exc_info=True)
            return None

    async def _fetch_info(
        self, ticker: str, force_refresh: bool = False
    ) -> Optional[Dict[str, Any]]:
        log_prefix = f"[{ticker.upper()}][yfinance_info]"
        cache_key = generate_cache_key("info", "yfinance", ticker.upper())

        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info(f"{log_prefix} Cache HIT.")
                return cached_data

        logger.info(f"{log_prefix} Cache MISS. Fetching live data.")
        try:
            yf_ticker = yf.Ticker(ticker)
            info = yf_ticker.info
            if info:
                await self.cache.set(cache_key, info, ttl=YFINANCE_INFO_TTL)
                logger.info(f"{log_prefix} Successfully fetched and cached data.")
                return info
            else:
                logger.warning(f"{log_prefix} No data returned from yfinance.")
                return None
        except Exception as e:
            logger.error(f"{log_prefix} An error occurred: {e}", exc_info=True)
            return None

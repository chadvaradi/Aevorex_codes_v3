from __future__ import annotations
import httpx
import pandas as pd
from typing import Any, List, Optional
import structlog

from backend.utils.cache_service import CacheService
from backend.core.fetchers.common.base_fetcher import BaseFetcher
from backend.core.fetchers.common._base_helpers import (
    FETCH_FAILED_MARKER,
    generate_cache_key,
    get_api_key,
    make_api_request,
)
from backend.core.fetchers.common._fetcher_constants import (
    EODHD_BASE_URL_EOD,
    EODHD_BASE_URL_INTRADAY,
    EODHD_DAILY_TTL,
    EODHD_INTRADAY_TTL,
    FETCH_FAILURE_CACHE_TTL,
    EODHD_BASE_URL_FUNDAMENTALS,
    EODHD_FUNDAMENTALS_TTL,
    EODHD_BASE_URL_NEWS,
)
from backend.config import settings
from backend.models import stock as sm

EODHD_FETCHER_LOGGER = structlog.get_logger(__name__)
HTTP_TIMEOUT = getattr(settings.HTTP_CLIENT, "REQUEST_TIMEOUT_SECONDS", 15.0)
TARGET_OHLCV_COLS = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
TARGET_OHLCV_COLS_INTRADAY = ["Open", "High", "Low", "Close", "Volume"]


class EODHDFetcher(BaseFetcher):
    """
    Data fetcher for EOD Historical Data.
    """

    def __init__(self, cache: CacheService, client: httpx.AsyncClient):
        self.cache = cache
        self.client = client

    async def fetch_ohlcv(
        self,
        ticker: str,
        interval: str = "d",
        period_or_start_date: str = "1y",
        **kwargs,
    ) -> pd.DataFrame | None:
        log_prefix = f"[{ticker}][eodhd_ohlcv({interval},{period_or_start_date})]"
        EODHD_FETCHER_LOGGER.debug(f"{log_prefix} === Starting OHLCV Fetch ===")

        try:
            api_key = await get_api_key("EODHD")
            if not api_key:
                EODHD_FETCHER_LOGGER.error(f"{log_prefix} API key for EODHD not found.")
                return None

            is_daily = interval.lower() in ["d", "w", "m"]
            base_url = EODHD_BASE_URL_EOD if is_daily else EODHD_BASE_URL_INTRADAY
            api_params = {"api_token": api_key, "fmt": "json"}
            cache_key_params = {"interval": interval, "range": period_or_start_date}
            cache_ttl = EODHD_DAILY_TTL if is_daily else EODHD_INTRADAY_TTL

            if is_daily:
                api_params["period"] = interval
                if period_or_start_date not in ["1y", "5y", "max"]:
                    api_params["from"] = period_or_start_date
            else:
                api_params["interval"] = interval

            cache_key = generate_cache_key(
                data_type="ohlcv",
                source="eodhd",
                identifier=ticker,
                params=cache_key_params,
            )
            EODHD_FETCHER_LOGGER.info(f"{log_prefix} Generated cache key: {cache_key}")

            EODHD_FETCHER_LOGGER.debug(f"{log_prefix} Cache MISS. Fetching from API...")
            response_data = await make_api_request(
                client=self.client,
                method="GET",
                url=f"{base_url}/{ticker}",
                params=api_params,
                source_name_for_log="EODHD",
                http_timeout=HTTP_TIMEOUT,
            )

            if response_data is None:
                await self.cache.set(
                    cache_key, FETCH_FAILED_MARKER, ttl=FETCH_FAILURE_CACHE_TTL
                )
                return None

            df = pd.DataFrame(response_data)
            if df.empty:
                EODHD_FETCHER_LOGGER.warning(f"{log_prefix} API returned empty data.")
                await self.cache.set(
                    cache_key, FETCH_FAILED_MARKER, ttl=FETCH_FAILURE_CACHE_TTL
                )
                return None

            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

            final_cols = TARGET_OHLCV_COLS if is_daily else TARGET_OHLCV_COLS_INTRADAY
            df = df[final_cols]

            EODHD_FETCHER_LOGGER.info(
                f"{log_prefix} Fetch successful. Shape: {df.shape}"
            )
            return df

        except Exception as e:
            EODHD_FETCHER_LOGGER.critical(
                f"{log_prefix} Critical failure in OHLCV fetch: {e}", exc_info=True
            )
            return None

    async def fetch_quote(
        self, ticker: str, force_refresh: bool = False, **kwargs
    ) -> dict[str, Any] | None:
        log_prefix = f"[EODHD-Quote:{ticker}]"

        cache_key = generate_cache_key(
            data_type="quote", source="eodhd", identifier=ticker
        )

        EODHD_FETCHER_LOGGER.info(f"{log_prefix} Fetch request.")

        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                EODHD_FETCHER_LOGGER.info(f"{log_prefix} Cache HIT.")
                if cached_data == FETCH_FAILED_MARKER:
                    return None
                return cached_data

        api_key = await get_api_key("EODHD")
        if not api_key:
            EODHD_FETCHER_LOGGER.error(f"{log_prefix} API key for EODHD not found.")
            return None

        request_url = f"https://eodhistoricaldata.com/api/real-time/{ticker}"

        request_params = {
            "api_token": api_key,
            "fmt": "json",
        }

        response_json = await make_api_request(
            client=self.client,
            method="GET",
            url=request_url,
            params=request_params,
            source_name_for_log="EODHD",
            http_timeout=HTTP_TIMEOUT,
        )

        if not response_json or not isinstance(response_json, dict):
            EODHD_FETCHER_LOGGER.warning(
                f"{log_prefix} API call failed or returned invalid data. Caching failure."
            )
            await self.cache.set(cache_key, FETCH_FAILED_MARKER, ttl=600)
            return None

        await self.cache.set(cache_key, response_json, ttl=EODHD_INTRADAY_TTL)
        EODHD_FETCHER_LOGGER.info(f"{log_prefix} Successfully fetched quote data.")
        return response_json

    async def fetch_fundamentals(
        self, ticker: str, force_refresh: bool = False, **kwargs
    ) -> dict | None:
        log_prefix = f"[EODHD-Fundamentals:{ticker}]"
        EODHD_FETCHER_LOGGER.info(f"{log_prefix} Fetch request received.")

        cache_key = generate_cache_key(
            data_type="fundamentals", source="eodhd", identifier=ticker
        )

        if not force_refresh:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                EODHD_FETCHER_LOGGER.info(f"{log_prefix} Cache HIT.")
                if cached_data == FETCH_FAILED_MARKER:
                    EODHD_FETCHER_LOGGER.warning(
                        f"{log_prefix} Cached failure detected. Returning None."
                    )
                    return None
                return cached_data

        api_key = await get_api_key("EODHD")
        if not api_key:
            EODHD_FETCHER_LOGGER.error(f"{log_prefix} API key for EODHD not found.")
            return None

        params = {"api_token": api_key}
        request_url = f"{EODHD_BASE_URL_FUNDAMENTALS}/{ticker}"

        response_json = await make_api_request(
            client=self.client,
            method="GET",
            url=request_url,
            params=params,
            source_name_for_log="EODHD",
            http_timeout=HTTP_TIMEOUT,
        )

        if not response_json or not isinstance(response_json, dict):
            EODHD_FETCHER_LOGGER.warning(
                f"{log_prefix} API call failed or returned invalid data. Caching failure."
            )
            await self.cache.set(cache_key, FETCH_FAILED_MARKER, ttl=600)
            return None

        EODHD_FETCHER_LOGGER.info(
            f"{log_prefix} Successfully fetched fundamentals data."
        )
        await self.cache.set(cache_key, response_json, ttl=EODHD_FUNDAMENTALS_TTL)
        return response_json

    async def fetch_company_info(
        self, ticker: str, force_refresh: bool = False, **kwargs
    ) -> dict | None:
        EODHD_FETCHER_LOGGER.info(
            f"[EODHD-CompanyInfo:{ticker}] Fetching company info (via fundamentals)."
        )
        fundamentals = await self.fetch_fundamentals(ticker, force_refresh)
        if fundamentals and "General" in fundamentals:
            return fundamentals["General"]
        return None

    async def fetch_financial_statements(
        self,
        ticker: str,
        statement_type: str,
        frequency: str = "Annual",
        force_refresh: bool = False,
        **kwargs,
    ) -> pd.DataFrame | None:
        EODHD_FETCHER_LOGGER.info(
            f"[EODHD-Financials:{ticker}] Fetching {frequency} {statement_type} (via fundamentals)."
        )

        fundamentals = await self.fetch_fundamentals(ticker, force_refresh)

        if (
            fundamentals
            and "Financials" in fundamentals
            and statement_type in fundamentals["Financials"]
            and frequency in fundamentals["Financials"][statement_type]
        ):
            statement_data = fundamentals["Financials"][statement_type][frequency]
            df = pd.DataFrame.from_dict(statement_data, orient="index")
            df.index.name = "date"
            df.reset_index(inplace=True)
            return df

        EODHD_FETCHER_LOGGER.warning(
            f"[EODHD-Financials:{ticker}] Could not find {frequency} {statement_type} in fundamentals data."
        )
        return None

    async def fetch_news(
        self,
        symbol: str,
        from_date_str: Optional[str] = None,
        to_date_str: Optional[str] = None,
        limit: Optional[int] = 50,
    ) -> List[sm.NewsItem]:
        """
        Fetches news from EODHD for a given symbol.
        """
        log_prefix = f"[EODHD-News:{symbol}]"
        EODHD_FETCHER_LOGGER.info(f"{log_prefix} Fetch request received.")

        cache_key = generate_cache_key(
            data_type="news",
            source="eodhd",
            identifier=symbol,
            params={"from": from_date_str, "to": to_date_str, "limit": limit},
        )

        cached_data = await self.cache.get(cache_key)
        if cached_data:
            EODHD_FETCHER_LOGGER.info(f"{log_prefix} Cache HIT.")
            # Assuming cached_data is a list of NewsItem models
            return cached_data

        api_key = await get_api_key("EODHD")
        if not api_key:
            EODHD_FETCHER_LOGGER.error(f"{log_prefix} API key for EODHD not found.")
            return []

        params = {"api_token": api_key, "s": symbol, "limit": limit, "fmt": "json"}
        if from_date_str:
            params["from"] = from_date_str
        if to_date_str:
            params["to"] = to_date_str

        response_json = await make_api_request(
            client=self.client,
            method="GET",
            url=EODHD_BASE_URL_NEWS,
            params=params,
            source_name_for_log="EODHD",
            http_timeout=HTTP_TIMEOUT,
        )

        if not response_json or not isinstance(response_json, list):
            EODHD_FETCHER_LOGGER.warning(
                f"{log_prefix} API call failed or returned invalid data."
            )
            return []

        # Using the mapper from the yfinance_fetcher as it is generic
        news_items = [sm.NewsItem(**article) for article in response_json]
        await self.cache.set(
            cache_key, [item.model_dump() for item in news_items], ttl=3600
        )

        return news_items

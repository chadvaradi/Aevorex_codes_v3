# backend/api/endpoints/market_data.py
"""
API Endpoint for Market Data related operations. (v2.1 Enterprise Refactor)

Provides access to pre-aggregated or cached market data points.
Currently includes fetching pre-cached news data.
"""

import os
import json
import httpx
from typing import Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

# --- Helyi Importok ---
from backend.utils.logger_config import get_logger
from backend.api.deps import get_cache_service
from backend.utils.cache_service import CacheService

# --- Logger Inicializálása ---
MODULE_NAME = "Market Data Endpoint"
logger = get_logger(__name__)  # Modul szintű logger

# Configuration and settings
try:
    logger.info("Settings imported successfully from config module")
except ImportError as e:
    logger.critical(f"Failed to import settings: {e}")
    raise ImportError("Cannot import configuration settings") from e

# --- Router Inicializálása ---
router = APIRouter(
    # Prefix és Tag-ek a Swagger UI és az útvonalak szervezéséhez
    # prefix="/api/v1/market-data",  # Removed because it's added in main.py
    tags=["Market Data"]
)

# --- Konstansok ---
LOG_PREFIX_ENDPOINT = f"[{MODULE_NAME}]"

# --- API Endpoint-ok ---


@router.get(
    "/news",
    summary="Get latest market-wide news",
    description="Retrieves latest market news articles",
    response_description="A list of news articles with metadata",
    response_model=list[dict[str, Any]],
    status_code=status.HTTP_200_OK,
)
async def get_market_news(
    cache: Annotated[CacheService, Depends(get_cache_service)],
    limit: Annotated[int, Query(description="Number of news items to return")] = 10,
) -> list[dict[str, Any]]:
    """
    Fetches the latest general market news from MarketAux.
    """
    logger.info(f"{LOG_PREFIX_ENDPOINT} /news request received.")

    try:
        cache_key = "market_news_data"
        cached_data_raw: Any | None = await cache.get(cache_key)

        if cached_data_raw is None:
            logger.info(
                f"{LOG_PREFIX_ENDPOINT} Cache MISS for key: '{cache_key}'. Fetching from NewsAPI.org"
            )

            api_key = os.getenv("FINBOT_API_KEYS__NEWSAPI") or os.getenv(
                "NEWSAPI_API_KEY"
            )

            async with httpx.AsyncClient(timeout=10.0) as client:
                if api_key:
                    url = (
                        "https://newsapi.org/v2/top-headlines?"
                        "category=business&language=en&pageSize={limit}&apiKey={api_key}"
                    ).format(limit=limit, api_key=api_key)
                    resp = await client.get(url)
                    try:
                        resp.raise_for_status()
                    except httpx.HTTPStatusError as http_err:
                        raise HTTPException(
                            status_code=502, detail=f"NewsAPI error: {http_err}"
                        ) from http_err

                    payload = resp.json()
                    if payload.get("status") != "ok":
                        raise HTTPException(
                            status_code=502,
                            detail="Unexpected response from NewsAPI.org",
                        )

                    articles = payload.get("articles", [])
                    source_name = "NewsAPI.org"
                else:
                    # Key-less fallback – CryptoCompare public news endpoint (business & finance)
                    url = f"https://min-api.cryptocompare.com/data/v2/news/?lang=EN&sortOrder=latest&limit={limit}"
                    resp = await client.get(url)
                    resp.raise_for_status()
                    payload = resp.json()
                    if payload.get("Type") != 100:  # Success code for CryptoCompare
                        raise HTTPException(
                            status_code=502,
                            detail="Unexpected response from CryptoCompare news API",
                        )
                    articles = payload.get("Data", [])
                    source_name = "CryptoCompare News"
                # Normalize to common structure
                news_data = []
                for art in articles:
                    news_data.append(
                        {
                            "headline": art.get("title")
                            or art.get("title")
                            or art.get("Headline"),
                            "summary": art.get("description") or art.get("Body"),
                            "url": art.get("url") or art.get("Url"),
                            "source": art.get("source", {}).get("name")
                            if isinstance(art.get("source"), dict)
                            else art.get("source") or source_name,
                            "timestamp": art.get("publishedAt")
                            or art.get("published_on"),
                            "image": art.get("urlToImage") or art.get("ImageUrl"),
                        }
                    )

            # Cache for 5 minutes (300s)
            try:
                await cache.set(cache_key, json.dumps(news_data), timeout_seconds=300)
                logger.debug(f"{LOG_PREFIX_ENDPOINT} News data cached with TTL: 300s")
            except Exception as cache_err:
                logger.warning(
                    f"{LOG_PREFIX_ENDPOINT} Failed to cache news data: {cache_err}"
                )

            logger.info(
                f"{LOG_PREFIX_ENDPOINT} Successfully fetched {len(news_data)} news items from NewsAPI"
            )
            return news_data

        # Process cached data
        logger.debug(f"{LOG_PREFIX_ENDPOINT} Cache HIT for key: '{cache_key}'")

        processed_data: list[dict[str, Any]]
        if isinstance(cached_data_raw, str):
            try:
                # Attempt to decode the raw string data
                cached_data = json.loads(cached_data_raw)
            except json.JSONDecodeError as json_err:
                logger.error(f"{LOG_PREFIX_ENDPOINT} Failed to decode JSON: {json_err}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal error: Cached news data is corrupted.",
                ) from json_err
            if isinstance(cached_data, list):
                processed_data = cached_data
            else:
                logger.error(
                    f"{LOG_PREFIX_ENDPOINT} Processed data is not a list: {type(processed_data)}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Internal error: Failed to process cached data correctly.",
                )
        elif isinstance(cached_data_raw, list):
            processed_data = cached_data_raw
        else:
            logger.error(
                f"{LOG_PREFIX_ENDPOINT} Unexpected data type in cache: {type(cached_data_raw)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error: Unexpected data type in news cache.",
            )

        if not isinstance(processed_data, list):
            logger.error(
                f"{LOG_PREFIX_ENDPOINT} Processed data is not a list: {type(processed_data)}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error: Failed to process cached data correctly.",
            )

        # Apply limit
        if limit:
            processed_data = processed_data[:limit]

        item_count = len(processed_data)
        logger.info(
            f"{LOG_PREFIX_ENDPOINT} Successfully retrieved {item_count} news items from cache."
        )
        return processed_data

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        logger.exception(f"{LOG_PREFIX_ENDPOINT} Unexpected error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An internal server error occurred while fetching market news.",
        ) from e


# --- Modul betöltés jelzése (hasznos debuggoláshoz) ---
logger.info(
    f"--- {MODULE_NAME} loaded and router configured with prefix '/api/v1/market'. Endpoint '/news' is available. ---"
)
logger.info("✅ Market data router loaded successfully.")

# ---------------------------------------------------------------------------
# NEW ENDPOINT: /indices – Major market indices snapshot
# ---------------------------------------------------------------------------

# NOTE: This uses the lightweight yfinance library that is already a dependency
# elsewhere in FinanceHub. For three symbols the blocking cost is negligible,
# but we still run it in a thread-pool so the event-loop remains responsive.

import asyncio
from concurrent.futures import ThreadPoolExecutor

try:
    import yfinance as yf  # Lazy import – only needed for this endpoint
except ImportError as imp_err:  # pragma: no cover – should be installed via poetry
    logger.warning(
        "yfinance not installed – /indices endpoint will be unavailable: %s", imp_err
    )
    yf = None  # type: ignore


@router.get(
    "/indices",
    summary="Get a snapshot of major market indices (price + daily change)",
    description="Returns latest price and daily change for S&P 500, Dow Jones and Nasdaq Composite.",
    response_description="List of index data dictionaries",
    status_code=status.HTTP_200_OK,
)
async def get_market_indices(
    limit: Annotated[
        int | None, Query(description="Max number of indices to return", ge=1, le=10)
    ] = None,
):
    if yf is None:
        raise HTTPException(
            status_code=503, detail="yfinance dependency unavailable on server"
        )

    symbols = ["^GSPC", "^DJI", "^IXIC"]
    if limit:
        symbols = symbols[:limit]

    def _fetch() -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for sym in symbols:
            ticker = yf.Ticker(sym)
            price = ticker.info.get("regularMarketPrice")
            prev = ticker.info.get("regularMarketPreviousClose")
            if price is None or prev is None:
                continue  # Skip incomplete data
            change = price - prev
            change_pct = (change / prev) * 100 if prev else 0
            result.append(
                {
                    "symbol": sym,
                    "price": price,
                    "change": round(change, 2),
                    "change_percent": round(change_pct, 2),
                }
            )
        return result

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as pool:
        indices_data = await loop.run_in_executor(pool, _fetch)

    if not indices_data:
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch index data from provider (yfinance)",
        )

    return {
        "status": "ok",
        "count": len(indices_data),
        "indices": indices_data,
    }

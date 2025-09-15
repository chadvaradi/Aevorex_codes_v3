"""
Ticker Tape Data Endpoint

Provides real-time ticker tape data for multiple symbols.
This endpoint aggregates basic stock data from multiple sources
to create a dynamic ticker tape feed.
"""

from datetime import datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from backend.utils.cache_service import CacheService
from backend.core.ticker_tape_service import (
    update_ticker_tape_data_in_cache,
    get_selected_provider,
    get_ticker_tape_data_from_cache,
)
from backend.api.deps import get_cache_service, get_http_client, get_orchestrator
from backend.config import settings
from backend.core.services.stock.orchestrator import StockOrchestrator
from backend.models.ticker_tape_response import TickerTapeItem
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Router setup
# ---------------------------------------------------------------------------
router = APIRouter(
    prefix="/ticker-tape",
    tags=["Ticker Tape"],
    redirect_slashes=False,  # Prevent 307 redirect between `/ticker-tape` and `/ticker-tape/`
)


# ---------------------------------------------------------------------------
# Internal helper: register a no-slash alias
# ---------------------------------------------------------------------------
def _register_no_slash_variant(router_ref: APIRouter):
    """Clone `/ticker-tape/` GET handler to `/ticker-tape` (no slash)."""
    for route in router_ref.routes:
        if getattr(route, "path", "") == "/":  # The existing `/` handler
            router_ref.add_api_route(
                path="",
                endpoint=route.endpoint,  # type: ignore[arg-type]
                methods=["GET"],
                include_in_schema=False,
                name=route.name or "get_ticker_tape_data_no_slash",
            )
            break


# ---------------------------------------------------------------------------
# Main endpoint: ticker tape root
# ---------------------------------------------------------------------------
@router.get("/", summary="Get ticker-tape data")
async def get_ticker_tape_root(
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
    limit: Annotated[int, Query(description="Number of symbols to return")] = 20,
    force_refresh: Annotated[
        bool, Query(description="Force refresh of cached data")
    ] = False,
) -> JSONResponse:
    """
    ✅ REAL TICKER TAPE DATA - Uses dedicated ticker_tape_service.py
    Returns real-time ticker data from EODHD API with cache support
    """
    try:
        logger.info(
            f"TickerTape API request (limit={limit}, force_refresh={force_refresh})"
        )

        # Provider selection
        selected_provider = get_selected_provider()

        # Cache configuration
        cache_key = settings.TICKER_TAPE.CACHE_KEY
        cache_ttl = settings.TICKER_TAPE.CACHE_TTL_SECONDS
        logger.debug(f"📦 Using cache key: {cache_key}, TTL: {cache_ttl}s")

        # Try cache first
        if not force_refresh:
            try:
                cached_data = await get_ticker_tape_data_from_cache(cache)
                if cached_data and isinstance(cached_data, list):
                    limited_data = (
                        cached_data[:limit] if limit < len(cached_data) else cached_data
                    )
                    return JSONResponse(
                        status_code=status.HTTP_200_OK,
                        content={
                            "status": "success",
                            "data": limited_data,
                            "metadata": {
                                "total_symbols": len(limited_data),
                                "requested_limit": limit,
                                "data_source": "cache",
                                "last_updated": datetime.utcnow().isoformat(),
                                "cache_hit": True,
                            },
                        },
                    )
            except Exception as cache_error:
                logger.warning(f"Cache read error: {cache_error}")

        # Otherwise fetch fresh
        logger.info("🔄 Fetching fresh ticker tape data...")
        try:
            await update_ticker_tape_data_in_cache(http_client, cache)
        except HTTPException as http_exc:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "error",
                    "message": http_exc.detail,
                    "provider": selected_provider,
                    "data": [],
                },
            )

        # Read fresh cache
        try:
            fresh_data = await get_ticker_tape_data_from_cache(cache)
            if fresh_data and isinstance(fresh_data, list):
                limited_data = (
                    fresh_data[:limit] if limit < len(fresh_data) else fresh_data
                )
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "status": "success",
                        "data": limited_data,
                        "metadata": {
                            "total_symbols": len(limited_data),
                            "requested_limit": limit,
                            "data_source": "real_api",
                            "last_updated": datetime.utcnow().isoformat(),
                            "cache_hit": False,
                        },
                    },
                )
            else:
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content={
                        "status": "error",
                        "message": "Live ticker tape data unavailable",
                        "provider": selected_provider,
                        "data": [],
                    },
                )
        except Exception as fresh_cache_error:
            logger.error(f"Error reading fresh cache data: {fresh_cache_error}")
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "error",
                    "message": "Cache retrieval failed after data fetch.",
                    "provider": selected_provider,
                    "data": [],
                },
            )

    except HTTPException as http_exc:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "error",
                "message": str(http_exc.detail)
                if hasattr(http_exc, "detail")
                else "Ticker tape error",
                "data": [],
            },
        )
    except Exception as e:
        logger.error(f"🚨 Ticker tape endpoint error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch ticker tape data: {str(e)}",
        ) from e


# Register alias
_register_no_slash_variant(router)


# ---------------------------------------------------------------------------
# Secondary endpoint: single ticker tape item
# ---------------------------------------------------------------------------
@router.get(
    "/item",
    summary="Get Ticker Tape Item Data",
    description="Returns ticker tape item data for a specific stock",
    responses={
        200: {"description": "Ticker tape item data retrieved successfully"},
        404: {"description": "Ticker tape item not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_ticker_tape_item(
    ticker: Annotated[
        str | None, Query(alias="symbol", description="Ticker symbol (alias: symbol)")
    ] = None,
    http_client: httpx.AsyncClient = Depends(get_http_client),
    cache: CacheService = Depends(get_cache_service),
    orchestrator: StockOrchestrator = Depends(get_orchestrator),
):
    try:
        if not ticker:
            ticker = "AAPL"  # Default
            logger.info(
                "Ticker tape /item called without symbol – defaulting to 'AAPL'"
            )

        data = await orchestrator.get_basic_stock_data(
            symbol=ticker, client=http_client
        )

        if not data:
            logger.warning(
                "TickerTape /item orchestrator empty – using yfinance fallback for %s",
                ticker,
            )
            try:
                import yfinance as _yf

                yf_ticker = _yf.Ticker(ticker)
                info = yf_ticker.fast_info if hasattr(yf_ticker, "fast_info") else {}
                price = float(info.get("last_price") or 0)
                change = (
                    float(info.get("last_price") - info.get("previous_close", 0))
                    if info
                    else 0
                )
                pct = (
                    round((change / info.get("previous_close", 1)) * 100, 2)
                    if info
                    else 0
                )
                data = {
                    "symbol": ticker,
                    "price": price,
                    "change": change,
                    "change_percent": pct,
                    "volume": info.get("volume", 0),
                    "currency": info.get("currency", "USD"),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            except Exception as yf_err:
                logger.error("yfinance fallback failed: %s", yf_err)
                data = {
                    "symbol": ticker,
                    "price": None,
                    "change": None,
                    "change_percent": None,
                    "volume": None,
                    "currency": "USD",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        # Validation hardening
        def _safe_numeric(value):
            try:
                return float(value)
            except (TypeError, ValueError):
                return 0.0

        for k, default in {
            "price": 0.0,
            "change": 0.0,
            "change_percent": 0.0,
            "volume": 0,
            "currency": "USD",
            "market_cap": None,
            "exchange": None,
        }.items():
            data.setdefault(k, default)

        for k in ("price", "change", "change_percent"):
            data[k] = _safe_numeric(data.get(k))

        try:
            serialised = TickerTapeItem(**data).model_dump()
        except Exception as validation_err:
            logger.error("TickerTapeItem validation failed: %s", validation_err)
            serialised = data

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": serialised,
            },
        )
    except Exception as e:
        logger.error("Ticker tape item fatal error: %s", e)
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Failed to fetch ticker item: {str(e)}",
                "data": {},
            },
        )

"""
Ticker Tape Data Endpoint - EODHD Only
======================================

Simplified ticker tape endpoints using only EODHD API.
No caching, no orchestrator - direct EODHD integration.
"""

from datetime import datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from backend.api.deps import get_http_client
from backend.config.eodhd import settings as eodhd_settings
from backend.core.ticker_tape_service import (
    get_ticker_tape_data,
    get_single_ticker_data
)
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

# Default ticker symbols
DEFAULT_TICKER_SYMBOLS = [
    "AAPL",
    "MSFT", 
    "GOOGL",
    "AMZN",
    "TSLA",
    "META",
    "NVDA",
    "NFLX",
    "AMD",
    "INTC",
    "BTC-USD",
    "ETH-USD"
]

# Router setup
router = APIRouter(
    redirect_slashes=False,
)

# Register no-slash alias
def _register_no_slash_variant(router_ref: APIRouter):
    """Clone `/ticker-tape/` GET handler to `/ticker-tape` (no slash)."""
    for route in router_ref.routes:
        if getattr(route, "path", "") == "/":
            router_ref.add_api_route(
                path="",
                endpoint=route.endpoint,
                methods=["GET"],
                include_in_schema=False,
                name=route.name or "get_ticker_tape_data_no_slash",
            )
            break

@router.get("/", summary="Get ticker-tape data (EODHD-only)")
async def get_ticker_tape_root(
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    limit: Annotated[int, Query(description="Number of symbols to return", ge=1, le=50)] = 20,
) -> JSONResponse:
    """
    Get real-time ticker tape data from EODHD API only.
    
    Returns live market data for multiple symbols without caching.
    Uses EODHD All World Extended API (300,000 requests/day).
    No fallback providers, no cache - direct EODHD integration.
    """
    try:
        logger.info(f"TickerTape API request (limit={limit})")
        
        # Get symbols to fetch (limit the default list)
        symbols = DEFAULT_TICKER_SYMBOLS[:limit]
        
        # Fetch data from EODHD - direct API calls
        ticker_data = []
        for symbol in symbols:
            try:
                # Direct EODHD API call
                url = f"https://eodhd.com/api/real-time/{symbol}"
                params = {
                    "api_token": eodhd_settings.API_KEY,
                    "fmt": "json"
                }
                
                response = await http_client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if data and isinstance(data, dict):
                    ticker_item = {
                        "symbol": symbol,
                        "price": data.get("close"),
                        "change": data.get("change"),
                        "change_percent": data.get("change_percent"),
                        "volume": data.get("volume"),
                        "high": data.get("high"),
                        "low": data.get("low"),
                        "open": data.get("open"),
                        "previous_close": data.get("previous_close"),
                        "timestamp": data.get("timestamp"),
                        "currency": data.get("currency", "USD")
                    }
                    ticker_data.append(ticker_item)
                    
            except Exception as e:
                logger.error(f"Failed to fetch {symbol}: {e}")
        
        if not ticker_data:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "error",
                    "message": "No ticker data available from EODHD",
                    "data": [],
                    "metadata": {
                        "total_symbols": 0,
                        "requested_limit": limit,
                        "provider": "EODHD",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": ticker_data,
                "metadata": {
                    "total_symbols": len(ticker_data),
                    "requested_limit": limit,
                    "provider": "EODHD",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Ticker tape endpoint error: {e}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "error",
                "message": f"Failed to fetch ticker tape data: {str(e)}",
                "data": [],
                "metadata": {
                    "total_symbols": 0,
                    "requested_limit": limit,
                    "provider": "EODHD",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )

# Register alias
_register_no_slash_variant(router)

@router.get(
    "/item",
    summary="Get Ticker Tape Item Data (EODHD-only)",
    description="Returns ticker tape item data for a specific stock from EODHD API only",
    responses={
        200: {"description": "Ticker tape item data retrieved successfully"},
        404: {"description": "Ticker tape item not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_ticker_tape_item(
    ticker: Annotated[
        str, Query(alias="symbol", description="Ticker symbol (e.g., AAPL, MSFT)")
    ] = "AAPL",
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    Get single ticker tape item from EODHD API only.
    
    Returns live market data for a specific symbol without caching.
    Uses EODHD All World Extended API (300,000 requests/day).
    No fallback providers, no cache - direct EODHD integration.
    """
    try:
        logger.info(f"Ticker tape /item called for symbol: {ticker}")
        
        # Fetch data from EODHD - direct API call
        try:
            url = f"https://eodhd.com/api/real-time/{ticker}"
            params = {
                "api_token": eodhd_settings.API_KEY,
                "fmt": "json"
            }
            
            response = await http_client.get(url, params=params)
            response.raise_for_status()
            
            raw_data = response.json()
            
            if raw_data and isinstance(raw_data, dict):
                data = {
                    "symbol": ticker,
                    "price": raw_data.get("close"),
                    "change": raw_data.get("change"),
                    "change_percent": raw_data.get("change_percent"),
                    "volume": raw_data.get("volume"),
                    "high": raw_data.get("high"),
                    "low": raw_data.get("low"),
                    "open": raw_data.get("open"),
                    "previous_close": raw_data.get("previous_close"),
                    "timestamp": raw_data.get("timestamp"),
                    "currency": raw_data.get("currency", "USD")
                }
            else:
                data = None
        except Exception as e:
            logger.error(f"Failed to fetch {ticker}: {e}")
            data = None
        
        if not data:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "error",
                    "message": f"No data available for symbol: {ticker}",
                    "data": {},
                    "metadata": {
                        "symbol": ticker,
                        "provider": "EODHD",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "data": data,
                "metadata": {
                    "symbol": ticker,
                    "provider": "EODHD",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Ticker tape item error for {ticker}: {e}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "error",
                "message": f"Failed to fetch ticker item: {str(e)}",
                "data": {},
                "metadata": {
                    "symbol": ticker,
                    "provider": "EODHD",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        )

__all__ = ["router"]
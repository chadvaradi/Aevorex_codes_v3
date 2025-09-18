"""
Ticker Tape Data Endpoint - EODHD Only (MCP-Ready)
==================================================

Simplified ticker tape endpoints using only EODHD API.
No caching, no orchestrator - direct EODHD integration.
Now with full MCP compatibility and standardized responses.

MCP-READY FEATURES:
- StandardResponseBuilder integration
- EODHD-specific helper functions
- Comprehensive metadata (mcp_ready, cache_status, data_type)
- Enhanced error handling with error codes
- Provider-specific metadata
- Cache status tracking
- Data source identification
"""

from datetime import datetime
from typing import Annotated, Dict, Any, Optional

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
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    create_eodhd_warning_response,
    CacheStatus
)

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

@router.get("/", summary="Get ticker-tape data (EODHD-only, MCP-Ready)")
async def get_ticker_tape_root(
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    limit: Annotated[int, Query(description="Number of symbols to return", ge=1, le=50)] = 20,
    symbols: Annotated[Optional[str], Query(description="Comma-separated list of custom symbols (e.g., 'AAPL,MSFT,GOOGL')")] = None,
) -> JSONResponse:
    """
    Get real-time ticker tape data from EODHD API only.
    
    Returns live market data for multiple symbols without caching.
    Uses EODHD All World Extended API (300,000 requests/day).
    No fallback providers, no cache - direct EODHD integration.
    
    MCP-READY RESPONSE:
    - Standardized success/error responses
    - Comprehensive metadata (mcp_ready, cache_status, data_type)
    - Provider-specific information
    - Enhanced error handling with error codes
    - Data source identification
    """
    try:
        logger.info(f"TickerTape API request (limit={limit})")
        
        # Start processing time measurement
        start_time = datetime.utcnow()
        
        # Get symbols to fetch (custom or default list)
        if symbols:
            # Parse custom symbols from comma-separated string
            custom_symbols = [s.strip().upper() for s in symbols.split(',') if s.strip()]
            symbols_to_fetch = custom_symbols[:limit]
            logger.info(f"Using custom symbols: {symbols_to_fetch}")
        else:
            # Use default symbols
            symbols_to_fetch = DEFAULT_TICKER_SYMBOLS[:limit]
            logger.info(f"Using default symbols: {symbols_to_fetch}")
        
        symbols = symbols_to_fetch
        
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
                    # Check if all critical fields are "NA" or null (invalid symbol detection)
                    critical_fields = ["close", "change", "volume", "high", "low", "open"]
                    field_values = [data.get(field) for field in critical_fields]
                    
                    # If all critical fields are "NA" or null, treat as invalid symbol
                    if all(val == "NA" or val is None for val in field_values):
                        logger.warning(f"Invalid symbol detected: {symbol} - all critical fields are NA/null")
                        continue  # Skip this symbol, don't add to ticker_data
                    
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
            # MCP-ready error response for no data (likely invalid symbols)
            return JSONResponse(
                content=create_eodhd_error_response(
                    message="No valid ticker data available from EODHD - all symbols may be invalid",
                    error_code="SYMBOL_NOT_FOUND",
                    symbol="multiple",
                    data_type="ticker_tape"
                ),
                status_code=404  # Not Found - invalid symbols
            )
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # MCP-ready success response
        return JSONResponse(
            content=create_eodhd_success_response(
                data=ticker_data,
                data_type="ticker_tape",
                symbol="multiple",
                frequency="real_time",
                cache_status=CacheStatus.FRESH,
                provider_meta={
                    "total_symbols": len(ticker_data),
                    "requested_limit": limit,
                    "data_source": "eodhd_live",
                    "processing_time_ms": round(processing_time_ms, 2),
                    "symbols_processed": len(ticker_data),
                    "symbols_failed": limit - len(ticker_data),
                    "api_requests_made": len(ticker_data),
                    "cache_status": "fresh",
                    "data_freshness": "real_time",
                    "start_time": start_time.isoformat() + "Z",
                    "end_time": end_time.isoformat() + "Z"
                }
            ),
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Ticker tape endpoint error: {e}")
        
        # MCP-ready error response for unexpected errors
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch ticker tape data: {str(e)}",
                error_code="TICKER_TAPE_ERROR",
                symbol="multiple",
                data_type="ticker_tape"
            ),
            status_code=500  # Internal Server Error - unexpected error
        )

# Register alias
_register_no_slash_variant(router)

@router.get(
    "/item",
    summary="Get Ticker Tape Item Data (EODHD-only, MCP-Ready)",
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
    
    MCP-READY RESPONSE:
    - Standardized success/error responses
    - Comprehensive metadata (mcp_ready, cache_status, data_type)
    - Provider-specific information
    - Enhanced error handling with error codes
    - Data source identification
    """
    try:
        logger.info(f"Ticker tape /item called for symbol: {ticker}")
        
        # Start processing time measurement
        start_time = datetime.utcnow()
        
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
                # Check if all critical fields are "NA" or null (invalid symbol detection)
                critical_fields = ["close", "change", "volume", "high", "low", "open"]
                field_values = [raw_data.get(field) for field in critical_fields]
                
                # If all critical fields are "NA" or null, treat as invalid symbol
                if all(val == "NA" or val is None for val in field_values):
                    logger.warning(f"Invalid symbol detected: {ticker} - all critical fields are NA/null")
                    data = None
                else:
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
            # MCP-ready error response for invalid symbol
            return JSONResponse(
                content=create_eodhd_error_response(
                    message=f"Symbol not found or invalid: {ticker}",
                    error_code="SYMBOL_NOT_FOUND",
                    symbol=ticker,
                    data_type="ticker_tape_item"
                ),
                status_code=404  # Not Found - invalid symbol
            )
        
        # Calculate processing time
        end_time = datetime.utcnow()
        processing_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # MCP-ready success response
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="ticker_tape_item",
                symbol=ticker,
                frequency="real_time",
                cache_status=CacheStatus.FRESH,
                provider_meta={
                    "data_source": "eodhd_live",
                    "processing_time_ms": round(processing_time_ms, 2),
                    "api_request_made": True,
                    "cache_status": "fresh",
                    "data_freshness": "real_time",
                    "symbol_validation": "passed",
                    "start_time": start_time.isoformat() + "Z",
                    "end_time": end_time.isoformat() + "Z"
                }
            ),
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Ticker tape item error for {ticker}: {e}")
        
        # MCP-ready error response for unexpected errors
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch ticker item: {str(e)}",
                error_code="TICKER_ITEM_ERROR",
                symbol=ticker,
                data_type="ticker_tape_item"
            ),
            status_code=500  # Internal Server Error - unexpected error
        )

__all__ = ["router"]
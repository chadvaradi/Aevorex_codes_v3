"""
Company Overview Handler

Provides company profile and basic fundamental information including:
- Company description and business overview
- Key metrics (market cap, employees, sector, industry)
- Contact information and corporate details
- Recent news and events

Returns MCP-ready response with standardized metadata including:
- Cache status tracking (cached/fresh)
- Provider information (yahoo_finance)
- Data type classification (company_overview)
- Timestamp and processing time metadata
- Error codes for different failure scenarios
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from datetime import datetime

from backend.api.deps import get_cache_service
from backend.utils.cache_service import CacheService
from ..services.yahoo_service import YahooService
from ..services.cache_service import FundamentalsCacheService
from backend.utils.logger_config import get_logger
from backend.api.endpoints.shared.response_builder import (
    create_fundamentals_success_response,
    create_fundamentals_error_response,
    CacheStatus
)

logger = get_logger(__name__)

router = APIRouter()


@router.get("/overview/{symbol}", summary="Get company overview data")
async def get_company_overview(
    symbol: str,
    cache: Annotated[CacheService, Depends(get_cache_service)],
    force_refresh: Annotated[bool, Query(description="Force refresh of cached data")] = False,
) -> JSONResponse:
    """
    Get comprehensive company overview data including:
    - Company name, sector, industry
    - Market cap, employees
    - Contact information and business summary
    """
    try:
        logger.info(f"Fetching company overview for {symbol}")
        
        # Initialize services
        yahoo_service = YahooService()
        fundamentals_cache = FundamentalsCacheService(cache)
        
        # Try cache first (unless force refresh)
        if not force_refresh:
            cached_data = await fundamentals_cache.get_cached_overview(symbol)
            if cached_data:
                logger.info(f"Returning cached overview for {symbol}")
                
                # Update cache metadata for MCP compatibility
                cached_meta = cached_data["metadata"].copy()
                cached_meta["cache_status"] = "cached"
                cached_meta["last_updated"] = datetime.utcnow().isoformat() + "Z"
                cached_meta["mcp_ready"] = True
                
                # MCP-ready response with cached data
                return JSONResponse(
                    content=create_fundamentals_success_response(
                        data=cached_data["data"],
                        data_type="company_overview",
                        symbol=symbol,
                        cache_status=CacheStatus.CACHED,
                        provider_meta=cached_meta
                    ),
                    status_code=200
                )
        
        # Fetch fresh data
        logger.info(f"Fetching fresh overview data for {symbol}")
        overview_data = await yahoo_service.get_company_overview(symbol)
        
        if not overview_data:
            logger.warning(f"Company overview not found for symbol: {symbol}")
            
            # Enhanced error metadata for symbol not found
            error_meta = {
                "error_timestamp": datetime.utcnow().isoformat() + "Z",
                "error_type": "symbol_not_found",
                "retry_available": False,
                "suggested_actions": [
                    "Verify symbol format (e.g., AAPL, MSFT)",
                    "Check if symbol is listed on supported exchanges",
                    "Try alternative symbol formats"
                ]
            }
            
            return JSONResponse(
                content=create_fundamentals_error_response(
                    message=f"Company overview not found for symbol: {symbol}",
                    error_code="SYMBOL_NOT_FOUND",
                    symbol=symbol,
                    data_type="company_overview",
                    provider_meta=error_meta
                ),
                status_code=404
            )
        
        # Cache the fresh data
        await fundamentals_cache.set_cached_overview(symbol, overview_data)
        
        logger.info(f"Successfully returned overview for {symbol}")
        
        # Update fresh data metadata for MCP compatibility
        fresh_meta = overview_data["metadata"].copy()
        fresh_meta["cache_status"] = "fresh"
        fresh_meta["last_updated"] = datetime.utcnow().isoformat() + "Z"
        fresh_meta["mcp_ready"] = True
        
        # MCP-ready response with fresh data
        return JSONResponse(
            content=create_fundamentals_success_response(
                data=overview_data["data"],
                data_type="company_overview",
                symbol=symbol,
                cache_status=CacheStatus.FRESH,
                provider_meta=fresh_meta
            ),
            status_code=200
        )
        
    except HTTPException:
        # Re-raise HTTPException as it's already handled above
        raise
    except Exception as e:
        logger.error(f"Failed to fetch overview for {symbol}: {e}")
        
        # Enhanced error metadata for MCP compatibility
        error_meta = {
            "error_timestamp": datetime.utcnow().isoformat() + "Z",
            "error_type": "yahoo_api_error",
            "retry_available": True,
            "cache_fallback_available": not force_refresh
        }
        
        # MCP-ready error response for unexpected errors
        return JSONResponse(
            content=create_fundamentals_error_response(
                message=f"Failed to fetch company overview: {str(e)}",
                error_code="YAHOO_API_ERROR",
                symbol=symbol,
                data_type="company_overview",
                provider_meta=error_meta
            ),
            status_code=503
        )




__all__ = ["router"]

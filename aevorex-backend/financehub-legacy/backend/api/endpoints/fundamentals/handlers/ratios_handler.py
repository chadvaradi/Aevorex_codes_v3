"""
Financial Ratios Handler

Provides comprehensive financial ratios and metrics including:
- Valuation ratios (P/E, P/B, P/S, EV/EBITDA)
- Profitability ratios (ROE, ROA, gross margin, net margin)
- Debt ratios (debt-to-equity, interest coverage)
- Efficiency ratios (asset turnover, inventory turnover)
- Liquidity ratios (current ratio, quick ratio)

Returns MCP-ready response with standardized metadata including:
- Cache status tracking (cached/fresh)
- Provider information (yahoo_finance)
- Data type classification (financial_ratios)
- Timestamp and processing time metadata
- Error codes for different failure scenarios
- Comprehensive financial ratio data (21+ metrics)
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


@router.get("/ratios/{symbol}", summary="Get comprehensive financial ratios")
async def get_financial_ratios(
    symbol: str,
    cache: Annotated[CacheService, Depends(get_cache_service)],
    force_refresh: Annotated[bool, Query(description="Force refresh of cached data")] = False,
) -> JSONResponse:
    """
    Get comprehensive financial ratios including:
    - Valuation: P/E, P/B, PEG, EV/Revenue, EV/EBITDA
    - Profitability: ROE, ROA, profit margins, gross margins
    - Debt: debt-to-equity, total debt, cash per share
    - Liquidity: current ratio, quick ratio
    - Growth: earnings growth, revenue growth
    """
    try:
        logger.info(f"Fetching financial ratios for {symbol}")
        
        # Initialize services
        yahoo_service = YahooService()
        fundamentals_cache = FundamentalsCacheService(cache)
        
        # Try cache first (unless force refresh)
        if not force_refresh:
            cached_data = await fundamentals_cache.get_cached_ratios(symbol)
            if cached_data:
                logger.info(f"Returning cached ratios for {symbol}")
                
                # Normalize cached metadata for MCP compatibility
                cached_meta = cached_data["metadata"].copy() if cached_data.get("metadata") else {}
                cached_meta["cache_status"] = "cached"
                cached_meta["last_updated"] = datetime.utcnow().isoformat() + "Z"
                cached_meta["mcp_ready"] = True
                cached_meta["data_source"] = "yahoo_finance_cache"
                
                # MCP-ready response with cached data
                return JSONResponse(
                    content=create_fundamentals_success_response(
                        data=cached_data["data"],
                        data_type="financial_ratios",
                        symbol=symbol,
                        cache_status=CacheStatus.CACHED,
                        provider_meta=cached_meta
                    ),
                    status_code=200
                )
        
        # Fetch fresh data
        logger.info(f"Fetching fresh ratios data for {symbol}")
        ratios_data = await yahoo_service.get_financial_ratios(symbol)
        
        if not ratios_data:
            logger.warning(f"Financial ratios not found for symbol: {symbol}")
            
            # Enhanced error metadata for ratios not found
            error_meta = {
                "error_timestamp": datetime.utcnow().isoformat() + "Z",
                "error_type": "ratios_not_found",
                "retry_available": False,
                "data_source": "yahoo_finance_live",
                "cache_fallback_available": not force_refresh,
                "suggested_actions": [
                    "Verify symbol format (e.g., AAPL, MSFT)",
                    "Check if symbol is listed on supported exchanges",
                    "Ensure company has sufficient financial data for ratio calculations",
                    "Try alternative symbol formats or exchanges"
                ],
                "error_context": "financial_ratios_validation"
            }
            
            return JSONResponse(
                content=create_fundamentals_error_response(
                    message=f"Financial ratios not found for symbol: {symbol}",
                    error_code="RATIOS_NOT_FOUND",
                    symbol=symbol,
                    data_type="financial_ratios",
                    provider_meta=error_meta
                ),
                status_code=404
            )
        
        # Check if all data fields are null (invalid symbol detection)
        if ratios_data.get("data"):
            data_values = [v for v in ratios_data["data"].values() if v is not None]
            if len(data_values) == 0:
                logger.warning(f"All financial ratios are null for symbol: {symbol} - likely invalid symbol")
                
                # Enhanced error metadata for invalid symbol
                error_meta = {
                    "error_timestamp": datetime.utcnow().isoformat() + "Z",
                    "error_type": "symbol_not_found",
                    "retry_available": False,
                    "data_source": "yahoo_finance_live",
                    "cache_fallback_available": not force_refresh,
                    "suggested_actions": [
                        "Verify symbol format (e.g., AAPL, MSFT)",
                        "Check if symbol is listed on supported exchanges",
                        "Try alternative symbol formats or exchanges",
                        "Use overview endpoint to verify symbol validity"
                    ],
                    "error_context": "financial_ratios_invalid_symbol"
                }
                
                return JSONResponse(
                    content=create_fundamentals_error_response(
                        message=f"Symbol not found or invalid: {symbol}",
                        error_code="SYMBOL_NOT_FOUND",
                        symbol=symbol,
                        data_type="financial_ratios",
                        provider_meta=error_meta
                    ),
                    status_code=404
                )
        
        # Cache the fresh data
        await fundamentals_cache.set_cached_ratios(symbol, ratios_data)
        
        logger.info(f"Successfully returned ratios for {symbol}")
        
        # Normalize fresh data metadata for MCP compatibility
        fresh_meta = ratios_data["metadata"].copy() if ratios_data.get("metadata") else {}
        fresh_meta["cache_status"] = "fresh"
        fresh_meta["last_updated"] = datetime.utcnow().isoformat() + "Z"
        fresh_meta["mcp_ready"] = True
        fresh_meta["data_source"] = "yahoo_finance_live"
        fresh_meta["cache_fallback_available"] = True  # Can fallback to cache if needed
        
        # MCP-ready response with fresh data
        return JSONResponse(
            content=create_fundamentals_success_response(
                data=ratios_data["data"],
                data_type="financial_ratios",
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
        logger.error(f"Failed to fetch ratios for {symbol}: {e}")
        
        # Enhanced error metadata for unexpected errors
        error_meta = {
            "error_timestamp": datetime.utcnow().isoformat() + "Z",
            "error_type": "yahoo_api_error",
            "retry_available": True,
            "cache_fallback_available": not force_refresh,
            "error_context": "financial_ratios_calculation",
            "data_source": "yahoo_finance_live",
            "suggested_retry_delay_seconds": 30
        }
        
        # MCP-ready error response for unexpected errors
        return JSONResponse(
            content=create_fundamentals_error_response(
                message=f"Failed to fetch financial ratios: {str(e)}",
                error_code="YAHOO_API_ERROR",
                symbol=symbol,
                data_type="financial_ratios",
                provider_meta=error_meta
            ),
            status_code=503
        )


__all__ = ["router"]

"""
Financial Statements Handler

Provides comprehensive financial statement data including:
- Income Statement (P&L)
- Balance Sheet
- Cash Flow Statement
- Quarterly and annual financials
- Historical financial data

CURRENT IMPLEMENTATION STATUS:
- ✅ Symbol validation implemented (overview data check)
- ✅ Differentiated error handling (404 vs 402)
- ✅ MCP-ready error responses
- ❌ Premium data source integration (not implemented)
- ❌ Actual financial statements data (not available)

ERROR HANDLING STRATEGY:
- Invalid symbol → 404 + SYMBOL_NOT_FOUND
- Valid symbol → 402 + PREMIUM_DATA_REQUIRED

FUTURE ENHANCEMENT ROADMAP:
- Phase 1: Alpha Vantage integration (Income Statement, Balance Sheet, Cash Flow)
- Phase 2: EODHD Fundamentals API integration
- Phase 3: IEX Cloud Financial Statements API integration
- Phase 4: Quandl Financial Statements API integration

Returns MCP-ready error response with standardized metadata including:
- Error code: PREMIUM_DATA_REQUIRED / SYMBOL_NOT_FOUND
- Provider information (yahoo_finance)
- Data type classification (financial_statements)
- Clear messaging about data source limitations
- Suggested alternative data sources
- Alternative endpoints for basic financial data
- Premium data source recommendations
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
    create_fundamentals_error_response,
    CacheStatus
)

logger = get_logger(__name__)

router = APIRouter()


@router.get("/financials/{symbol}", summary="Get comprehensive financial statements")
async def get_financial_statements(
    symbol: str,
    cache: Annotated[CacheService, Depends(get_cache_service)],
    force_refresh: Annotated[bool, Query(description="Force refresh of cached data")] = False,
) -> JSONResponse:
    """
    Get comprehensive financial statements data including:
    - Income Statement: Revenue, Gross Profit, Operating Income, Net Income
    - Balance Sheet: Total Assets, Liabilities, Shareholder Equity
    - Cash Flow: Operating Cash Flow, Capital Expenditure, Free Cash Flow
    
    CURRENT IMPLEMENTATION:
    - Symbol validation implemented (overview data check)
    - Differentiated error handling (404 vs 402)
    - MCP-ready error responses
    - Premium data source integration NOT implemented
    
    ERROR HANDLING:
    - Invalid symbol → 404 + SYMBOL_NOT_FOUND
    - Valid symbol → 402 + PREMIUM_DATA_REQUIRED
    
    FUTURE ENHANCEMENT:
    - Premium data source integration planned
    - Alpha Vantage, EODHD, IEX Cloud, Quandl APIs
    - Actual financial statements data will be available
    """
    try:
        logger.info(f"Financial statements requested for {symbol} - checking symbol validity first")
        
        # Initialize services for symbol validation
        yahoo_service = YahooService()
        fundamentals_cache = FundamentalsCacheService(cache)
        
        # Step 1: Validate symbol by checking overview data
        logger.info(f"Validating symbol {symbol} using overview endpoint")
        try:
            overview_data = await yahoo_service.get_company_overview(symbol)
            
            # Check if overview data is valid (not all null values)
            if not overview_data or not overview_data.get("data"):
                logger.warning(f"Symbol {symbol} validation failed - no overview data available")
                raise ValueError("Invalid symbol - no overview data")
            
            # Check if all overview fields are null (invalid symbol detection)
            if overview_data.get("data"):
                data_values = [v for v in overview_data["data"].values() if v is not None]
                if len(data_values) == 0:
                    logger.warning(f"Symbol {symbol} validation failed - all overview data is null")
                    raise ValueError("Invalid symbol - all overview data is null")
            
            logger.info(f"Symbol {symbol} validation successful - proceeding with premium data required error")
            
        except Exception as e:
            logger.warning(f"Symbol validation failed for {symbol}: {e}")
            
            # Enhanced error metadata for invalid symbol
            error_meta = {
                "error_timestamp": datetime.utcnow().isoformat() + "Z",
                "error_type": "symbol_not_found",
                "retry_available": False,
                "data_source": "yahoo_finance_live",
                "cache_fallback_available": False,
                "suggested_actions": [
                    "Verify symbol format (e.g., AAPL, MSFT)",
                    "Check if symbol is listed on supported exchanges",
                    "Try alternative symbol formats or exchanges",
                    "Use overview endpoint to verify symbol validity"
                ],
                "error_context": "financial_statements_invalid_symbol"
            }
            
            # MCP-ready error response for invalid symbol
            return JSONResponse(
                content=create_fundamentals_error_response(
                    message=f"Symbol not found or invalid: {symbol}",
                    error_code="SYMBOL_NOT_FOUND",
                    symbol=symbol,
                    data_type="financial_statements",
                    provider_meta=error_meta
                ),
                status_code=404  # Not Found - invalid symbol
            )
        
        # Step 2: Symbol is valid, but financial statements require premium data
        logger.info(f"Symbol {symbol} is valid - returning premium data required error")
        
        # Enhanced error metadata for premium data required
        error_meta = {
            "error_timestamp": datetime.utcnow().isoformat() + "Z",
            "error_type": "premium_data_required",
            "retry_available": False,
            "data_source": "yahoo_finance_live",
            "cache_fallback_available": False,
            "suggested_actions": [
                "Use overview endpoint for basic company information",
                "Use ratios endpoint for financial ratios and metrics",
                "Use earnings endpoint for EPS and growth data",
                "Consider premium data sources (Alpha Vantage, EODHD, IEX) for financial statements"
            ],
            "error_context": "financial_statements_premium_required",
            "alternative_endpoints": [
                "/api/v1/fundamentals/overview/{symbol}",
                "/api/v1/fundamentals/ratios/{symbol}",
                "/api/v1/fundamentals/earnings/{symbol}"
            ],
            "premium_data_sources": [
                "Alpha Vantage - Financial Statements API",
                "EODHD - Fundamentals API",
                "IEX Cloud - Financial Statements API",
                "Quandl - Financial Statements API"
            ],
            "symbol_validation": "passed",
            "implementation_status": {
                "current_state": "error_handling_only",
                "premium_integration": "not_implemented",
                "data_availability": "not_available",
                "future_roadmap": [
                    "Phase 1: Alpha Vantage integration",
                    "Phase 2: EODHD Fundamentals API",
                    "Phase 3: IEX Cloud Financial Statements",
                    "Phase 4: Quandl Financial Statements"
                ]
            }
        }
        
        # MCP-ready error response for premium data required
        return JSONResponse(
            content=create_fundamentals_error_response(
                message="Financial statements require premium data source - Yahoo Finance API does not provide financial statements data",
                error_code="PREMIUM_DATA_REQUIRED",
                symbol=symbol,
                data_type="financial_statements",
                provider_meta=error_meta
            ),
            status_code=402  # Payment Required - indicates premium data needed
        )
        
    except Exception as e:
        logger.error(f"Unexpected error in financials handler for {symbol}: {e}")
        
        # Enhanced error metadata for unexpected errors
        error_meta = {
            "error_timestamp": datetime.utcnow().isoformat() + "Z",
            "error_type": "unexpected_error",
            "retry_available": True,
            "data_source": "yahoo_finance_live",
            "cache_fallback_available": False,
            "error_context": "financial_statements_handler_error",
            "suggested_retry_delay_seconds": 30
        }
        
        # MCP-ready error response for unexpected errors
        return JSONResponse(
            content=create_fundamentals_error_response(
                message=f"Unexpected error in financial statements handler: {str(e)}",
                error_code="HANDLER_ERROR",
                symbol=symbol,
                data_type="financial_statements",
                provider_meta=error_meta
            ),
            status_code=500
        )


__all__ = ["router"]

"""
Financial Statements Handler

Provides comprehensive financial statement data including:
- Income Statement (P&L)
- Balance Sheet
- Cash Flow Statement
- Quarterly and annual financials
- Historical financial data
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from backend.api.deps import get_cache_service
from backend.utils.cache_service import CacheService
from ..services.yahoo_service import YahooService
from ..services.cache_service import FundamentalsCacheService
from backend.utils.logger_config import get_logger

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
    """
    try:
        logger.info(f"Fetching financial statements for {symbol}")
        
        # Initialize services
        yahoo_service = YahooService()
        fundamentals_cache = FundamentalsCacheService(cache)
        
        # Try cache first (unless force refresh)
        if not force_refresh:
            cached_data = await fundamentals_cache.get_cached_financials(symbol)
            if cached_data:
                logger.info(f"Returning cached financials for {symbol}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=cached_data
                )
        
        # Fetch fresh data
        logger.info(f"Fetching fresh financials data for {symbol}")
        financials_data = await yahoo_service.get_financial_statements(symbol)
        
        if not financials_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial statements not found for symbol: {symbol}"
            )
        
        # Cache the fresh data
        await fundamentals_cache.set_cached_financials(symbol, financials_data)
        
        logger.info(f"Successfully returned financials for {symbol}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=financials_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch financials for {symbol}: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": f"Failed to fetch financial statements: {str(e)}",
                "symbol": symbol
            }
        )


__all__ = ["router"]

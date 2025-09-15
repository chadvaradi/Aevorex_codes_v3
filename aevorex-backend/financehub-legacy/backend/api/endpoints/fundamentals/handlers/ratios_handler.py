"""
Financial Ratios Handler

Provides comprehensive financial ratios and metrics including:
- Valuation ratios (P/E, P/B, P/S, EV/EBITDA)
- Profitability ratios (ROE, ROA, gross margin, net margin)
- Debt ratios (debt-to-equity, interest coverage)
- Efficiency ratios (asset turnover, inventory turnover)
- Liquidity ratios (current ratio, quick ratio)
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
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=cached_data
                )
        
        # Fetch fresh data
        logger.info(f"Fetching fresh ratios data for {symbol}")
        ratios_data = await yahoo_service.get_financial_ratios(symbol)
        
        if not ratios_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Financial ratios not found for symbol: {symbol}"
            )
        
        # Cache the fresh data
        await fundamentals_cache.set_cached_ratios(symbol, ratios_data)
        
        logger.info(f"Successfully returned ratios for {symbol}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=ratios_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch ratios for {symbol}: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": f"Failed to fetch financial ratios: {str(e)}",
                "symbol": symbol
            }
        )


__all__ = ["router"]

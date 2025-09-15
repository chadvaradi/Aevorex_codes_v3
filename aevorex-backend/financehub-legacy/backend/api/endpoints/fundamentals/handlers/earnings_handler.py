"""
Earnings Handler

Provides comprehensive earnings data including:
- Earnings per Share (EPS) history
- Earnings surprises and estimates
- Analyst guidance and recommendations
- Quarterly and annual earnings
- Earnings calendar and upcoming reports
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


@router.get("/earnings/{symbol}", summary="Get comprehensive earnings data")
async def get_earnings_data(
    symbol: str,
    cache: Annotated[CacheService, Depends(get_cache_service)],
    force_refresh: Annotated[bool, Query(description="Force refresh of cached data")] = False,
) -> JSONResponse:
    """
    Get comprehensive earnings data including:
    - Trailing and Forward EPS
    - Earnings growth rates (quarterly and annual)
    - Revenue growth
    - Analyst price targets and recommendations
    - Number of analyst opinions
    """
    try:
        logger.info(f"Fetching earnings data for {symbol}")
        
        # Initialize services
        yahoo_service = YahooService()
        fundamentals_cache = FundamentalsCacheService(cache)
        
        # Try cache first (unless force refresh)
        if not force_refresh:
            cached_data = await fundamentals_cache.get_cached_earnings(symbol)
            if cached_data:
                logger.info(f"Returning cached earnings for {symbol}")
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=cached_data
                )
        
        # Fetch fresh data
        logger.info(f"Fetching fresh earnings data for {symbol}")
        earnings_data = await yahoo_service.get_earnings_data(symbol)
        
        if not earnings_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Earnings data not found for symbol: {symbol}"
            )
        
        # Cache the fresh data
        await fundamentals_cache.set_cached_earnings(symbol, earnings_data)
        
        logger.info(f"Successfully returned earnings for {symbol}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=earnings_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch earnings for {symbol}: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": f"Failed to fetch earnings data: {str(e)}",
                "symbol": symbol
            }
        )


__all__ = ["router"]

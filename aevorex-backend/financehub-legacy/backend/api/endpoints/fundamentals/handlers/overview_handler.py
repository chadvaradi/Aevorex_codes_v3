"""
Company Overview Handler

Provides company profile and basic fundamental information including:
- Company description and business overview
- Key metrics (market cap, employees, sector, industry)
- Contact information and corporate details
- Recent news and events
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
                return JSONResponse(
                    status_code=status.HTTP_200_OK,
                    content=cached_data
                )
        
        # Fetch fresh data
        logger.info(f"Fetching fresh overview data for {symbol}")
        overview_data = await yahoo_service.get_company_overview(symbol)
        
        if not overview_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Company overview not found for symbol: {symbol}"
            )
        
        # Cache the fresh data
        await fundamentals_cache.set_cached_overview(symbol, overview_data)
        
        logger.info(f"Successfully returned overview for {symbol}")
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=overview_data
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to fetch overview for {symbol}: {e}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "message": f"Failed to fetch company overview: {str(e)}",
                "symbol": symbol
            }
        )




__all__ = ["router"]

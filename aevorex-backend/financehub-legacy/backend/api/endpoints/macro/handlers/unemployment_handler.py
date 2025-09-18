"""
Unemployment Handler

Provides Euro Area Unemployment Rate data endpoints.
Handles unemployment data via ECB API with proper SDMX headers.
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional
import logging

from backend.api.endpoints.macro.services.ecb_service import ECBService
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus
from backend.utils.cache_service import CacheService, get_cache_service

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Macro"]
)


@router.get("/", summary="Eurozone Unemployment Rate Time Series")
async def get_unemployment_data(
    start_date: Optional[date] = Query(None, description="Start date (ISO format)"),
    end_date: Optional[date] = Query(None, description="End date (ISO format)"),
    force_refresh: bool = Query(False, description="Force refresh cache"),
    cache_service: CacheService = Depends(get_cache_service)
) -> JSONResponse:
    """
    Get Eurozone unemployment rate time series data.
    Returns Euro Area unemployment rate data from ECB API.
    
    This endpoint fetches unemployment rate data directly from ECB API
    using proper SDMX headers to avoid blocking issues.
    
    Args:
        start_date: Optional start date for the data range (defaults to 1 year ago)
        end_date: Optional end date for the data range (defaults to today)
        force_refresh: Force refresh cache
        cache_service: Injected cache service
        
    Returns:
        JSONResponse containing unemployment data with MCP-ready format:
        - status: "success" | "error"
        - data: unemployment observations and statistics
        - meta: MCP-compatible metadata including:
          - provider: "ecb"
          - cache_status: "fresh" | "cached" | "error"
          - series_id: "unemployment_ea"
          - title: "Euro Area Unemployment Rate"
          - frequency: "monthly"
          - units: "percent"
          - last_updated: ISO timestamp
    """
    logger.info(f"Fetching unemployment data | start_date: {start_date}, end_date: {end_date}, force_refresh: {force_refresh}")
    
    try:
        # Initialize ECB service
        ecb_service = ECBService(cache_service)
        
        # Convert dates to strings if provided
        start_str = start_date.isoformat() if start_date else None
        end_str = end_date.isoformat() if end_date else None
        
        # Fetch unemployment data
        result = await ecb_service.get_unemployment_data(
            start_date=start_str,
            end_date=end_str,
            force_refresh=force_refresh
        )
        
        # Return result directly - ECBService already provides MCP-ready format
        if result.get("status") == "success":
            return JSONResponse(content=result, status_code=200)
        else:
            # Error response from service - return with appropriate status code
            status_code = 404 if "not found" in result.get("message", "").lower() else 400
            return JSONResponse(content=result, status_code=status_code)
        
    except Exception as e:
        logger.error(f"Error fetching unemployment data: {e} | Input: start_date={start_date}, end_date={end_date}, force_refresh={force_refresh}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=f"Failed to fetch unemployment data: {str(e)}",
            error_code="SERVICE_ERROR"
        )
        return JSONResponse(content=error_response, status_code=500)


__all__ = ["router"]
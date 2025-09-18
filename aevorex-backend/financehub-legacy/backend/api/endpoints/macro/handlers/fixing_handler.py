"""
Fixing Rates Handler

Provides fixing rates data endpoints for ECB €STR and Euribor.
Handles overnight and term fixing rates from official sources.
"""

from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.responses import JSONResponse
import logging

from backend.api.endpoints.macro.services.fixing_service import FixingService
from backend.api.endpoints.macro.services.euribor_service import EuriborService
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus
from backend.utils.cache_service import CacheService

def get_cache_service() -> CacheService:
    """Get a cache service instance."""
    return CacheService()

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/estr", summary="ECB €STR (Euro Short-Term Rate)")
async def get_estr_rate(
    date: str = Query(None, description="Date (ISO format, optional)"),
    cache=Depends(get_cache_service)
):
    """
    ECB €STR (Euro Short-Term Rate).
    Returns the latest ECB Euro Short-Term Rate (€STR) with MCP-ready response format.
    """
    logger.info("Fetching ECB €STR rate")
    service = FixingService(cache)
    try:
        result = await service.get_estr_rate(date)
        
        # Ensure response follows MCP format
        if result.get("status") == "success":
            return JSONResponse(content=result, status_code=status.HTTP_200_OK)
        else:
            error_response = StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.ECB,
                message=result.get("message", "Failed to fetch €STR rate"),
                error_code="ESTR_FETCH_ERROR",
                series_id="ECB_ESTR"
            )
            return error_response
            
    except Exception as e:
        logger.error(f"Error fetching €STR rate: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=f"Failed to fetch €STR rate: {str(e)}",
            error_code="ESTR_FETCH_ERROR",
            series_id="ECB_ESTR"
        )
        return error_response

@router.get("/euribor", summary="Get available Euribor tenors")
async def get_euribor_tenors(
    cache=Depends(get_cache_service)
):
    """
    Get list of available Euribor tenors.
    Returns available tenor periods for Euribor rates.
    """
    # Return static list of available Euribor tenors
    available_tenors = ["1M", "3M", "6M", "12M"]
    result = StandardResponseBuilder.create_macro_success_response(
        provider=MacroProvider.EMMI,
        data={"available_tenors": available_tenors},
        series_id="EURIBOR_TENORS",
        frequency="metadata",
        units="list",
        cache_status=CacheStatus.FRESH
    )
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)

@router.get("/euribor/{tenor}", summary="Get Euribor rate for specific tenor")
async def get_euribor_rate(
    tenor: str = Path(..., description="Tenor period (e.g. 1M, 3M, 6M, 12M)"),
    cache=Depends(get_cache_service)
):
    """
    Get Euribor rate for specific tenor.
    Returns Euribor rate for a specific tenor with MCP-ready response format.
    """
    logger.info(f"Fetching Euribor rate for tenor: {tenor}")
    service = FixingService(cache)
    try:
        result = await service.get_euribor_rate(tenor)
        
        # Return MCP-ready response directly from service
        return result
            
    except Exception as e:
        logger.error(f"Error fetching Euribor rate for tenor {tenor}: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.EMMI,
            message=f"Failed to fetch Euribor rate for {tenor}: {str(e)}",
            error_code="EURIBOR_FETCH_ERROR",
            series_id=f"EURIBOR_{tenor}"
        )
        return error_response


@router.get("/euribor-service/{tenor}", summary="Get Euribor rate using EuriborService")
async def get_euribor_rate_service(
    tenor: str = Path(..., description="Tenor period (e.g. 1M, 3M, 6M, 12M)"),
    force_refresh: bool = Query(False, description="Force refresh from source")
):
    """
    Get Euribor rate using EuriborService.
    Returns Euribor rate for a specific tenor with MCP-ready response format.
    """
    logger.info(f"Fetching Euribor rate using EuriborService | tenor: {tenor}, force_refresh: {force_refresh}")
    
    try:
        cache = await CacheService.create()
        service = EuriborService(cache=cache)
        result = await service.get_euribor_rate(tenor, force_refresh=force_refresh)
        
        # Return MCP-ready response directly from service
        return result
            
    except Exception as e:
        logger.error(f"Error fetching Euribor rate using EuriborService: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.EMMI,
            message=f"Failed to fetch Euribor rate: {str(e)}",
            error_code="EURIBOR_SERVICE_ERROR",
            series_id=f"EURIBOR_{tenor}"
        )
        return error_response


@router.get("/euribor-service/curve", summary="Get Euribor curve using EuriborService")
async def get_euribor_curve_service(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    force_refresh: bool = Query(False, description="Force refresh from source")
):
    """
    Get Euribor curve using EuriborService.
    Returns Euribor curve data with MCP-ready response format.
    """
    logger.info(f"Fetching Euribor curve using EuriborService | start_date: {start_date}, end_date: {end_date}, force_refresh: {force_refresh}")
    
    try:
        cache = await CacheService.create()
        service = EuriborService(cache=cache)
        result = await service.get_euribor_curve(start_date=start_date, end_date=end_date, force_refresh=force_refresh)
        
        # Return MCP-ready response directly from service
        return result
            
    except Exception as e:
        logger.error(f"Error fetching Euribor curve using EuriborService: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.EMMI,
            message=f"Failed to fetch Euribor curve: {str(e)}",
            error_code="EURIBOR_CURVE_ERROR",
            series_id="EURIBOR_CURVE"
        )
        return error_response


__all__ = ["router"]

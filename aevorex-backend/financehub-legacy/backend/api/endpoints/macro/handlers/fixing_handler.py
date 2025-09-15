"""
Fixing Rates Handler

Provides fixing rates data endpoints for ECB €STR and Euribor.
Handles overnight and term fixing rates from official sources.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Path
import logging

from backend.api.endpoints.macro.services.fixing_service import FixingService
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
    Get the latest ECB Euro Short-Term Rate (€STR).
    """
    logger.info("Fetching ECB €STR rate")
    service = FixingService(cache)
    try:
        rate_data = await service.get_estr_rate(date)
        return {"success": True, "data": rate_data}
    except Exception as e:
        logger.error(f"Error fetching €STR rate: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch €STR rate")

@router.get("/euribor/{tenor}", summary="Get Euribor rate for specific tenor")
async def get_euribor_rate(
    tenor: str = Path(..., description="Tenor period (e.g. 1M, 3M, 6M, 12M)"),
    cache=Depends(get_cache_service)
):
    """
    Get Euribor rate for specific tenor.
    Returns Euribor rate for a specific tenor.
    """
    logger.info(f"Fetching Euribor rate for tenor: {tenor}")
    service = FixingService(cache)
    try:
        rate_data = await service.get_euribor_rate(tenor)
        return {"success": True, "data": rate_data}
    except ValueError as ve:
        logger.warning(f"Invalid tenor provided: {tenor}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error fetching Euribor rate for tenor {tenor}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch Euribor rate")


__all__ = ["router"]

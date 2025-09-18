"""
BUBOR Handler

Provides Hungarian Interbank Offered Rate (BUBOR) data endpoints.
Handles BUBOR curve data from MNB (Hungarian National Bank) official Excel files.
Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
"""

from fastapi import APIRouter, Depends, Query, Path
from datetime import date
from typing import Optional
import logging

from backend.api.endpoints.macro.services.bubor_service import BuborService
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus

logger = logging.getLogger(__name__)

router = APIRouter()



@router.get("/", summary="Get complete BUBOR curve data")
async def get_bubor_curve(
    start_date: Optional[date] = Query(None, description="Start date for BUBOR curve (ISO format)"),
    end_date: Optional[date] = Query(None, description="End date for BUBOR curve (ISO format)"),
):
    """
    Get complete BUBOR curve data from MNB official Excel file.
    Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
    Returns all available tenors for the most recent date.
    """
    try:
        bubor_service = BuborService()
        result = await bubor_service.get_bubor_curve(
            start_date=start_date.isoformat() if start_date else None,
            end_date=end_date.isoformat() if end_date else None,
        )
        
        # Return MCP-ready response with standardized meta fields
        if result.get("status") == "success":
            return StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data=result["data"],
                series_id="BUBOR_CURVE",
                cache_status=CacheStatus.FRESH,
                frequency="daily",
                units="percent"
            )
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in get_bubor_curve endpoint: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.MNB,
            message=f"Failed to fetch BUBOR curve: {str(e)}",
            error_code="BUBOR_CURVE_ERROR",
            series_id="BUBOR_CURVE"
        )
        return error_response


@router.get("/latest", summary="Get latest BUBOR fixing")
async def get_latest_bubor():
    """
    Get the latest BUBOR fixing from MNB official Excel file.
    Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
    Returns all available tenors for the most recent date.
    """
    try:
        bubor_service = BuborService()
        result = await bubor_service.get_latest_bubor()
        
        # Return MCP-ready response with standardized meta fields
        if result.get("status") == "success":
            return StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data=result["data"],
                series_id="BUBOR_LATEST",
                cache_status=CacheStatus.FRESH,
                frequency="daily",
                units="percent"
            )
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in get_latest_bubor endpoint: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.MNB,
            message=f"Failed to fetch latest BUBOR: {str(e)}",
            error_code="BUBOR_LATEST_ERROR",
            series_id="BUBOR_LATEST"
        )
        return error_response


@router.get("/metadata", summary="Get BUBOR metadata and available tenors")
async def get_bubor_metadata():
    """
    Get BUBOR metadata and available tenors from MNB official Excel file.
    Source: https://www.mnb.hu/letoltes/bubor2.xls.
    Returns available tenors and metadata information.
    """
    try:
        bubor_service = BuborService()
        result = await bubor_service.get_bubor_metadata()
        
        # Return MCP-ready response with standardized meta fields
        if result.get("status") == "success":
            return StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data=result["data"],
                series_id="BUBOR_METADATA",
                cache_status=CacheStatus.FRESH,
                frequency="metadata",
                units="list"
            )
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in get_bubor_metadata endpoint: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.MNB,
            message=f"Failed to fetch BUBOR metadata: {str(e)}",
            error_code="BUBOR_METADATA_ERROR",
            series_id="BUBOR_METADATA"
        )
        return error_response


@router.get("/{tenor}", summary="Get BUBOR rate for specific tenor")
async def get_bubor_rate(
    tenor: str = Path(..., description="Tenor period (e.g. 1W, 3M, 6M)"),
):
    """
    Get BUBOR rate for specific tenor from MNB official Excel file.
    Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
    Returns the latest BUBOR rate for a specific tenor.
    """
    try:
        bubor_service = BuborService()
        result = await bubor_service.get_bubor_rate(tenor=tenor)
        
        # Return MCP-ready response with standardized meta fields
        if result.get("status") == "success":
            return StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data=result["data"],
                series_id=f"BUBOR_{tenor}",
                cache_status=CacheStatus.FRESH,
                frequency="daily",
                units="percent"
            )
        else:
            return result
            
    except Exception as e:
        logger.error(f"Error in get_bubor_rate endpoint: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.MNB,
            message=f"Failed to fetch BUBOR rate for {tenor}: {str(e)}",
            error_code="BUBOR_RATE_ERROR",
            series_id=f"BUBOR_{tenor}"
        )
        return error_response

__all__ = ["router"]

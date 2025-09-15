"""
BUBOR Handler

Provides Hungarian Interbank Offered Rate (BUBOR) data endpoints.
Handles BUBOR curve data from MNB (Hungarian National Bank) official Excel files.
Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
"""

from fastapi import APIRouter, Depends, Query, Path, status
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional

from backend.api.endpoints.macro.services.bubor_service import BuborService
# Cache service temporarily disabled for testing

router = APIRouter()



@router.get("/", response_class=JSONResponse, summary="Get complete BUBOR curve data")
async def get_bubor_curve(
    start_date: Optional[date] = Query(None, description="Start date for BUBOR curve (ISO format)"),
    end_date: Optional[date] = Query(None, description="End date for BUBOR curve (ISO format)"),
    period: Optional[str] = Query(None, description="Period for BUBOR curve"),
):
    """
    Get complete BUBOR curve data from MNB official Excel file.
    Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
    Returns all available tenors for the most recent date.
    """
    bubor_service = BuborService()
    result = await bubor_service.get_bubor_curve(
        start_date=start_date.isoformat() if start_date else None,
        end_date=end_date.isoformat() if end_date else None,
    )
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get("/latest", response_class=JSONResponse, summary="Get latest BUBOR fixing")
async def get_latest_bubor():
    """
    Get the latest BUBOR fixing from MNB official Excel file.
    Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
    Returns all available tenors for the most recent date.
    """
    bubor_service = BuborService()
    result = await bubor_service.get_latest_bubor()
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)


@router.get("/{tenor}", response_class=JSONResponse, summary="Get BUBOR rate for specific tenor")
async def get_bubor_rate(
    tenor: str = Path(..., description="Tenor period (e.g. 1W, 3M, 6M)"),
):
    """
    Get BUBOR rate for specific tenor from MNB official Excel file.
    Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
    Returns the latest BUBOR rate for a specific tenor.
    """
    bubor_service = BuborService()
    result = await bubor_service.get_bubor_rate(tenor=tenor)
    return JSONResponse(content=result, status_code=status.HTTP_200_OK)

__all__ = ["router"]

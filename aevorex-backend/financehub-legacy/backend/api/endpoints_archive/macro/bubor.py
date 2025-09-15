"""
BUBOR API Endpoint
==================

Clean API router for BUBOR (Budapest Interbank Offered Rate) data.
Business logic moved to core/services/macro/bubor_service.py
"""

from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional

from backend.utils.date_utils import PeriodEnum
from backend.core.services.macro_service import MacroDataService
from backend.core.services.macro.bubor_service import BuborService
from backend.api.endpoints.macro.ecb import get_macro_service

router = APIRouter(prefix="", tags=["Macroeconomic Data", "BUBOR"])


@router.get("", summary="Get BUBOR Rates", status_code=status.HTTP_200_OK)
async def get_bubor_curve(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(
        None, description="Start date for historical data (YYYY-MM-DD)"
    ),
    end_date: Optional[date] = Query(
        None, description="End date for historical data (YYYY-MM-DD)"
    ),
    period: Optional[PeriodEnum] = Query(
        None, description="Time period for data retrieval (1d, 1w, 1m, 6m, 1y)"
    ),
):
    """
    Returns historical BUBOR rates for a specified date range.
    Enhanced with period support for consistent API interface.
    """
    # Delegate to core service
    result = await BuborService.get_bubor_rates(
        macro_service=service,
        start_date=start_date,
        end_date=end_date,
        period=period,
    )

    if result["status"] == "success":
        return result
    else:
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)


@router.get(
    "/",
    summary="Get BUBOR Rates (trailing slash alias)",
    include_in_schema=False,
    status_code=status.HTTP_200_OK,
)
async def get_bubor_curve_trailing_slash(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    period: Optional[PeriodEnum] = Query(None),
):
    """Thin wrapper – delegates to canonical no-slash handler."""
    return await get_bubor_curve(service, start_date, end_date, period)

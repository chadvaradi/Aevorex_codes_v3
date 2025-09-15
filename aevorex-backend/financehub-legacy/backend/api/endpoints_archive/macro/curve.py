"""
Yield Curve API Endpoint
========================

Clean API router for yield curve data.
Business logic moved to core/services/macro/curve_service.py
"""

from typing import Dict, Any

from fastapi import APIRouter, Path, status, Depends, Query, Request

from .ecb.utils import get_macro_service
from backend.core.services.macro_service import MacroDataService
from backend.core.services.macro.curve_service import CurveService
from backend.config import settings

curve_router = APIRouter(tags=["Macro – Yield Curves"], prefix="/curve")


@curve_router.get(
    "/{source}",
    summary="Get yield curve for a given source (ECB or UST)",
    status_code=status.HTTP_200_OK,
)
async def get_curve(
    request: Request,
    source: str = Path(..., description="Data source, e.g. 'ecb' or 'ust'"),
    days: int = Query(
        0, description="How many days of history to include. 0 = latest only (default)."
    ),
    macro_service: MacroDataService = Depends(get_macro_service),
) -> Dict[str, Any]:
    """
    Return yield curve data for the requested provider.

    • **ecb** – uses YC dataflow via MacroDataService.get_ecb_yield_curve
    • **ust** – fetches historical U.S. Treasury curve from FRED
    """
    # Plan clamp
    plan = (
        request.session.get("plan", "free") if hasattr(request, "session") else "free"
    )
    hdr_plan = request.headers.get("x-plan")
    if settings.ENVIRONMENT.NODE_ENV != "production" and hdr_plan:
        plan = hdr_plan

    # Delegate to core service
    result = await CurveService.get_curve_data(
        source=source,
        days=days,
        plan=plan,
        macro_service=macro_service,
    )

    return result

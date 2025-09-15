"""ECB Yield Curve Endpoints - Thin Router"""

from datetime import date
from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Query, Request
from backend.core.services.macro_service import MacroDataService
from backend.core.services.macro.specials.yield_curve_service import (
    build_yield_curve_response,
)
from backend.api.endpoints.macro.models import ECBPeriod
from backend.api.endpoints.macro.utils import get_macro_service
from backend.core.services.macro.specials.yield_curve_service import resolve_plan

router = APIRouter(prefix="/yield-curve", tags=["ECB Yield Curve"])


@router.get("/", summary="Get ECB Yield Curve")
async def get_ecb_yield_curve(
    service: Annotated[MacroDataService, Depends(get_macro_service)],
    request: Request,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    period: Optional[ECBPeriod] = Query(None, description="Relative period e.g. 1m,6m"),
):
    plan = resolve_plan(request)
    return await build_yield_curve_response(service, start_date, end_date, period, plan)


@router.get("/historical", summary="Get Historical U.S. Treasury Yield Curve")
async def get_us_treasury_historical_yield_curve(
    service: Annotated[MacroDataService, Depends(get_macro_service)],
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
):

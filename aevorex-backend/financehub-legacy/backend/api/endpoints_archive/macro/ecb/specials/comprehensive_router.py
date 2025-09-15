"""ECB Comprehensive Endpoints - Consolidated Router"""

from datetime import date
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, Query
from backend.core.services.macro_service import MacroDataService
from backend.core.services.macro.specials.comprehensive_service import (
    get_comprehensive_response,
    get_monetary_aggregates_response,
    get_inflation_indicators_response,
)
from ..utils import get_macro_service

comprehensive_router = APIRouter()


@comprehensive_router.get(
    "/comprehensive", summary="Get Comprehensive ECB Economic Data"
)
async def get_ecb_comprehensive_data(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    period: Optional[str] = Query(None),
) -> Dict[str, Any]:
    return await get_comprehensive_response(service, start_date, end_date, period)


@comprehensive_router.get("/monetary-aggregates", summary="Get ECB Monetary Aggregates")
async def get_ecb_monetary_aggregates(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    period: Optional[str] = Query(None),
) -> Dict[str, Any]:
    return await get_monetary_aggregates_response(service, start_date, end_date, period)


@comprehensive_router.get("/inflation", summary="Get ECB Inflation Indicators")
async def get_ecb_inflation_indicators(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    period: Optional[str] = Query(None),
) -> Dict[str, Any]:
    return await get_inflation_indicators_response(
        service, start_date, end_date, period
    )

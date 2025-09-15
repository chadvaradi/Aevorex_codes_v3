"""ECB Rates Endpoints - Thin Router"""

from datetime import date
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from backend.core.services.macro_service import MacroDataService
from backend.api.endpoints.macro.utils import get_macro_service
from backend.core.services.macro.specials.rates_service import get_short_end_rates
from backend.core.services.macro.specials.rates_extended_service import (
    monetary_policy_response,
    retail_rates_response,
)

router = APIRouter(prefix="/rates", tags=["ECB Rates"])


@router.get("/", summary="Get ECB Short-End Rates (BUBOR parity)")
async def get_ecb_rates(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    period: Optional[str] = Query(
        None, description="Relative period e.g. 1d,1w,1m,6m,1y"
    ),
) -> Dict[str, Any]:
    return await get_short_end_rates(service, start_date, end_date, period)


@router.get("/monetary-policy", summary="Get ECB Monetary Policy Info")
async def get_ecb_monetary_policy(
    service: MacroDataService = Depends(get_macro_service),
) -> Dict[str, Any]:
    return await monetary_policy_response(service)


@router.get("/retail", summary="Get ECB Retail Bank Interest Rates")
async def get_ecb_retail_rates(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    period: Optional[str] = Query(None, description="Relative period e.g. 1m,6m,1y"),
) -> Dict[str, Any]:
    return await retail_rates_response(service, start_date, end_date, period)

"""ECB FX Endpoints - Consolidated Router"""

from datetime import date
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query
from ..utils import get_macro_service
from backend.core.services.macro_service import MacroDataService
from backend.core.services.macro.specials.fx_service import (
    build_fx_response,
    get_ecb_fx_rates_legacy,
)

fx_router = APIRouter()


@fx_router.get("/fx", summary="Get ECB FX rates for major currencies")
async def get_ecb_fx(
    service: MacroDataService = Depends(get_macro_service),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
) -> Dict[str, Any]:
    return await build_fx_response(service, start_date, end_date)


@fx_router.get("/fx/legacy", summary="Get ECB FX Rates (Legacy)")
async def get_ecb_fx_rates_legacy_endpoint(
    service: MacroDataService = Depends(get_macro_service),
    currency_pair: str = Query(
        "USD+GBP+JPY+CHF", description="Currency pairs to fetch"
    ),
) -> Dict[str, Any]:
    return await get_ecb_fx_rates_legacy(service, currency_pair)

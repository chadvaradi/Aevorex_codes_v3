"""ECB Balance of Payments Endpoints - Consolidated Router"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.utils.cache_service import CacheService
from backend.api.deps import get_cache_service
from backend.core.services.macro.specials.bop_service import (
    build_bop_response,
    get_bop_components,
    bop_health_check,
)

router = APIRouter(prefix="/bop", tags=["ECB Balance of Payments"])


@router.get("/", summary="Get ECB Balance of Payments Data")
async def get_ecb_bop(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    cache_service: CacheService = Depends(get_cache_service),
    components: Optional[str] = Query(
        None, description="Comma-separated BOP components"
    ),
):
    comp = [c.strip() for c in components.split(",")] if components else None
    return await build_bop_response(cache_service, start_date, end_date, comp)


@router.get("/components", summary="Get Available BOP Components")
async def get_bop_components_endpoint():
    return get_bop_components()


@router.get("/health", summary="BOP Endpoint Health Check")
async def bop_health_check_endpoint():
    return bop_health_check()

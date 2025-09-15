"""ECB Securities Issues Statistics Endpoints - Consolidated Router"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.utils.cache_service import CacheService
from backend.api.deps import get_cache_service
from backend.core.services.macro.specials.sec_service import (
    build_sec_response,
    get_sec_components,
    sec_health_check,
)

router = APIRouter(prefix="/sec", tags=["ECB SEC"])


@router.get("/")
async def get_sec(
    start: Optional[date] = Query(None, description="Start date YYYY-MM-DD"),
    end: Optional[date] = Query(None, description="End date YYYY-MM-DD"),
    cache: CacheService = Depends(get_cache_service),
):
    return await build_sec_response(cache, start, end)


@router.get("/components", summary="Get Available SEC Components")
async def get_sec_components_endpoint():
    return get_sec_components()


@router.get("/health", summary="SEC Endpoint Health Check")
async def sec_health_check_endpoint():
    return sec_health_check()

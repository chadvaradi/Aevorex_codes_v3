# backend/api/endpoints/macro/ecb/sts_router.py

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from backend.utils.cache_service import CacheService
from backend.api.deps import get_cache_service
from backend.core.services.macro.specials.sts_service import (
    get_sts_response,
    get_latest_sts_response,
    get_indicators_response,
)

router = APIRouter(prefix="/sts", tags=["ECB Short-term Statistics"])


@router.get("/")
async def get_sts(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    indicators: Optional[str] = Query(
        None, description="Comma-separated indicator list"
    ),
    cache: CacheService = Depends(get_cache_service),
):
    return await get_sts_response(start_date, end_date, indicators, cache)


@router.get("/latest")
async def latest_sts(
    indicators: Optional[str] = Query(
        None, description="Comma-separated indicator list"
    ),
    cache: CacheService = Depends(get_cache_service),
):
    return await get_latest_sts_response(indicators, cache)


@router.get("/indicators")
async def sts_indicators():
    return get_indicators_response()

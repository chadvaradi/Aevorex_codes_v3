"""
Technical Analysis Stock Data Endpoint
Provides technical analysis data using TechnicalService and calculators.
Canonical endpoint: /{ticker}/full
"""

import logging

import httpx
from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse

from backend.utils.cache_service import CacheService
from backend.api.deps import get_cache_service, get_http_client
from backend.core.services.stock.technical_service import TechnicalService
from backend.middleware.jwt_auth.deps import get_current_user
from backend.middleware.subscription_middleware import require_active_subscription

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/technical-analysis",
    tags=["Stock Technical Analysis"],
)

# Alias for consistent import name across codebase
technical_analysis_router = router


@router.get(
    "/{ticker}/full",
    summary="Get technical analysis for a stock",
    tags=["Technical Analysis"],
    dependencies=[Depends(require_active_subscription())],
)
async def get_technical_analysis_stock(
    ticker: str,
    force_refresh: bool = Query(
        False, description="Force a refresh from the API, bypassing the cache"
    ),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    cache: CacheService = Depends(get_cache_service),
    current_user: dict = Depends(get_current_user),
):
    service = TechnicalService()
    try:
        data = await service.get_technical_analysis(
            symbol=ticker.upper(),
            client=http_client,
            cache=cache,
            force_refresh=force_refresh,
        )
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "data": data.model_dump() if hasattr(data, "model_dump") else data,
            },
        )
    except Exception as e:
        logger.error(f"Technical analysis full endpoint error for {ticker}: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Failed to fetch technical analysis for {ticker}: {str(e)}",
                "data": {},
            },
        )

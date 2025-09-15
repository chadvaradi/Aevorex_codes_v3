"""
Federal Reserve Search Handler

Provides FRED data search and discovery endpoints.
Handles series search, metadata queries, and data exploration.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from typing import Annotated
from backend.api.deps import get_cache_service
from backend.utils.cache_service import CacheService
# from ..services.fed_service import FedService  # Service not implemented
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

router = APIRouter(
    tags=["Macro"]
)


@router.get("/series")
async def search_fred_series(
    query: Annotated[str, Query(description="Search query for FRED series")],
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of results to return")] = 20,
    offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    force_refresh: Annotated[bool, Query(description="Force refresh from FRED API")] = False,
    cache: Annotated[CacheService, Depends(get_cache_service)] = None,
):
    """
    Search FRED time series by keyword.
    """
    fed_service = FedService(cache)
    try:
        if not force_refresh:
            cached = await fed_service.get_cached_search(query, limit, offset)
            if cached is not None:
                logger.info(f"Returned cached FRED search results for query: {query}")
                return JSONResponse(content=cached)
        # Fetch from FRED and update cache
        results = await fed_service.fetch_fred_search(query, limit=limit, offset=offset)
        await fed_service.set_cached_search(query, limit, offset, results)
        logger.info(f"Fetched FRED search results for query: {query} from FRED API")
        return JSONResponse(content=results)
    except Exception as exc:
        logger.error(f"FRED search failed for query '{query}': {exc}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="FRED search service unavailable")


@router.get("/metadata/{series_id}")
async def get_series_metadata(
    series_id: str,
    force_refresh: Annotated[bool, Query(description="Force refresh from FRED API")] = False,
    cache: Annotated[CacheService, Depends(get_cache_service)] = None,
):
    """
    Get metadata for specific FRED series.
    """
    fed_service = FedService(cache)
    try:
        if not force_refresh:
            cached = await fed_service.get_cached_metadata(series_id)
            if cached is not None:
                logger.info(f"Returned cached FRED metadata for series_id: {series_id}")
                return JSONResponse(content=cached)
        result = await fed_service.fetch_fred_metadata(series_id)
        await fed_service.set_cached_metadata(series_id, result)
        logger.info(f"Fetched FRED metadata for series_id: {series_id} from FRED API")
        return JSONResponse(content=result)
    except Exception as exc:
        logger.error(f"FRED metadata fetch failed for series_id '{series_id}': {exc}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="FRED metadata service unavailable")


@router.get("/related/{series_id}")
async def get_related_series(
    series_id: str,
    force_refresh: Annotated[bool, Query(description="Force refresh from FRED API")] = False,
    cache: Annotated[CacheService, Depends(get_cache_service)] = None,
):
    """
    Get related FRED series.
    """
    fed_service = FedService(cache)
    try:
        if not force_refresh:
            cached = await fed_service.get_cached_related(series_id)
            if cached is not None:
                logger.info(f"Returned cached related FRED series for series_id: {series_id}")
                return JSONResponse(content=cached)
        result = await fed_service.fetch_fred_related(series_id)
        await fed_service.set_cached_related(series_id, result)
        logger.info(f"Fetched related FRED series for series_id: {series_id} from FRED API")
        return JSONResponse(content=result)
    except Exception as exc:
        logger.error(f"FRED related fetch failed for series_id '{series_id}': {exc}")
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="FRED related service unavailable")


__all__ = ["router"]

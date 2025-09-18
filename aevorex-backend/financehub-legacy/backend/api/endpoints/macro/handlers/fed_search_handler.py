"""
Federal Reserve Search Handler

Provides FRED data search and discovery endpoints.
Handles series search, metadata queries, and data exploration.
MCP-ready response format for AI agent integration.
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
from typing import Annotated
from backend.api.deps import get_cache_service
from backend.utils.cache_service import CacheService
from ..services.fed_service import FedService
from backend.utils.logger_config import get_logger
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus

logger = get_logger(__name__)

router = APIRouter(
    tags=["Macro"]
)


@router.get("/series", summary="Search FRED Time Series")
async def search_fred_series(
    query: Annotated[str, Query(description="Search query for FRED series")],
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum number of results to return")] = 20,
    offset: Annotated[int, Query(ge=0, description="Result offset")] = 0,
    force_refresh: Annotated[bool, Query(description="Force refresh from FRED API")] = False,
    cache: Annotated[CacheService, Depends(get_cache_service)] = None,
):
    """
    Search FRED time series by keyword with MCP-ready response format.
    
    Returns standardized search results with comprehensive metadata for AI agent integration.
    """
    fed_service = FedService(cache)
    try:
        if not force_refresh:
            cached = await fed_service.get_cached_search(query, limit, offset)
            if cached is not None:
                logger.info(f"Returned cached FRED search results for query: {query}")
                return JSONResponse(
                    status_code=200,
                    content=StandardResponseBuilder.create_macro_success_response(
                        provider=MacroProvider.FRED,
                        data={
                            "series": cached.get("seriess", []) if cached else [],
                            "count": cached.get("count", 0) if cached else 0,
                            "offset": cached.get("offset", 0) if cached else 0,
                            "limit": cached.get("limit", limit) if cached else limit
                        },
                        series_id="search_results",
                        cache_status=CacheStatus.CACHED
                    )
                )
        
        # Fetch from FRED and update cache
        results = await fed_service.fetch_fred_search(query, limit=limit, offset=offset)
        await fed_service.set_cached_search(query, limit, offset, results)
        logger.info(f"Fetched FRED search results for query: {query} from FRED API")
        
        return JSONResponse(
            status_code=200,
            content=StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.FRED,
                data={
                    "series": results.get("series", results.get("seriess", [])) if results else [],
                    "count": results.get("count", 0) if results else 0,
                    "offset": results.get("offset", 0) if results else 0,
                    "limit": results.get("limit", limit) if results else limit
                },
                series_id="search_results",
                cache_status=CacheStatus.FRESH
            )
        )
    except Exception as exc:
        logger.error(f"FRED search failed for query '{query}': {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.FRED,
                message="FRED search service unavailable",
                error_code="SERVICE_UNAVAILABLE"
            )
        )


@router.get("/metadata/{series_id}", summary="Get FRED Series Metadata")
async def get_series_metadata(
    series_id: str,
    force_refresh: Annotated[bool, Query(description="Force refresh from FRED API")] = False,
    cache: Annotated[CacheService, Depends(get_cache_service)] = None,
):
    """
    Get metadata for specific FRED series with MCP-ready response format.
    
    Returns comprehensive series information including title, description, frequency, units, and observation dates.
    """
    fed_service = FedService(cache)
    try:
        if not force_refresh:
            cached = await fed_service.get_cached_metadata(series_id)
            if cached is not None:
                logger.info(f"Returned cached FRED metadata for series_id: {series_id}")
                return JSONResponse(
                    status_code=200,
                    content=StandardResponseBuilder.create_macro_success_response(
                        provider=MacroProvider.FRED,
                        data={
                            "series": cached.get("seriess", []) if cached else []
                        },
                        series_id=series_id,
                        cache_status=CacheStatus.CACHED
                    )
                )
        
        result = await fed_service.fetch_fred_metadata(series_id)
        await fed_service.set_cached_metadata(series_id, result)
        logger.info(f"Fetched FRED metadata for series_id: {series_id} from FRED API")
        
        return JSONResponse(
            status_code=200,
            content=StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.FRED,
                data={
                    "series": result.get("series", result.get("seriess", [])) if result else []
                },
                series_id=series_id,
                cache_status=CacheStatus.FRESH
            )
        )
    except Exception as exc:
        logger.error(f"FRED metadata fetch failed for series_id '{series_id}': {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.FRED,
                message="FRED metadata service unavailable",
                error_code="SERVICE_UNAVAILABLE",
                series_id=series_id
            )
        )


@router.get("/related/{series_id}", summary="Get Related FRED Series")
async def get_related_series(
    series_id: str,
    force_refresh: Annotated[bool, Query(description="Force refresh from FRED API")] = False,
    cache: Annotated[CacheService, Depends(get_cache_service)] = None,
):
    """
    Get related FRED series with MCP-ready response format.
    
    Returns series that are related to the specified series based on tag-based relationships.
    """
    fed_service = FedService(cache)
    try:
        if not force_refresh:
            cached = await fed_service.get_cached_related(series_id)
            if cached is not None:
                logger.info(f"Returned cached related FRED series for series_id: {series_id}")
                return JSONResponse(
                    status_code=200,
                    content=StandardResponseBuilder.create_macro_success_response(
                        provider=MacroProvider.FRED,
                        data={
                            "series": cached.get("seriess", []) if cached else [],
                            "count": cached.get("count", 0) if cached else 0,
                            "offset": cached.get("offset", 0) if cached else 0,
                            "limit": cached.get("limit", 20) if cached else 20
                        },
                        series_id=series_id,
                        cache_status=CacheStatus.CACHED
                    )
                )
        
        result = await fed_service.get_related_series(series_id)
        await fed_service.set_cached_related(series_id, result)
        logger.info(f"Fetched related FRED series for series_id: {series_id} from FRED API")
        
        return JSONResponse(
            status_code=200,
            content=StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.FRED,
                data={
                    "series": result.get("series", result.get("seriess", [])) if result else [],
                    "count": result.get("count", 0) if result else 0,
                    "offset": result.get("offset", 0) if result else 0,
                    "limit": result.get("limit", 20) if result else 20
                },
                series_id=series_id,
                cache_status=CacheStatus.FRESH
            )
        )
    except Exception as exc:
        logger.error(f"FRED related fetch failed for series_id '{series_id}': {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.FRED,
                message="FRED related service unavailable",
                error_code="SERVICE_UNAVAILABLE",
                series_id=series_id
            )
        )


__all__ = ["router"]

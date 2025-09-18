
"""
Search API Endpoint - MCP-Ready
===============================

Professional ticker search endpoint with MCP compatibility.
Provides standardized search results for MCP agents.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from backend.api.dependencies.eodhd_client import get_eodhd_client
from backend.api.dependencies.tier import get_current_tier
from backend.api.endpoints.shared.response_builder import (
    StandardResponseBuilder,
    CacheStatus,
    MacroProvider
)
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/", summary="Search Ticker - MCP-Ready")
async def search_ticker(
    query: str = Query(..., description="Ticker search query"),
    eodhd_client = Depends(get_eodhd_client),
    tier: str = Depends(get_current_tier)
):
    """
    Search for ticker symbols with MCP-ready response format.
    
    Returns standardized search results for MCP agents with:
    - Standardized response structure (status, meta, data)
    - Provider metadata (search, query, cache_status)
    - MCP compatibility flags
    - Error handling with proper HTTP status codes
    """
    if tier not in ("pro", "enterprise"):
        return JSONResponse(
            content=StandardResponseBuilder.error(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                error_message="This endpoint is available for pro and enterprise tiers only.",
                meta={
                    "provider": "search",
                    "query": query,
                    "tier": tier,
                    "mcp_ready": True,
                    "cache_status": "error"
                }
            ),
            status_code=status.HTTP_402_PAYMENT_REQUIRED
        )
    
    try:
        logger.info(f"Search API request for query: {query}")
        
        # EODHD search endpoint: /search/{query}
        result = await eodhd_client.get(f"/search/{query}")
        
        # Create MCP-ready response
        return JSONResponse(
            content=StandardResponseBuilder.success(
                data=result,
                meta={
                    "provider": "eodhd",
                    "mcp_ready": True,
                    "data_type": "search_results",
                    "query": query,
                    "cache_status": CacheStatus.FRESH.value,
                    "frequency": "metadata",
                    "units": "list"
                }
            ),
            status_code=200
        )
        
    except Exception as e:
        logger.error(f"Search API error for query '{query}': {e}")
        
        return JSONResponse(
            content=StandardResponseBuilder.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error_message=f"EODHD search error: {str(e)}",
                meta={
                    "provider": "search",
                    "query": query,
                    "tier": tier,
                    "mcp_ready": True,
                    "cache_status": "error"
                }
            ),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


__all__ = ["router"]
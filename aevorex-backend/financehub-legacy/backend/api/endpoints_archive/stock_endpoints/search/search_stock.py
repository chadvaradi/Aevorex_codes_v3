"""
Stock Search Endpoint
Provides search functionality for stock symbols and company names
"""

import logging
import os
import httpx
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()
from backend.api.deps import get_http_client
from backend.config import settings


class SearchResult(BaseModel):
    """Single search result"""

    symbol: str = Field(..., description="Stock ticker symbol")
    name: str = Field(..., description="Company name")
    exchange: str | None = Field(None, description="Exchange name")
    type: str = Field(default="stock", description="Security type")


class SearchResponse(BaseModel):
    """Search response model"""

    status: str = Field("success", description="Request status")
    query: str = Field(..., description="Original search query")
    results: list[SearchResult] = Field(
        default_factory=list, description="Search results"
    )
    total_results: int = Field(0, description="Total number of results")
    limit: int = Field(..., description="Applied limit")


# Removed static POPULAR_STOCKS to comply with no-mock policy


@router.get("/search", response_model=SearchResponse)
async def search_stocks(
    q: str | None = Query(
        None, description="Search query (symbol or company name)", min_length=1
    ),
    limit: int = Query(10, description="Maximum number of results", ge=1, le=50),
    http_client: httpx.AsyncClient = Depends(get_http_client),
):
    """
    Search for stocks by symbol or company name

    This endpoint provides fast search functionality for stock symbols and company names.
    It searches through a curated list of popular stocks for quick results.

    Args:
        q: Search query (can be symbol like 'AAPL' or company name like 'Apple')
        limit: Maximum number of results to return (1-50)

    Returns:
        SearchResponse with matching stocks
    """
    try:
        logger.info(f"Stock search request: query='{q}', limit={limit}")
        query = (q or "").strip()
        if not query:
            return SearchResponse(
                status="success", query="", results=[], total_results=0, limit=limit
            )

        # Resolve API key (env or settings)
        api_key = (
            os.getenv("FINBOT_API_KEYS__EODHD")
            or os.getenv("EODHD_API_KEY")
            or (
                settings.API_KEYS.EODHD.get_secret_value()
                if getattr(settings, "API_KEYS", None)
                and getattr(settings.API_KEYS, "EODHD", None)
                else None
            )
        )
        if not api_key:
            logger.warning(
                "EODHD API key missing – returning empty results per no-mock policy"
            )
            return SearchResponse(
                status="error", query=query, results=[], total_results=0, limit=limit
            )

        # EODHD Search API
        url = f"https://eodhd.com/api/search/{httpx.utils.quote(query)}"
        params = {"api_token": api_key, "limit": str(limit)}
        try:
            resp = await http_client.get(url, params=params, timeout=10.0)
            resp.raise_for_status()
            data = resp.json() or []
            items: list[SearchResult] = []
            for it in data[:limit]:
                symbol = it.get("Code") or it.get("Symbol") or ""
                name = it.get("Name") or ""
                exchange = it.get("Exchange") or it.get("ExchangeName") or None
                sec_type = (it.get("Type") or "stock").lower()
                if symbol and name:
                    items.append(
                        SearchResult(
                            symbol=symbol, name=name, exchange=exchange, type=sec_type
                        )
                    )
            return SearchResponse(
                status="success",
                query=query,
                results=items,
                total_results=len(items),
                limit=limit,
            )
        except httpx.HTTPError as http_err:
            logger.error(f"EODHD search HTTP error for '{query}': {http_err}")
            return SearchResponse(
                status="error", query=query, results=[], total_results=0, limit=limit
            )
    except Exception as e:
        logger.error(f"Error in stock search: {e}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "error",
                "message": f"Search failed: {str(e)}",
                "results": [],
                "query": q,
                "limit": limit,
            },
        )

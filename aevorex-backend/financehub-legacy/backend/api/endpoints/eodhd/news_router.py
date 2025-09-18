

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
import os
import httpx
from typing import Optional
from backend.api.dependencies.eodhd_client import get_eodhd_client
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)

# Dependency: get http_client (should be provided elsewhere in the app)
async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client

router = APIRouter()

def get_env() -> str:
    return os.environ.get("ENV", "development")

def get_plan(request: Request) -> str:
    # Try to get plan from request.state, or default to 'free'
    return getattr(getattr(request, "state", None), "plan", "free")

@router.get("/")
async def get_eodhd_news(
    request: Request,
    tickers: Optional[str] = Query(None, description="Comma separated tickers"),
    limit: int = Query(20, ge=1, le=100, description="Number of news items"),
    lang: str = Query("en", description="Language"),
    from_date: Optional[str] = Query(None, description="From date (ISO format)"),
    http_client: httpx.AsyncClient = Depends(get_http_client),
    eodhd_client = Depends(get_eodhd_client),
):
    # Paywall: Only allow pro/team/enterprise in production
    env = get_env()
    plan = get_plan(request)
    if env == "production" and plan not in {"pro", "team", "enterprise"}:
        return JSONResponse(
            status_code=402,
            content=create_eodhd_error_response(
                message="Payment Required: Upgrade your plan to access this endpoint",
                error_code="PAYMENT_REQUIRED",
                data_type="eodhd_news"
            ),
        )
    
    # Build EODHD API request
    base_url = "https://eodhd.com/api/news"
    params = {
        "api_token": eodhd_client.api_key,
        "limit": limit,
        "lang": lang,
    }
    if tickers:
        params["s"] = tickers
    if from_date:
        params["from"] = from_date
    
    try:
        response = await http_client.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="eodhd_news",
                frequency="realtime",
                cache_status=CacheStatus.FRESH,
                provider_meta={"tickers": tickers, "limit": limit, "lang": lang, "from": from_date}
            ),
            status_code=200
        )
    except httpx.HTTPStatusError as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD News API error: {e.response.text}",
                error_code="EODHD_NEWS_API_ERROR",
                data_type="eodhd_news"
            ),
            status_code=e.response.status_code
        )
    except Exception as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Internal server error: {str(e)}",
                error_code="INTERNAL_ERROR",
                data_type="eodhd_news"
            ),
            status_code=500
        )
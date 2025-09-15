from __future__ import annotations

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from httpx import AsyncClient

from backend.api.deps import get_http_client
from backend.config import settings

router = APIRouter(prefix="/fed/series", tags=["US Fed Search"])


def _plan_from_request(request: Request) -> str:
    plan = (
        request.session.get("plan", "free") if hasattr(request, "session") else "free"
    )
    hdr_plan = request.headers.get("x-plan")
    if settings.ENVIRONMENT.NODE_ENV != "production" and hdr_plan:
        plan = hdr_plan
    return plan


@router.get("/search", summary="Search FRED series")
async def search_series(
    request: Request,
    q: str = Query(..., description="Search text"),
    limit: Optional[int] = Query(None),
    offset: int = Query(0, ge=0),
    order_by: str = Query("search_rank"),
    sort_order: str = Query("desc"),
    http: Annotated[AsyncClient, Depends(get_http_client)] = None,
):
    plan = _plan_from_request(request)
    if settings.API_KEYS.FRED is None:
        raise HTTPException(status_code=503, detail="FRED API key missing")
    api_key = settings.API_KEYS.FRED.get_secret_value()

    # Plan-based cap
    if limit is None:
        limit = 20 if plan == "free" else (100 if plan == "pro" else 500)
    limit = max(1, min(limit, 500))

    params = {
        "api_key": api_key,
        "file_type": "json",
        "search_text": q,
        "limit": str(limit),
        "offset": str(offset),
        "order_by": order_by,
        "sort_order": sort_order,
    }
    url = "https://api.stlouisfed.org/fred/series/search"
    try:
        resp = await http.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"FRED search unavailable: {e}")

    return {
        "status": "success",
        "metadata": {
            "source": "FRED",
            "last_updated": date.today().isoformat(),
            "plan": plan,
            "limit": limit,
            "offset": offset,
        },
        "data": payload.get("seriess") or payload.get("series") or [],
    }


@router.get("/search/tags", summary="Search FRED series tags")
async def search_series_tags(
    request: Request,
    q: str = Query(..., description="Search text for series"),
    http: Annotated[AsyncClient, Depends(get_http_client)] = None,
):
    plan = _plan_from_request(request)
    if settings.API_KEYS.FRED is None:
        raise HTTPException(status_code=503, detail="FRED API key missing")
    api_key = settings.API_KEYS.FRED.get_secret_value()
    params = {
        "api_key": api_key,
        "file_type": "json",
        "series_search_text": q,
    }
    url = "https://api.stlouisfed.org/fred/series/search/tags"
    try:
        resp = await http.get(url, params=params)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"FRED tags unavailable: {e}")

    return {
        "status": "success",
        "metadata": {
            "source": "FRED",
            "plan": plan,
            "last_updated": date.today().isoformat(),
        },
        "data": payload.get("tags", []),
    }

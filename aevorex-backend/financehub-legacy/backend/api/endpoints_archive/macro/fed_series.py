from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from httpx import AsyncClient

from backend.config import settings
from backend.api.deps import get_http_client
from backend.core.fetchers.macro.fred_client import _fetch_series_observations
from time import perf_counter
from backend.core.metrics import METRICS_EXPORTER

router = APIRouter(prefix="/fed/series", tags=["US Fed Series"])


@router.get("/{series_id}/observations", summary="FRED series observations")
async def get_series_observations(
    request: Request,
    series_id: str = Path(..., description="FRED series ID, e.g., CPIAUCSL, UNRATE"),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    frequency: Optional[str] = Query(
        None, description="FRED frequency param, e.g., m,q,a"
    ),
    units: Optional[str] = Query(
        None, description="FRED units param, e.g., pc1 (YoY %)"
    ),
    http: Annotated[AsyncClient, Depends(get_http_client)] = None,
):
    plan = (
        request.session.get("plan", "free") if hasattr(request, "session") else "free"
    )
    hdr_plan = request.headers.get("x-plan")
    if settings.ENVIRONMENT.NODE_ENV != "production" and hdr_plan:
        plan = hdr_plan

    if end_date is None:
        end_date = date.today()
    if start_date is None:
        if plan == "free":
            start_date = end_date - timedelta(days=7)
        elif plan == "pro":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365 * 5)

    if settings.API_KEYS.FRED is None:
        raise HTTPException(status_code=503, detail="FRED API key missing")
    api_key = settings.API_KEYS.FRED.get_secret_value()

    if not series_id or len(series_id) > 32:
        raise HTTPException(status_code=400, detail="Invalid series_id")

    _t0 = perf_counter()
    data = await _fetch_series_observations(
        http, api_key, series_id, start_date, end_date, frequency, units
    )
    METRICS_EXPORTER.observe_fred_request(perf_counter() - _t0)

    return {
        "status": "success",
        "metadata": {
            "source": "FRED",
            "unit": units or "",
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "series": series_id,
            "plan": plan,
        },
        "data": data,
    }

"""Fed policy rates endpoint (EFFR/IORB, etc.)

No fallbacks. History window gated by plan.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from httpx import AsyncClient

from backend.config import settings
from backend.utils.logger_config import get_logger
from backend.api.deps import get_http_client
from backend.core.fetchers.macro.fred_client import fetch_fred_series_matrix
from time import perf_counter
from backend.core.metrics import METRICS_EXPORTER

router = APIRouter(prefix="/fed", tags=["US Fed"])
logger = get_logger(__name__)


@router.get("/policy", summary="Fed policy rate series (FRED)")
async def get_fed_policy(
    request: Request,
    series: List[str] = Query(
        ["EFFR"], description="FRED series IDs, e.g., EFFR, IORB"
    ),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    http: Annotated[AsyncClient, Depends(get_http_client)] = None,
):
    # Entitlement window
    plan = (
        request.session.get("plan", "free") if hasattr(request, "session") else "free"
    )
    hdr_plan = request.headers.get("x-plan")
    if settings.ENVIRONMENT.NODE_ENV != "production" and hdr_plan:
        plan = hdr_plan

    if end_date is None:
        end_date = date.today()
    if start_date is None:
        # default: 7d for free; 30d pro; 5y team/ent
        if plan == "free":
            start_date = end_date - timedelta(days=7)
        elif plan == "pro":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=365 * 5)

    if settings.API_KEYS.FRED is None:
        raise HTTPException(status_code=503, detail="FRED API key missing")
    api_key = settings.API_KEYS.FRED.get_secret_value()

    try:
        _t0 = perf_counter()
        matrix = await fetch_fred_series_matrix(
            http, api_key, series, start_date, end_date
        )
        METRICS_EXPORTER.observe_fred_request(perf_counter() - _t0)
    except Exception as e:
        METRICS_EXPORTER.inc_fred_error(type(e).__name__)
        logger.error("FRED fetch failed: %s", e)
        raise HTTPException(status_code=503, detail="FRED provider unavailable")

    return {
        "status": "success",
        "metadata": {
            "source": "FRED",
            "unit": "%",
            "last_updated": date.today().isoformat(),
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
            "series": series,
            "plan": plan,
        },
        "data": matrix,
    }



from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from typing import Optional

from backend.api.deps import get_http_client
from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings

router = APIRouter()

@router.get("/", summary="Run EODHD Screener")
async def run_screener(
    filters: Optional[str] = Query(None, description="Filters in JSON format: [['field','operation','value']]"),
    signals: Optional[str] = Query(None, description="Signals: signal1,signal2,signalN"),
    sort: Optional[str] = Query(None, description="Sort field: field_name.(asc|desc)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0, le=999),
    http_client: AsyncClient = Depends(get_http_client),
):
    # Paywall check: only allow certain plans in production
    allowed_plans = {"pro", "team", "enterprise"}
    if settings.ENVIRONMENT == "production" and getattr(settings, "PLAN", None) not in allowed_plans:
        return JSONResponse(
            status_code=402,
            content={"status": "error", "detail": "Upgrade required for screener access in production."},
        )

    # Build URL according to EODHD documentation
    url = f"https://eodhd.com/api/screener?api_token={eodhd_settings.API_KEY}&limit={limit}&offset={offset}"
    
    if filters:
        url += f"&filters={filters}"
    if signals:
        url += f"&signals={signals}"
    if sort:
        url += f"&sort={sort}"
    
    response = await http_client.get(url)
    if response.status_code == 200:
        return JSONResponse(content=response.json())
    else:
        return JSONResponse(
            status_code=response.status_code,
            content={"status": "error", "detail": f"Upstream error: {response.status_code}"},
        )

# Export router
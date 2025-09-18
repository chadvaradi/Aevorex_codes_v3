

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from typing import Optional

from backend.api.deps import get_http_client
from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)

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
            content=create_eodhd_error_response(
                message="Upgrade required for screener access in production",
                error_code="PAYMENT_REQUIRED",
                data_type="eodhd_screener"
            ),
        )

    # Build URL according to EODHD documentation
    url = f"https://eodhd.com/api/screener?api_token={eodhd_settings.API_KEY}&limit={limit}&offset={offset}"
    
    if filters:
        url += f"&filters={filters}"
    if signals:
        url += f"&signals={signals}"
    if sort:
        url += f"&sort={sort}"
    
    try:
        response = await http_client.get(url)
        response.raise_for_status()
        raw_data = response.json()
        
        # Extract the actual data array from nested structure for consistency
        # EODHD screener returns {"data": [...]}, we want just [...]
        data = raw_data.get("data", []) if isinstance(raw_data, dict) and "data" in raw_data else raw_data
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="eodhd_screener",
                frequency="realtime",
                cache_status=CacheStatus.FRESH,
                provider_meta={"filters": filters, "signals": signals, "sort": sort, "limit": limit, "offset": offset}
            ),
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"EODHD Screener API error: {str(e)}",
                error_code="EODHD_SCREENER_ERROR",
                data_type="eodhd_screener"
            ),
            status_code=500
        )

# Export router
"""
EODHD Forex Endpoints
Provides access to forex pairs, quotes, intraday, daily, historical, splits, dividends, and adjusted data.
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse
from httpx import AsyncClient
from backend.config.eodhd import settings as eodhd_settings
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)

router = APIRouter()

BASE_URL = "https://eodhd.com/api"


async def fetch_from_eodhd(endpoint: str, params: dict) -> dict:
    """Helper to fetch data from EODHD API."""
    if not eodhd_settings.API_KEY:
        raise HTTPException(status_code=503, detail="EODHD API key not configured.")

    params["api_token"] = eodhd_settings.API_KEY
    params["fmt"] = "json"

    async with AsyncClient() as client:
        url = f"{BASE_URL}/{endpoint}"
        resp = await client.get(url, params=params)
        if resp.status_code != 200:
            raise HTTPException(
                status_code=resp.status_code,
                detail=f"EODHD API error: {resp.text}",
            )
        return resp.json()


@router.get("/pairs", summary="List available forex pairs")
async def list_forex_pairs():
    """Return all supported forex pairs."""
    # Note: EODHD doesn't have a dedicated forex pairs endpoint
    # Return a list of common forex pairs instead
    common_forex_pairs = [
        {"pair": "EURUSD", "name": "Euro/US Dollar"},
        {"pair": "GBPUSD", "name": "British Pound/US Dollar"},
        {"pair": "USDJPY", "name": "US Dollar/Japanese Yen"},
        {"pair": "USDCHF", "name": "US Dollar/Swiss Franc"},
        {"pair": "AUDUSD", "name": "Australian Dollar/US Dollar"},
        {"pair": "USDCAD", "name": "US Dollar/Canadian Dollar"},
        {"pair": "NZDUSD", "name": "New Zealand Dollar/US Dollar"},
        {"pair": "EURGBP", "name": "Euro/British Pound"},
        {"pair": "EURJPY", "name": "Euro/Japanese Yen"},
        {"pair": "GBPJPY", "name": "British Pound/Japanese Yen"},
    ]
    
    # MCP-ready response with standardized format
    return JSONResponse(
        content=create_eodhd_success_response(
            data={"forex_pairs": common_forex_pairs},
            data_type="forex_pairs",
            frequency="static",
            cache_status=CacheStatus.FRESH
        ),
        status_code=200
    )


@router.get("/quote", summary="Get latest forex quote")
async def forex_quote(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Get the latest quote for a forex pair."""
    try:
        data = await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="forex_quote",
                symbol=pair,
                frequency="realtime",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except HTTPException as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch forex quote: {e.detail}",
                error_code="FOREX_QUOTE_ERROR",
                symbol=pair,
                data_type="forex_quote"
            ),
            status_code=e.status_code
        )


@router.get("/intraday", summary="Get intraday forex data")
async def forex_intraday(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
    interval: str = Query("5m", description="Interval, e.g. 1m,5m,15m,1h"),
):
    """Get intraday forex data for a pair."""
    try:
        data = await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="forex_intraday",
                symbol=pair,
                frequency="intraday",
                cache_status=CacheStatus.FRESH,
                provider_meta={"interval": interval}
            ),
            status_code=200
        )
    except HTTPException as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch forex intraday data: {e.detail}",
                error_code="FOREX_INTRADAY_ERROR",
                symbol=pair,
                data_type="forex_intraday"
            ),
            status_code=e.status_code
        )


@router.get("/endofday", summary="Get daily OHLCV forex data")
async def forex_endofday(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Get daily OHLCV data for a forex pair."""
    try:
        data = await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="forex_endofday",
                symbol=pair,
                frequency="daily",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except HTTPException as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch forex endofday data: {e.detail}",
                error_code="FOREX_ENDOFDAY_ERROR",
                symbol=pair,
                data_type="forex_endofday"
            ),
            status_code=e.status_code
        )


@router.get("/history", summary="Get historical forex data")
async def forex_history(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
    from_date: str = Query(..., alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(..., alias="to", description="End date in YYYY-MM-DD format"),
):
    """Get historical forex data for a pair between two dates."""
    try:
        data = await fetch_from_eodhd(
            f"real-time/{pair}.FOREX",
            {"from": from_date, "to": to_date},
        )
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="forex_history",
                symbol=pair,
                frequency="daily",
                cache_status=CacheStatus.FRESH,
                provider_meta={"from": from_date, "to": to_date}
            ),
            status_code=200
        )
    except HTTPException as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch forex history data: {e.detail}",
                error_code="FOREX_HISTORY_ERROR",
                symbol=pair,
                data_type="forex_history"
            ),
            status_code=e.status_code
        )


@router.get("/splits", summary="Get forex splits data (not supported)")
async def forex_splits(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Splits data is not supported for forex pairs."""
    return JSONResponse(
        content=create_eodhd_error_response(
            message="Splits data is not applicable or supported for forex pairs",
            error_code="FOREX_SPLITS_NOT_SUPPORTED",
            symbol=pair,
            data_type="forex_splits"
        ),
        status_code=400
    )


@router.get("/dividends", summary="Get forex dividends data (not supported)")
async def forex_dividends(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Dividends data is not supported for forex pairs."""
    return JSONResponse(
        content=create_eodhd_error_response(
            message="Dividends data is not applicable or supported for forex pairs",
            error_code="FOREX_DIVIDENDS_NOT_SUPPORTED",
            symbol=pair,
            data_type="forex_dividends"
        ),
        status_code=400
    )


@router.get("/adjusted", summary="Get adjusted forex data")
async def forex_adjusted(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Get adjusted data for a forex pair."""
    try:
        data = await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})
        
        # MCP-ready response with standardized format
        return JSONResponse(
            content=create_eodhd_success_response(
                data=data,
                data_type="forex_adjusted",
                symbol=pair,
                frequency="daily",
                cache_status=CacheStatus.FRESH
            ),
            status_code=200
        )
    except HTTPException as e:
        return JSONResponse(
            content=create_eodhd_error_response(
                message=f"Failed to fetch forex adjusted data: {e.detail}",
                error_code="FOREX_ADJUSTED_ERROR",
                symbol=pair,
                data_type="forex_adjusted"
            ),
            status_code=e.status_code
        )

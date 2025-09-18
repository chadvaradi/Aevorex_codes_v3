from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse
import httpx
from typing import Optional
from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings
from backend.core.fetchers.common._fetcher_constants import EODHD_BASE_URL
from backend.api.dependencies.eodhd_client import get_eodhd_client
from backend.api.endpoints.shared.response_builder import (
    create_eodhd_success_response,
    create_eodhd_error_response,
    CacheStatus
)

router = APIRouter()

@router.get("/indicators", summary="Get technical indicators data")
async def get_technical_indicators(
    request: Request,
    symbol: str = Query(..., description="Stock symbol"),
    indicator: str = Query(..., description="Technical indicator (e.g. sma, ema, rsi, macd, bbands, stoch, vwap, atr, adx, cci, obv)"),
    from_date: Optional[str] = Query(None, alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: Optional[str] = Query(None, alias="to", description="End date in YYYY-MM-DD format"),
    interval: Optional[str] = Query("1d", description="Interval (e.g. 1m, 5m, 1h, 1d)"),
    eodhd_client = Depends(get_eodhd_client)
):
    url = f"{EODHD_BASE_URL}/technical/{symbol}"
    params = {
        "api_token": eodhd_client.api_key,
        "fmt": "json",
        "function": indicator,
        "interval": interval
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # MCP-ready response with standardized format
            return JSONResponse(
                content=create_eodhd_success_response(
                    data=data,
                    data_type="technical_indicators",
                    symbol=symbol,
                    frequency="daily" if interval == "1d" else "intraday",
                    cache_status=CacheStatus.FRESH,
                    provider_meta={"indicator": indicator, "interval": interval, "from": from_date, "to": to_date}
                ),
                status_code=200
            )
        except httpx.HTTPStatusError as e:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message=f"Error fetching technical indicator data: {e.response.text}",
                    error_code="TECHNICAL_INDICATORS_ERROR",
                    symbol=symbol,
                    data_type="technical_indicators"
                ),
                status_code=e.response.status_code
            )
        except Exception as e:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message=f"Internal server error: {str(e)}",
                    error_code="INTERNAL_ERROR",
                    symbol=symbol,
                    data_type="technical_indicators"
                ),
                status_code=500
            )

@router.get("/screener", summary="Get screener data")
async def get_technical_screener(
    request: Request,
    symbol: str = Query(..., description="Stock symbol"),
    function: str = Query(..., description="Technical function (e.g. sma, ema, rsi, macd)"),
    from_date: Optional[str] = Query(None, alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: Optional[str] = Query(None, alias="to", description="End date in YYYY-MM-DD format"),
    interval: Optional[str] = Query("1d", description="Interval (e.g. 1m, 5m, 1h, 1d)"),
    eodhd_client = Depends(get_eodhd_client)
):
    url = f"{EODHD_BASE_URL}/screener"
    params = {
        "api_token": eodhd_client.api_key,
        "fmt": "json"
    }
    if from_date:
        params["from"] = from_date
    if to_date:
        params["to"] = to_date

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params)
            response.raise_for_status()
            raw_data = response.json()
            
            # Extract the actual data array from nested structure for consistency
            # EODHD screener returns {"data": [...]}, we want just [...]
            data = raw_data.get("data", []) if isinstance(raw_data, dict) and "data" in raw_data else raw_data
            
            # MCP-ready response with standardized format
            return JSONResponse(
                content=create_eodhd_success_response(
                    data=data,
                    data_type="technical_screener",
                    symbol=symbol,
                    frequency="daily" if interval == "1d" else "intraday",
                    cache_status=CacheStatus.FRESH,
                    provider_meta={"function": function, "interval": interval, "from": from_date, "to": to_date}
                ),
                status_code=200
            )
        except httpx.HTTPStatusError as e:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message=f"Error fetching screener data: {e.response.text}",
                    error_code="TECHNICAL_SCREENER_ERROR",
                    symbol=symbol,
                    data_type="technical_screener"
                ),
                status_code=e.response.status_code
            )
        except Exception as e:
            return JSONResponse(
                content=create_eodhd_error_response(
                    message=f"Internal server error: {str(e)}",
                    error_code="INTERNAL_ERROR",
                    symbol=symbol,
                    data_type="technical_screener"
                ),
                status_code=500
            )


__all__ = ["router"]

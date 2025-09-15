from fastapi import APIRouter, HTTPException, Query, Depends, Request
from fastapi.responses import JSONResponse
import httpx
from typing import Optional
from backend.config import settings
from backend.config.eodhd import settings as eodhd_settings
from backend.core.fetchers.common._fetcher_constants import EODHD_BASE_URL
from backend.api.dependencies.eodhd_client import get_eodhd_client

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
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching technical indicator data: {response.text}")
        return JSONResponse(content=response.json())

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
        response = await client.get(url, params=params)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching screener data: {response.text}")
        return JSONResponse(content=response.json())


__all__ = ["router"]

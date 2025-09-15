"""
EODHD Forex Endpoints
Provides access to forex pairs, quotes, intraday, daily, historical, splits, dividends, and adjusted data.
"""

from fastapi import APIRouter, Query, HTTPException
from httpx import AsyncClient
from backend.config.eodhd import settings as eodhd_settings

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
    return {"forex_pairs": common_forex_pairs}


@router.get("/quote", summary="Get latest forex quote")
async def forex_quote(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Get the latest quote for a forex pair."""
    return await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})


@router.get("/intraday", summary="Get intraday forex data")
async def forex_intraday(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
    interval: str = Query("5m", description="Interval, e.g. 1m,5m,15m,1h"),
):
    """Get intraday forex data for a pair."""
    return await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})


@router.get("/endofday", summary="Get daily OHLCV forex data")
async def forex_endofday(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Get daily OHLCV data for a forex pair."""
    return await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})


@router.get("/history", summary="Get historical forex data")
async def forex_history(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
    from_date: str = Query(..., alias="from", description="Start date in YYYY-MM-DD format"),
    to_date: str = Query(..., alias="to", description="End date in YYYY-MM-DD format"),
):
    """Get historical forex data for a pair between two dates."""
    return await fetch_from_eodhd(
        f"real-time/{pair}.FOREX",
        {"from": from_date, "to": to_date},
    )


@router.get("/splits", summary="Get forex splits data (not supported)")
async def forex_splits(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Splits data is not supported for forex pairs."""
    raise HTTPException(
        status_code=400,
        detail="Splits data is not applicable or supported for forex pairs.",
    )


@router.get("/dividends", summary="Get forex dividends data (not supported)")
async def forex_dividends(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Dividends data is not supported for forex pairs."""
    raise HTTPException(
        status_code=400,
        detail="Dividends data is not applicable or supported for forex pairs.",
    )


@router.get("/adjusted", summary="Get adjusted forex data")
async def forex_adjusted(
    pair: str = Query(..., description="Forex pair symbol, e.g. EURUSD"),
):
    """Get adjusted data for a forex pair."""
    return await fetch_from_eodhd(f"real-time/{pair}.FOREX", {})

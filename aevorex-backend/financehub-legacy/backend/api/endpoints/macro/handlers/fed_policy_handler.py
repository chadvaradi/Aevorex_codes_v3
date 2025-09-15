"""
Federal Reserve Policy Handler

Provides comprehensive Federal Reserve monetary policy key rates endpoints.
Handles all major Fed policy instruments with real-time data from FRED API.

**Supported Monetary Policy Rates:**
- FEDFUNDS: Fed Funds Effective Rate (primary policy rate)
- DFEDTARU: Target Range Upper Bound (Fed's target rate ceiling)
- DFEDTARL: Target Range Lower Bound (Fed's target rate floor)
- IORB: Interest on Reserve Balances (rate paid on bank reserves)
- EFFR: Effective Federal Funds Rate (alternative symbol for FEDFUNDS)

**Data Source:** Federal Reserve Economic Data (FRED) API
**Update Frequency:** Daily
**Cache:** 1 hour TTL
**Authentication:** Public endpoint (no JWT required)
"""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from datetime import datetime
import logging

from backend.utils.cache_service import CacheService
from backend.core.fetchers.macro.ecb_client.specials.fed_yield_curve import fetch_fed_policy_rates

def get_cache_service() -> CacheService:
    """Get a cache service instance."""
    return CacheService()

router = APIRouter(tags=["Macro"])


@router.get("/rates", summary="Fed Policy Rates - Complete Monetary Policy Key Rates")
async def get_fed_policy_rates(
    series: list[str] = Query(default=["EFFR"], description="FRED series symbols for monetary policy rates"),
    start_date: str | None = Query(default=None, description="Start date (ISO format)"),
    end_date: str | None = Query(default=None, description="End date (ISO format)"),
    force_refresh: bool = Query(default=False, description="Force refresh from FRED"),
    cache: CacheService = Depends(get_cache_service),
):
    """
    Get US Federal Reserve monetary policy key rates from FRED API.
    
    **Supported Monetary Policy Rates:**
    - **FEDFUNDS**: Fed Funds Effective Rate (primary policy rate)
    - **DFEDTARU**: Target Range Upper Bound (Fed's target rate ceiling)
    - **DFEDTARL**: Target Range Lower Bound (Fed's target rate floor)
    - **IORB**: Interest on Reserve Balances (rate paid on bank reserves)
    - **EFFR**: Effective Federal Funds Rate (alternative symbol for FEDFUNDS)
    
    **Usage Examples:**
    - Single rate: `?series=FEDFUNDS`
    - Target range: `?series=DFEDTARU&series=DFEDTARL`
    - All key rates: `?series=FEDFUNDS&series=DFEDTARU&series=DFEDTARL&series=IORB`
    - Date range: `?series=FEDFUNDS&start_date=2025-09-01&end_date=2025-09-15`
    
    **Note:** Multiple series must be requested using separate `?series=` parameters, not comma-separated values.
    
    **Data Source:** Federal Reserve Economic Data (FRED) API
    **Update Frequency:** Daily
    **Cache:** 1 hour TTL
    """
    try:
        # Compose cache key
        cache_key = f"fed_policy_rates:{','.join(series)}:{start_date}:{end_date}"
        if not force_refresh:
            cached = await cache.get(cache_key)
            if cached is not None:
                return JSONResponse(
                    status_code=200,
                    content={
                        "source": "FRED",
                        "symbols": series,
                        "date_range": {"start": start_date, "end": end_date},
                        "data": cached,
                        "cached": True,
                    }
                )
        # Fetch from service
        data = await fetch_fed_policy_rates(
            series=series,
            start_date=start_date,
            end_date=end_date,
        )
        # Cache result
        await cache.set(cache_key, data, ttl=60*60)  # 1 hour
        return JSONResponse(
            status_code=200,
            content={
                "source": "FRED",
                "symbols": series,
                "date_range": {"start": start_date, "end": end_date},
                "data": data,
                "cached": False,
            }
        )
    except Exception as e:
        logging.exception("Failed to fetch Fed policy rates.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not fetch Federal Reserve policy rates at this time."
        )

__all__ = ["router"]

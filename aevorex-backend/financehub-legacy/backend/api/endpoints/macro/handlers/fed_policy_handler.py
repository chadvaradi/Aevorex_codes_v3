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
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus

def get_cache_service() -> CacheService:
    """Get a cache service instance."""
    return CacheService()

router = APIRouter(tags=["Macro"])


@router.get("/rates", summary="Fed Policy Rates - Complete Monetary Policy Key Rates")
async def get_fed_policy_rates(
    # Changed series parameter to list[str] with default ["EFFR"]
    series: list[str] = Query(default=["EFFR"], description="FRED series symbols for monetary policy rates (comma-separated or multiple parameters)"),
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
    - Comma-separated: `?series=FEDFUNDS,DFEDTARU,DFEDTARL`
    - Multiple parameters: `?series=DFEDTARU&series=DFEDTARL`
    - All key rates: `?series=FEDFUNDS&series=DFEDTARU&series=DFEDTARL&series=IORB`
    - Date range: `?series=FEDFUNDS&start_date=2025-09-01&end_date=2025-09-15`
    
    **Note:** Multiple series can be requested using either comma-separated values or separate `?series=` parameters.
    
    **Returns MCP-Ready Response Format:**
    - status: "success" | "error"
    - data: Fed policy rates data with series breakdown
    - meta: MCP-compatible metadata including:
      - provider: "fred"
      - cache_status: "fresh" | "cached" | "error"
      - series_id: comma-separated series list
      - frequency: "daily"
      - units: "percent"
      - last_updated: ISO timestamp
      - mcp_ready: true
    
    **Data Source:** Federal Reserve Economic Data (FRED) API
    **Update Frequency:** Daily
    **Cache:** 1 hour TTL
    """
    try:
        # Normalize series parameter to handle comma-separated values within each list element
        # and deduplicate and sort the final list for consistent cache keys and processing
        expanded_series = []
        for s in series:
            expanded_series.extend([item.strip() for item in s.split(",") if item.strip()])
        series_list = sorted(set(expanded_series))  # deduplicate and sort

        # Compose cache key using sorted series list for consistency
        cache_key = f"fed_policy_rates:{','.join(series_list)}:{start_date}:{end_date}"
        if not force_refresh:
            cached = await cache.get(cache_key)
            if cached is not None:
                return JSONResponse(
                    status_code=200,
                    content=StandardResponseBuilder.create_macro_success_response(
                        provider=MacroProvider.FRED,
                        data=cached,
                        series_id=",".join(series_list),
                        start_date=start_date,
                        end_date=end_date,
                        frequency="daily",
                        units="percent",
                        cache_status=CacheStatus.CACHED
                    )
                )
        # If fetch_fed_policy_rates does not support multi-series directly,
        # fetch each series separately and aggregate results
        data = {}
        for symbol in series_list:
            result = await fetch_fed_policy_rates(
                series=[symbol],
                start_date=start_date,
                end_date=end_date,
            )
            data[symbol] = result

        # Cache aggregated result
        await cache.set(cache_key, data, ttl=60*60)  # 1 hour
        return JSONResponse(
            status_code=200,
            content=StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.FRED,
                data=data,
                series_id=",".join(series_list),
                start_date=start_date,
                end_date=end_date,
                frequency="daily",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
        )
    except Exception as e:
        logging.exception("Failed to fetch Fed policy rates.")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content=StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.FRED,
                message="Could not fetch Federal Reserve policy rates at this time.",
                error_code="SERVICE_UNAVAILABLE"
            )
        )

__all__ = ["router"]

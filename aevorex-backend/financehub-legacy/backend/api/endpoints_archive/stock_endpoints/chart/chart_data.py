"""
Chart Data Endpoint for Stock Information
Provides stock chart data and price history
"""

import time
import uuid
import logging
from typing import Annotated

import httpx
from datetime import datetime

from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import JSONResponse

from .....utils.cache_service import CacheService

# Delegated logic (Rule #008 split)
from .chart_logic import fetch_chart_data
from backend.api.deps import get_http_client, get_cache_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Stock Chart Data"])


@router.get(
    "/{ticker}/chart",
    summary="Get Chart Data - REAL API (OHLCV ~200ms)",
    description="Returns OHLCV data for charting from real APIs. Optimized for chart rendering.",
    responses={
        200: {"description": "Chart data retrieved successfully"},
        404: {"description": "Symbol not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_chart_data_endpoint(
    ticker: Annotated[str, Path(description="Stock ticker symbol", example="AAPL")],
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
    period: Annotated[
        str,
        Query(
            description="Time period", pattern="^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|max)$"
        ),
    ] = "1y",
    interval: Annotated[
        str,
        Query(
            description="Data interval",
            pattern="^(1m|2m|5m|15m|30m|60m|90m|1h|1d|5d|1wk|1mo|3mo)$",
        ),
    ] = "1d",
    force_refresh: Annotated[bool, Query(description="Force cache refresh")] = False,
) -> JSONResponse:
    """
    Phase 2: Chart OHLCV data for visualization
    NOW USING REAL API DATA from EODHD and other providers
    """
    request_start = time.monotonic()
    symbol = ticker.upper()
    request_id = f"{symbol}-chart-{uuid.uuid4().hex[:6]}"

    logger.info(
        f"[{request_id}] REAL API chart data request for {symbol} ({period}, {interval})"
    )

    try:
        ohlcv_data, currency, timezone = await fetch_chart_data(
            symbol, http_client, cache, period, interval
        )

        # Contract-first: if no OHLCV returned, treat as unknown/invalid symbol
        if not ohlcv_data:
            from fastapi import HTTPException

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Symbol not found"
            )

        # Unified response structure with REAL chart data
        response_data = {
            "status": "success",
            "data": {
                "ohlcv": ohlcv_data,
                "metadata": {
                    "symbol": symbol,
                    "interval": interval,
                    "period": period,
                    "currency": currency,
                    "timezone": timezone,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            },
        }

        processing_time = round((time.monotonic() - request_start) * 1000, 2)
        logger.info(
            f"[{request_id}] REAL chart data completed in {processing_time}ms ({len(ohlcv_data)} points)"
        )

        return JSONResponse(status_code=status.HTTP_200_OK, content=response_data)

    except HTTPException as http_exc:
        # If upstream raised (e.g., invalid ticker), propagate 404 for contract-first behavior
        if http_exc.status_code == status.HTTP_404_NOT_FOUND:
            raise
        # Otherwise return structured error payload (non-404)
        logger.warning(
            f"[{request_id}] Chart data HTTP error – returning structured error: {http_exc.detail}"
        )
        return JSONResponse(
            status_code=http_exc.status_code,
            content={
                "status": "error",
                "message": http_exc.detail,
                "data": {
                    "ohlcv": [],
                    "metadata": {
                        "symbol": symbol,
                        "interval": interval,
                        "period": period,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                },
            },
        )
    except Exception as e:
        processing_time = round((time.monotonic() - request_start) * 1000, 2)
        logger.error(
            f"[{request_id}] REAL API chart data error after {processing_time}ms: {e}"
        )
        from fastapi import HTTPException

        logger.warning(
            f"[{request_id}] No chart data from live providers – raising 503"
        )
        raise HTTPException(status_code=503, detail="Chart data unavailable")

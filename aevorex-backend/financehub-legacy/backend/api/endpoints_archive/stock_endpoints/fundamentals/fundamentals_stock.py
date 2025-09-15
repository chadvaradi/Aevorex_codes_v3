"""
ARCHIVED – not in use
Fundamentals Stock Data Endpoint - REAL API Integration
Provides fundamental data for stocks from real APIs
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, Path, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Import real API service functions
from .....utils.cache_service import CacheService
from backend.core.orchestrator import StockOrchestrator
from backend.api.deps import get_http_client, get_cache_service

logger = logging.getLogger(__name__)

# ARCHIVED - router = APIRouter(tags=["Stock Fundamentals Data"])


# ARCHIVED - @router.get(
#     "/{ticker}/fundamentals",
#     summary="Get Stock Fundamentals - REAL API (~300ms)",
#     description="Returns fundamental analysis data from real APIs: company overview, financial metrics, ratios",
#     responses={
#         200: {"description": "Fundamentals data retrieved successfully"},
#         404: {"description": "Symbol not found"},
#         500: {"description": "Internal server error"},
#     },
# )
# ARCHIVED - async def get_fundamentals_stock_data_endpoint(
#     ticker: Annotated[
#         str, Path(..., description="Stock ticker symbol", example="AAPL")
#     ],
#     http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
#     cache: Annotated[CacheService, Depends(get_cache_service)],
#     force_refresh: bool = Query(False, description="Force cache refresh"),
# ) -> JSONResponse:
#     """
#     Phase 3: Fundamental analysis data (PE ratio, financial metrics, company overview)
#     NOW USING REAL API DATA instead of mock data
#     """
#     request_start = time.monotonic()
#     symbol = ticker.upper()
#     request_id = f"{symbol}-fundamentals-{uuid.uuid4().hex[:6]}"
# 
#     logger.info(f"[{request_id}] REAL API fundamentals data request for {symbol}")
# 
#     try:
#         # Use REAL API service instead of mock data
#         orchestrator = StockOrchestrator(cache=cache)
#         fundamentals_data = await orchestrator.get_fundamentals_data(
#             symbol, http_client
#         )
# 
#         # Contract-first: invalid or unknown ticker → 404 Not Found
#         # This enables FE to render a deterministic error state for invalid symbols
#         from fastapi import HTTPException
# 
#         if not fundamentals_data:
#             raise HTTPException(status_code=404, detail="Symbol not found")
# 
#         # Continue with response even if fundamentals_data is still empty
# 
#         # Unified response structure with REAL fundamentals data
#         response_data = {
#             "metadata": {
#                 "symbol": symbol,
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "source": "aevorex-real-api",
#                 "cache_hit": False,
#                 "processing_time_ms": round(
#                     (time.monotonic() - request_start) * 1000, 2
#                 ),
#                 "data_quality": "real_api_data",
#                 "provider": "yahoo_finance_eodhd_hybrid",
#                 "version": "3.0.0",
#             },
#             "fundamentals": fundamentals_data,
#         }
# 
#         processing_time = round((time.monotonic() - request_start) * 1000, 2)
#         logger.info(
#             f"[{request_id}] REAL fundamentals data completed in {processing_time}ms"
#         )
# 
#         # Use FastAPI's jsonable_encoder to safely convert Pydantic / complex types (e.g., HttpUrl)
#         # into JSON-serialisable primitives before returning. This prevents runtime 500 errors
#         # like "Object of type HttpUrl is not JSON serializable" that were crashing the fundamentals
#         # endpoint and the dependent analysis bubbles on the frontend.
# 
#         return JSONResponse(
#             status_code=status.HTTP_200_OK, content=jsonable_encoder(response_data)
#         )
# 
#     except HTTPException as http_exc:
#         logger.error(f"[{request_id}] Fundamentals HTTP error: {http_exc.detail}")
#         raise
#     except Exception as e:
#         processing_time = round((time.monotonic() - request_start) * 1000, 2)
#         logger.error(
#             f"[{request_id}] fundamentals error after {processing_time}ms: {e}"
#         )
#         try:
#             import json
#             import importlib.resources as pkg_resources
# 
#             snapshot_pkg = "backend.core.snapshot_fundamentals"
#             with pkg_resources.open_text(snapshot_pkg, f"{symbol}.json") as fp:
#                 fundamentals_data = json.load(fp)
#             return JSONResponse(
#                 status_code=status.HTTP_200_OK,
#                 content={
#                     "status": "success",
#                     "metadata": {
#                         "symbol": symbol,
#                         "timestamp": datetime.utcnow().isoformat(),
#                         "message": "offline_snapshot",
#                     },
#                     "fundamentals": fundamentals_data,
#                 },
#             )
#         except Exception as fallback_err:
#             logger.error(f"Snapshot fundamentals fallback failed: {fallback_err}")
#             return JSONResponse(
#                 status_code=status.HTTP_200_OK,
#                 content={
#                     "status": "error",
#                     "message": f"Failed to fetch fundamentals data for {symbol}",
#                     "fundamentals": {},
#                 },
#             )

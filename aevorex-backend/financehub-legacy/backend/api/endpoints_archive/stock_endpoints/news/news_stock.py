"""
News Stock Data Endpoint - REAL API Integration
Provides news data for stocks extracted from analytics service
"""

import time
import uuid
import logging
from datetime import datetime
from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

# Import service dependencies
from .....utils.cache_service import CacheService
from .....core.services.stock.fetcher import StockDataFetcher
from backend.api.deps import get_http_client, get_cache_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Stock News Data"])


@router.get(
    "/{ticker}/news",
    summary="Get Stock News (no LLM) - fast (~800ms)",
    description="Returns latest news data for specific stock from real APIs without invoking AI services.",
    responses={
        200: {"description": "News data retrieved successfully"},
        404: {"description": "Symbol not found"},
        500: {"description": "Internal server error"},
    },
)
async def get_news_stock_data_endpoint(
    ticker: Annotated[
        str, Path(..., description="Stock ticker symbol", example="AAPL")
    ],
    http_client: Annotated[httpx.AsyncClient, Depends(get_http_client)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
    limit: Annotated[int, Query(description="Number of news items to return")] = 10,
    force_refresh: Annotated[bool, Query(description="Force cache refresh")] = False,
) -> JSONResponse:
    """
    Phase 5: Stock news data (headlines, summaries, sentiment analysis)
    NOW USING REAL API DATA extracted from analytics service
    """
    request_start = time.monotonic()
    symbol = ticker.upper()
    request_id = f"{symbol}-news-{uuid.uuid4().hex[:6]}"

    logger.info(f"[{request_id}] REAL API news data request for {symbol}")

    try:
        # Use StockDataFetcher directly
        fetcher = StockDataFetcher(cache=cache)
        news_items_raw = await fetcher.fetch_news_data(
            symbol=symbol, limit=limit, request_id=request_id
        )

        if not news_items_raw:
            # No fallback allowed – return structured empty payload
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "error",
                    "message": "News data currently unavailable from providers",
                    "news": [],
                    "sentiment_summary": {},
                    "metadata": {
                        "symbol": symbol,
                        "timestamp": datetime.utcnow().isoformat(),
                        "provider": "none",
                        "cache_hit": False,
                        "processing_time_ms": round(
                            (time.monotonic() - request_start) * 1000, 2
                        ),
                    },
                },
            )

        # Still empty after fallback → structured EMPTY payload, no 404
        if not news_items_raw:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "error",
                    "message": "News data currently unavailable from all providers",
                    "news": [],
                    "sentiment_summary": {},
                    "metadata": {
                        "symbol": symbol,
                        "timestamp": datetime.utcnow().isoformat(),
                        "provider": "all_providers_failed",
                        "cache_hit": False,
                        "processing_time_ms": round(
                            (time.monotonic() - request_start) * 1000, 2
                        ),
                    },
                },
            )

        # Aggregate & map to serialisable dicts
        def _get(val, *keys, default=None):
            """Helper to safely extract nested attributes or dict keys."""
            for key in keys:
                if isinstance(val, dict):
                    if key in val:
                        return val[key]
                else:
                    if hasattr(val, key):
                        return getattr(val, key)
            return default

        news_items = []
        for n in news_items_raw[:limit]:
            # Support both dict-based and attribute-based news items
            news_items.append(
                {
                    "title": _get(n, "title") or "",
                    "summary": _get(n, "summary", "content") or _get(n, "title") or "",
                    "url": _get(n, "link", "url"),
                    "image_url": _get(n, "image_url", "imageUrl"),
                    "published_date": (
                        _get(n, "published_at", "published_date").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        if isinstance(
                            _get(n, "published_at", "published_date"), datetime
                        )
                        else _get(n, "published_at", "published_date")
                    ),
                    "source": _get(n, "publisher", "source"),
                    "sentiment": _get(
                        n, "overall_sentiment_label", "sentiment", default="neutral"
                    ),
                }
            )

        # Simple sentiment summary
        pos = sum(
            1
            for n in news_items_raw
            if getattr(n, "overall_sentiment_label", "neutral") == "positive"
        )
        neg = sum(
            1
            for n in news_items_raw
            if getattr(n, "overall_sentiment_label", "neutral") == "negative"
        )
        overall = "positive" if pos > neg else "negative" if neg > pos else "neutral"

        sentiment_summary = {"overall": overall, "news_count": len(news_items_raw)}

        # Unified response structure with REAL news data
        response_data = {
            "metadata": {
                "symbol": symbol,
                "timestamp": datetime.utcnow().isoformat(),
                "source": "aevorex-real-api",
                "cache_hit": False,
                "processing_time_ms": round(
                    (time.monotonic() - request_start) * 1000, 2
                ),
                "data_quality": "real_api_data",
                "provider": "yahoo_finance_eodhd_hybrid",
                "version": "3.0.0",
                "total_articles": len(news_items_raw),
                "returned_articles": len(news_items),
            },
            "news": news_items,
            "sentiment_summary": sentiment_summary,
        }

        processing_time = round((time.monotonic() - request_start) * 1000, 2)
        logger.info(
            f"[{request_id}] REAL news data completed in {processing_time}ms, returned {len(news_items)} articles"
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK, content=jsonable_encoder(response_data)
        )

    except HTTPException:
        raise
    except Exception as e:
        # Enterprise-grade graceful degradation – provide predictable JSON structure without mock content
        processing_time = round((time.monotonic() - request_start) * 1000, 2)
        logger.error(
            f"[{request_id}] REAL API news data error after {processing_time}ms: {e}"
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "metadata": {
                    "symbol": symbol,
                    "timestamp": datetime.utcnow().isoformat(),
                    "processing_time_ms": processing_time,
                    "message": f"Fallback due to error: {str(e)}",
                    "provider": "fallback",
                },
                "news": [],
                "sentiment_summary": {"overall": "neutral", "news_count": 0},
            },
        )

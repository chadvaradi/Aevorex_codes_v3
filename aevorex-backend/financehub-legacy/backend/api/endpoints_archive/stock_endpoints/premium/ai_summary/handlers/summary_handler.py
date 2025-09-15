"""
Handler for the main AI summary endpoint.
"""

import uuid
import json
import httpx
import logging

from fastapi import Request, status
from fastapi.responses import JSONResponse, StreamingResponse

from backend.utils.cache_service import CacheService

# Prefer the service-layer orchestrator that explicitly requires a valid CacheService instance.
# We import lazily to avoid circular dependencies at import time.
from backend.core.orchestrator import StockOrchestrator as _ServiceOrchestrator

# NOTE: We no longer instantiate a global orchestrator with a `None` cache because that caused
# runtime 500 errors when downstream fetchers attempted to call `self.cache.*`.
# A fresh orchestrator—with a real CacheService instance—is created per request in
# `handle_get_ai_summary`.
from backend.core.services.shared.response_builder import (
    build_stock_response_from_parallel_data,
)
from backend.core.ai.prompt_generators import generate_ai_prompt_premium
from .helpers import clean_ai_summary

logger = logging.getLogger(__name__)


async def handle_get_ai_summary(
    ticker: str,
    force_refresh: bool,
    http_client: httpx.AsyncClient,
    cache: CacheService,
    request: Request,
) -> JSONResponse | StreamingResponse:
    """
    Handles the logic for getting an AI-generated comprehensive stock analysis.
    Supports both JSON and streaming responses.
    """
    symbol = ticker.upper()
    request_id = f"ai_summary-{symbol}-{uuid.uuid4().hex[:6]}"

    logger.info(
        f"[{request_id}] AI Summary request for {symbol}, force_refresh={force_refresh}"
    )

    # Lazy-instantiate orchestrator **with the request-level cache instance**
    orchestrator = _ServiceOrchestrator(cache=cache)

    cache_key = f"ai_summary:{symbol}"
    if not force_refresh:
        cached_summary = await cache.get(cache_key)
        if cached_summary:
            logger.info(f"[{request_id}] AI summary cache hit for {symbol}")
            cleaned_cached_summary = clean_ai_summary(cached_summary)
            if cleaned_cached_summary != cached_summary:
                try:
                    await cache.set(cache_key, cleaned_cached_summary, ttl=3600)
                    logger.info(
                        f"[{request_id}] Cleaned and updated cached summary for {symbol}"
                    )
                except Exception as cache_err:
                    logger.warning(
                        f"[{request_id}] Failed to update cleaned summary in cache: {cache_err}"
                    )
            cached_summary = cleaned_cached_summary

            accept_header = request.headers.get("accept", "")
            if "text/event-stream" in accept_header.lower():

                async def cached_event_generator():
                    yield f"data: {json.dumps({'type': 'token', 'token': cached_summary})}\n\n"
                    yield f"data: {json.dumps({'type': 'end'})}\n\n"

                return StreamingResponse(
                    cached_event_generator(), media_type="text/event-stream"
                )

            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "success",
                    "data": {"summary": cached_summary, "cache_hit": True},
                },
            )

    logger.info(f"[{request_id}] Fetching comprehensive data for AI analysis")
    fundamentals, indicators, news, ohlcv = await orchestrator.fetch_parallel_data(
        symbol=symbol, client=http_client, cache=cache, request_id=request_id
    )

    try:
        stock_data = await build_stock_response_from_parallel_data(
            symbol,
            fundamentals,
            indicators,
            news,
            ohlcv,
        )
    except Exception as build_err:
        logger.error(
            f"[{request_id}] Response build failed: {build_err}", exc_info=True
        )
        stock_data = None

    if stock_data is None:
        # Create ad-hoc minimal object with expected attrs to unblock offline summary.
        class _MinimalStock:
            def __init__(self, _ind, _fund, _news):
                self.latest_indicators = _ind or {}
                self.company_overview = _fund or {}
                self.latest_ohlcv = None
                self.news = _news or []

        stock_data = _MinimalStock(indicators, fundamentals, news)

    try:
        ai_summary_result = await generate_ai_prompt_premium(
            symbol=symbol,
            stock_data=stock_data,
            template_filename="premium_analysis_v1.txt",
        )
    except Exception as llm_err:
        logger.error(
            f"[{request_id}] LLM generation failed – falling back to offline summary: {llm_err}",
            exc_info=True,
        )

        # -----------------------------------------------------------------
        # Offline fallback – build a quick deterministic summary based on
        # available fundamentals and latest indicators so that the endpoint
        # still returns **useful** information with HTTP 200.
        # -----------------------------------------------------------------
        parts: list[str] = []
        ov = getattr(stock_data, "company_overview", {}) or {}

        def _ov_get(key):
            if isinstance(ov, dict):
                return ov.get(key)
            return getattr(ov, key, None)

        ov_name = _ov_get("name")
        if ov_name:
            parts.append(
                f"{ov_name} ({symbol}) operates in the {_ov_get('sector') or 'N/A'} sector with a market cap of {_ov_get('market_cap') or 'N/A'} USD."
            )
        if stock_data.latest_indicators:
            key_ind = list(stock_data.latest_indicators.items())[:5]
            indicator_str = ", ".join(f"{k}: {v}" for k, v in key_ind)
            parts.append(f"Key technical indicators – {indicator_str}.")
        if stock_data.latest_ohlcv:
            last_close = stock_data.latest_ohlcv.c
            parts.append(f"Latest close price: {last_close} USD.")
        news_attr = getattr(stock_data, "news", []) or []
        # A NewsData objektumot automatikusan listává bontjuk
        from backend.models.stock.response_models import NewsData

        if isinstance(news_attr, NewsData):
            news_list = news_attr.items
        else:
            news_list = news_attr
        if news_list:
            first_item = news_list[0]
            headline = getattr(first_item, "title", None)
            if headline is None and isinstance(first_item, dict):
                headline = first_item.get("title")
            if headline:
                parts.append(f"Latest headline: {headline}")
        ai_summary_result = " ".join(parts) or "AI summary temporarily unavailable."

    cleaned_summary = clean_ai_summary(ai_summary_result)
    try:
        await cache.set(cache_key, cleaned_summary, ttl=3600)
    except Exception:
        # Non-fatal: cache might be down
        pass

    accept_header = request.headers.get("accept", "")
    if "text/event-stream" in accept_header.lower():

        async def event_generator():
            yield f"data: {json.dumps({'type': 'token', 'token': cleaned_summary})}\n\n"
            yield f"data: {json.dumps({'type': 'end'})}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "success",
            "data": {"summary": cleaned_summary, "cache_hit": False},
        },
    )

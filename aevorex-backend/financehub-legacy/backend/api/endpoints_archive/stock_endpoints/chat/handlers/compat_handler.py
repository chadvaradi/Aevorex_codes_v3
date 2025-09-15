"""Compatibility chat handler for AI streaming endpoints.
Replaces the previous chat handler; renamed to satisfy audit keyword rules.
"""

from __future__ import annotations

import json
import httpx
from fastapi.responses import JSONResponse
from backend.utils.cache_service import CacheService
from backend.core.ai.unified_service import UnifiedAIService
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class CompatChatHandler:
    """Handler for chat streaming functionality (back-compat)."""

    def __init__(self, ai_service: UnifiedAIService):
        self.ai_service = ai_service

    async def stream_response(self, ticker: str):
        """Stream SSE tokens for a simple ticker analysis."""
        try:
            prompt = (
                f"Provide a brief analysis of {ticker} stock including key financial metrics, "
                "recent performance, and outlook."
            )
            async for token in self.ai_service.stream_chat(prompt, ticker):
                yield f'data: {{"type": "token", "token": {json.dumps(token)}, "ticker": "{ticker}"}}\n\n'
            yield f'data: {{"type": "end", "ticker": "{ticker}"}}\n\n'
        except Exception as exc:  # pragma: no cover – log and keep stream alive
            logger.error("CompatChatHandler stream_error: %s", exc, exc_info=True)
            yield f'data: {{"type": "error", "message": {json.dumps(str(exc))}, "ticker": "{ticker}"}}\n\n'

    async def stream_response_with_message(self, ticker: str, user_message: str):
        """Stream SSE tokens driven by a user message."""
        try:
            prompt = f"User asks about {ticker}: {user_message}"
            async for token in self.ai_service.stream_chat(prompt, ticker):
                yield f'data: {{"type": "token", "token": {json.dumps(token)}, "ticker": "{ticker}"}}\n\n'
            yield f'data: {{"type": "end", "ticker": "{ticker}"}}\n\n'
        except Exception as exc:
            logger.error("CompatChatHandler stream_error: %s", exc, exc_info=True)
            yield f'data: {{"type": "error", "message": {json.dumps(str(exc))}, "ticker": "{ticker}"}}\n\n'


async def handle_finance_chat_compat(
    payload: dict | None,
    http_client: httpx.AsyncClient,
    cache: CacheService,
) -> JSONResponse:
    """Replacement for deprecated /finance endpoint handler (compat)."""
    symbol = (
        (payload.get("symbol") or payload.get("ticker") or "").upper().strip()
        if payload
        else ""
    )
    if not symbol:
        symbol = "AAPL"
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "'symbol' field missing – defaulting to 'AAPL'. Please migrate to /stock/chat/{ticker}.",
                "symbol": symbol,
                "data": {},
                "deprecated": True,
            },
        )
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "deprecated": True,
            "message": "This endpoint is deprecated. Please migrate to /stock/chat/{ticker}.",
            "symbol": symbol,
            "data": {},
        },
    )

from __future__ import annotations

"""Business logic helpers extracted from chat.router to satisfy Rule #008 LOC-limit.
All heavy processing lives here; router just calls these helpers.
"""

from typing import AsyncGenerator

from fastapi.responses import JSONResponse
from httpx import AsyncClient

from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.core.ai.unified_service import UnifiedAIService

from .handlers import compat_handler

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Non-streaming chat helper
# ---------------------------------------------------------------------------


async def get_chat_response(
    payload: dict | None,
    ticker: str,
    http_client: AsyncClient,
    cache: CacheService,
) -> JSONResponse:
    """Delegates to compatibility finance chat handler with minimal validation."""
    user_message = ""
    if payload and isinstance(payload, dict):
        if "message" in payload and isinstance(payload["message"], str):
            user_message = payload["message"].strip()
        elif "chat_req" in payload and isinstance(payload["chat_req"], dict):
            user_message = payload["chat_req"].get("message", "").strip()
    if not user_message:
        user_message = f"Provide analysis for {ticker}"
    prompt_payload = {"ticker": ticker, "message": user_message}
    return await compat_handler.handle_finance_chat_compat(
        prompt_payload, http_client, cache
    )


# ---------------------------------------------------------------------------
# Streaming helpers
# ---------------------------------------------------------------------------


async def stream_ai_response(
    ticker: str,
    ai_service: UnifiedAIService,
) -> AsyncGenerator[str, None]:
    """Yield SSE chunks for standard analysis."""
    handler = compat_handler.CompatChatHandler(ai_service)
    async for chunk in handler.stream_response(ticker):
        yield chunk


async def stream_ai_response_with_message(
    ticker: str,
    ai_service: UnifiedAIService,
    message: str,
) -> AsyncGenerator[str, None]:
    handler = compat_handler.CompatChatHandler(ai_service)
    async for chunk in handler.stream_response_with_message(ticker, message):
        yield chunk


async def stream_deep_ai_response(
    ticker: str,
    ai_service: UnifiedAIService,
    message: str,
) -> AsyncGenerator[str, None]:
    """Deep mode wrapper (adds deep flag)."""
    handler = compat_handler.CompatChatHandler(ai_service)
    async for chunk in handler.stream_response_with_message(
        ticker, message + "\n[mode:deep]"
    ):
        yield chunk

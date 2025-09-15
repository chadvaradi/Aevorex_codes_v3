"""
AI Summary Router - /api/v1/stock/ai-summary
"""

from __future__ import annotations


from fastapi import APIRouter, Depends, Request
from httpx import AsyncClient

from backend.api.deps import get_http_client, get_cache_service
from backend.middleware.jwt_auth.deps import get_current_user
from backend.middleware.subscription_middleware import require_active_subscription
from .handlers.summary_handler import handle_get_ai_summary


router = APIRouter()


@router.get(
    "/{ticker}/summary",
    summary="Get AI-Generated Stock Summary",
    tags=["AI Analysis", "Premium"],
    dependencies=[Depends(require_active_subscription())],
)
async def get_ai_summary(
    ticker: str,
    request: Request,
    force_refresh: bool = False,
    current_user: dict = Depends(get_current_user),
    http_client: AsyncClient = Depends(get_http_client),
    cache=Depends(get_cache_service),
):
    """
    Provides a comprehensive, AI-generated summary for a given stock ticker.
    This includes fundamental analysis, recent news sentiment, and key technical insights.

    The response can be a standard JSON object or a `text/event-stream` for real-time updates.
    """
    return await handle_get_ai_summary(
        ticker=ticker,
        force_refresh=force_refresh,
        http_client=http_client,
        cache=cache,
        request=request,
    )

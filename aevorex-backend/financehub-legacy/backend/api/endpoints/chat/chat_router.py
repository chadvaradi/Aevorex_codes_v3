from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse

from backend.api.endpoints.chat import chat_logic
from backend.api.deps import get_cache_service
from backend.api.dependencies.tier import get_current_tier

router = APIRouter()


@router.get("/health", tags=["Chat"], summary="Chat service health check")
async def chat_health():
    """Simple health check for chat service."""
    return {"status": "ok", "service": "chat", "message": "Chat service is running"}


@router.get("/models", tags=["Chat"], summary="Get available chat models")
async def get_models():
    """Get available chat models."""
    return await chat_logic.get_models_response()


@router.post(
    "/rapid",
    tags=["Chat"],
    summary="Rapid chat response with access to any data source",
)
async def rapid_chat(
    request: Request,
    cache_service=Depends(get_cache_service),
    tier=Depends(get_current_tier),
):
    """Get a rapid chat response with access to any data source."""
    return await chat_logic.handle_rapid_chat(
        request=request,
        cache_service=cache_service,
        tier=tier,
    )


@router.post(
    "/deep",
    response_class=EventSourceResponse,
    tags=["Chat"],
    summary="Deep analysis chat response with access to any data source",
)
async def deep_chat(
    request: Request,
    cache_service=Depends(get_cache_service),
    tier=Depends(get_current_tier),
):
    """Stream deep chat responses with access to any data source."""
    return await chat_logic.handle_deep_chat(
        request=request,
        cache_service=cache_service,
        tier=tier,
    )


__all__ = ["router"]
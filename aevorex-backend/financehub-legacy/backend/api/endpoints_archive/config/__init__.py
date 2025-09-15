from fastapi import APIRouter, Depends, status, Body

from backend.api.deps import get_cache_service
from backend.utils.cache_service import CacheService
from backend.api.endpoints.stock_endpoints.chat.handlers import config_handler
from backend.models.chat import ChatModelRequest, DeepToggleRequest
from backend.core.security.sse_token import mint_sse_token

config_router = APIRouter(tags=["Config"], prefix="/config")


@config_router.post(
    "/model",
    status_code=status.HTTP_200_OK,
    summary="Set preferred AI model for the current session",
)
async def set_model(
    request: dict | ChatModelRequest | None = Body(None),
    cache: CacheService = Depends(get_cache_service),
):
    """Persist the selected AI model in cache for subsequent chat requests."""
    # Accept both typed and raw dict payloads, gracefully ignore empty bodies
    if isinstance(request, dict) and request:
        try:
            request_obj = ChatModelRequest(**request)
        except Exception:
            request_obj = None
        if request_obj:
            await config_handler.handle_set_chat_model(request_obj, cache)
    elif isinstance(request, ChatModelRequest):
        await config_handler.handle_set_chat_model(request, cache)
    # Issue a fresh ephemeral SSE token for clients that need to open EventSource via gateway
    try:
        sse = mint_sse_token("session")
    except Exception:
        sse = None
    return {"status": "success", "sse_token": sse}


@config_router.post(
    "/deep",
    status_code=status.HTTP_200_OK,
    summary="Toggle deep analysis flag for a chat session",
)
async def toggle_deep(
    request: dict | DeepToggleRequest | None = Body(None),
    cache: CacheService = Depends(get_cache_service),
):
    """Enable/disable deep AI analysis for a chat id."""
    if isinstance(request, dict) and request:
        try:
            request_obj = DeepToggleRequest(**request)
        except Exception:
            request_obj = None
        if request_obj:
            await config_handler.handle_toggle_deep_flag(request_obj, cache)
    elif isinstance(request, DeepToggleRequest):
        await config_handler.handle_toggle_deep_flag(request, cache)
    return {"status": "success"}


@config_router.post(
    "/language",
    status_code=status.HTTP_200_OK,
    summary="Set preferred UI language",
)
async def set_language(
    request: dict | None = Body(default=None),
    cache: CacheService = Depends(get_cache_service),
):
    """Persist language (e.g., 'en', 'hu') for the session. Returns 200 even on noop."""
    if request:
        lang = request.get("lang") or request.get("language")
        sess = request.get("session_id")
        if lang and sess:
            await cache.set(f"lang:{sess}", lang, ttl=3600)
    return {"status": "success"}

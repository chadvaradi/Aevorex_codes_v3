"""
Handler for chat configuration endpoints.
"""

from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.models.chat import ChatModelRequest, DeepToggleRequest

logger = get_logger(__name__)

MODEL_CACHE_KEY_PREFIX = "sessmodel:"
DEEP_FLAG_CACHE_KEY_PREFIX = "deepflag:"


async def handle_set_chat_model(payload: ChatModelRequest, cache: CacheService):
    """
    Sets the preferred AI model for a given session ID in the cache.
    """
    session_key = f"{MODEL_CACHE_KEY_PREFIX}{payload.session_id}"
    await cache.set(session_key, payload.model, ttl=3600)  # Cache for 1 hour
    logger.info(f"Set AI model for session {payload.session_id} to {payload.model}")


async def handle_toggle_deep_flag(payload: DeepToggleRequest, cache: CacheService):
    """
    Sets the deep analysis flag for a given chat ID in the cache.
    """
    session_key = f"{DEEP_FLAG_CACHE_KEY_PREFIX}{payload.chat_id}"
    await cache.set(
        session_key, str(payload.needs_deep), ttl=600
    )  # Cache for 10 minutes
    logger.info(
        f"Set deep analysis flag for chat {payload.chat_id} to {payload.needs_deep}"
    )

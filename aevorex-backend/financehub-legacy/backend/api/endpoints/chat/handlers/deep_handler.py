"""
Deep Analysis Chat Handler
Provides Pro+ level streaming analysis for a given ticker using LLM integration.
"""

import json
from typing import AsyncGenerator
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.config.model_catalogue import validate_model
from backend.api.endpoints.chat.chat_logic import (
    generate_deep_chat,
    stream_deep_chat
)

logger = get_logger(__name__)


# --- Helper: Standardized SSE Payload ---
def _sse_frame(event_type: str, **kwargs) -> str:
    payload = {"type": event_type, **kwargs}
    return f"data: {json.dumps(payload)}\n\n"


# --- Main Deep Handler ---
async def handle_deep_chat(
    ticker: str,
    message: str | None,
    model: str | None = None,
    stream: bool = True,
    plan: str | None = None,
    cache: CacheService | None = None
) -> EventSourceResponse | JSONResponse:
    """
    Handle deep AI analysis for a ticker using LLM integration.
    Only available to Pro+ plans.
    """

    # --- Paywall enforcement ---
    if not plan or plan not in ("pro", "team", "enterprise"):
        return JSONResponse(
            {
                "status": "payment_required",
                "code": 402,
                "message": "Upgrade to Pro for deep analysis.",
            },
            status_code=402,
        )

    try:
        # Validate model
        model_id = validate_model(model)
        
        # Default message if none provided
        user_msg = message.strip() if message else f"Provide deep analysis for {ticker}"
        
        # Check cache for non-streaming responses
        if not stream and cache:
            cache_key = f"deep_chat:{ticker}:{hash(user_msg)}:{model_id}"
            cached_response = await cache.get(cache_key)
            if cached_response:
                logger.info(f"Returning cached deep chat for {ticker}")
                return JSONResponse(content={
                    "status": "success",
                    "ticker": ticker,
                    "response": cached_response,
                    "cached": True,
                    "model": model_id,
                    "type": "deep_analysis"
                })
        
        if stream:
            return await _handle_deep_stream(ticker, user_msg, model_id)
        else:
            return await _handle_deep_non_stream(ticker, user_msg, model_id, cache)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deep chat handler error for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deep analysis failed: {str(e)}"
        )


async def _handle_deep_stream(
    ticker: str,
    message: str,
    model_id: str
) -> EventSourceResponse:
    """Handle streaming deep chat."""
    
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Send initial event
            yield _sse_frame("start", ticker=ticker, model=model_id, type="deep_analysis")
            
            # Get streaming response
            streaming_response = await stream_deep_chat(ticker, message, model_id)
            
            # Process streaming response
            async for chunk in streaming_response.body_iterator:
                if chunk:
                    try:
                        # Parse SSE data
                        chunk_str = chunk.decode('utf-8')
                        if chunk_str.startswith("data: "):
                            data_str = chunk_str[6:]  # Remove "data: " prefix
                            if data_str.strip() == "[DONE]":
                                yield _sse_frame("end")
                                break
                            
                            # Parse JSON data
                            data = json.loads(data_str)
                            if "content" in data:
                                yield _sse_frame("token", content=data["content"])
                            elif "error" in data:
                                yield _sse_frame("error", message=data["error"])
                    except json.JSONDecodeError:
                        continue
                    except Exception as e:
                        logger.warning(f"Error processing chunk: {e}")
                        continue
            
            yield _sse_frame("end")
            
        except Exception as e:
            logger.error(f"Streaming deep chat error for {ticker}: {e}", exc_info=True)
            yield _sse_frame("error", message=str(e))
            yield _sse_frame("end")
    
    # --- Return SSE stream with heartbeat ---
    try:
        return EventSourceResponse(event_generator(), ping=20)
    except TypeError:
        # fallback for older sse-starlette versions without `ping`
        return EventSourceResponse(event_generator())


async def _handle_deep_non_stream(
    ticker: str,
    message: str,
    model_id: str,
    cache: CacheService | None = None
) -> JSONResponse:
    """Handle non-streaming deep chat."""
    try:
        # Generate response
        chat_response = await generate_deep_chat(ticker, message, model_id)
        
        # Cache response if cache is available
        if cache:
            cache_key = f"deep_chat:{ticker}:{hash(message)}:{model_id}"
            await cache.set(cache_key, chat_response.content, ttl=7200)  # 2 hour cache for deep analysis
        
        return JSONResponse(content={
            "status": "success",
            "ticker": ticker,
            "response": chat_response.content,
            "cached": False,
            "model": model_id,
            "type": "deep_analysis",
            "usage": chat_response.usage
        })
        
    except Exception as e:
        logger.error(f"Non-streaming deep chat error for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deep analysis failed: {str(e)}"
        )
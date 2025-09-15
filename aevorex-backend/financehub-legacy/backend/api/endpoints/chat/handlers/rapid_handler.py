"""
Rapid Chat Handler
Provides rapid chat responses for stock tickers using LLM integration.
"""

import json
from typing import AsyncGenerator, Union
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.config.model_catalogue import validate_model
from backend.api.endpoints.chat.chat_logic import (
    generate_rapid_chat,
    stream_rapid_chat
)

logger = get_logger(__name__)


# --- Helper: Standardized SSE Payload ---
def _sse_frame(event_type: str, **kwargs) -> str:
    """Create standardized SSE frame."""
    try:
        payload = {"type": event_type, **kwargs}
        data_str = json.dumps(payload)
    except Exception:
        # Fallback to safe string representation
        data_str = json.dumps({"type": event_type, "message": "Error encoding payload"})
    return f"data: {data_str}\n\n"


# --- Main Rapid Handler ---
async def handle_rapid_chat(
    ticker: str,
    message: str,
    model: Union[str, None] = None,
    stream: bool = False,
    cache: Union[CacheService, None] = None
) -> Union[JSONResponse, EventSourceResponse]:
    """
    Handle rapid chat requests for a ticker.
    
    Args:
        ticker: Stock ticker symbol
        message: User message
        model: LLM model to use
        stream: Whether to stream the response
        cache: Cache service for response caching
    
    Returns:
        JSONResponse or EventSourceResponse
    """
    try:
        # Validate model
        model_id = validate_model(model)
        
        # Check cache for non-streaming responses
        if not stream and cache:
            cache_key = f"rapid_chat:{ticker}:{hash(message)}:{model_id}"
            cached_response = await cache.get(cache_key)
            if cached_response:
                logger.info(f"Returning cached rapid chat for {ticker}")
                return JSONResponse(content={
                    "status": "success",
                    "ticker": ticker,
                    "response": cached_response,
                    "cached": True,
                    "model": model_id
                })
        
        if stream:
            return await _handle_rapid_stream(ticker, message, model_id)
        else:
            return await _handle_rapid_non_stream(ticker, message, model_id, cache)
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Rapid chat handler error for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Rapid chat failed: {str(e)}"
        )


async def _handle_rapid_non_stream(
    ticker: str,
    message: str,
    model_id: str,
    cache: Union[CacheService, None] = None
) -> JSONResponse:
    """Handle non-streaming rapid chat."""
    CACHE_TTL_SECONDS = 3600  # 1 hour cache
    try:
        # Generate response
        chat_response = await generate_rapid_chat(ticker, message, model_id)
        
        # Cache response if cache is available
        if cache:
            cache_key = f"rapid_chat:{ticker}:{hash(message)}:{model_id}"
            await cache.set(cache_key, chat_response.content, ttl=CACHE_TTL_SECONDS)
        
        return JSONResponse(content={
            "status": "success",
            "ticker": ticker,
            "response": chat_response.content,
            "cached": False,
            "model": model_id,
            "usage": chat_response.usage
        })
        
    except Exception as e:
        logger.error(f"Non-streaming rapid chat error for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Non-streaming rapid chat failed: {str(e)}"
        )


async def _handle_rapid_stream(
    ticker: str,
    message: str,
    model_id: str
) -> EventSourceResponse:
    """Handle streaming rapid chat."""
    
    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            # Send initial event
            yield _sse_frame("start", ticker=ticker, model=model_id)
            
            # Get streaming response
            streaming_response = await stream_rapid_chat(ticker, message, model_id)
            
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
                    except json.JSONDecodeError as jde:
                        logger.warning(f"JSON decode error processing chunk: {jde}")
                        yield _sse_frame("error", message="Invalid JSON in stream chunk")
                    except Exception as e:
                        logger.warning(f"Error processing chunk: {e}")
                        yield _sse_frame("error", message="Error processing stream chunk")
            
            yield _sse_frame("end")
            
        except Exception as e:
            logger.error(f"Streaming rapid chat error for {ticker}: {e}", exc_info=True)
            yield _sse_frame("error", message=str(e))
            yield _sse_frame("end")
    
    return EventSourceResponse(event_generator())


# --- Utility Functions ---
async def get_rapid_chat_models() -> dict:
    """Get available models for rapid chat."""
    from backend.config.model_catalogue import get_models_response
    return get_models_response()


async def validate_rapid_chat_request(ticker: str, message: str) -> bool:
    """Validate rapid chat request parameters."""
    if not ticker or not ticker.strip():
        raise HTTPException(
            status_code=400,
            detail="Ticker symbol is required"
        )
    
    if not message or not message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message is required"
        )
    
    # Basic ticker validation (alphanumeric, 1-10 chars)
    if not ticker.strip().isalnum() or len(ticker.strip()) > 10:
        raise HTTPException(
            status_code=400,
            detail="Invalid ticker symbol format"
        )
    
    return True

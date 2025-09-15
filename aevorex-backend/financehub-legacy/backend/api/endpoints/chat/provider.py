"""
OpenRouter Provider
Handles LLM API calls through OpenRouter.
"""

import json
import logging
from typing import Dict, List, AsyncGenerator
from fastapi import HTTPException

from backend.utils.logger_config import get_logger
from backend.config.model_catalogue import resolve_model
from .schemas import ChatResponse

logger = get_logger(__name__)


class OpenRouterProvider:
    """OpenRouter API provider for LLM calls."""
    
    def __init__(self):
        self.base_url = "https://openrouter.ai/api/v1"
        self.api_key = self._get_api_key()
    
    def _get_api_key(self) -> str:
        """Get OpenRouter API key from environment."""
        import os
        # Try both possible environment variable names
        api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("FINBOT_API_KEYS__OPENROUTER")
        if not api_key:
            raise HTTPException(status_code=401, detail="OpenRouter API key not configured")
        return api_key
    
    async def generate(self, messages: List[Dict[str, str]], model: str) -> ChatResponse:
        """Generate non-streaming response."""
        import httpx
        
        model_id = resolve_model(model)
        
        payload = {
            "model": model_id,
            "messages": messages,
            "stream": False
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                if response.status_code in (401, 403):
                    raise HTTPException(status_code=401, detail="Invalid or unauthorized OpenRouter API key")
                response.raise_for_status()
                data = response.json()
                if not data.get("choices") or not isinstance(data["choices"], list) or len(data["choices"]) == 0:
                    logger.error(f"OpenRouter generate error: Missing 'choices' in response. Payload: {payload}, Response: {data}")
                    raise HTTPException(status_code=500, detail="LLM generation failed: Missing 'choices' in response")
                message = data["choices"][0].get("message")
                if not message or "content" not in message:
                    logger.error(f"OpenRouter generate error: Missing 'message.content' in response. Payload: {payload}, Response: {data}")
                    raise HTTPException(status_code=500, detail="LLM generation failed: Missing 'message.content' in response")
                content = message["content"]
                usage = data.get("usage")
                return ChatResponse(
                    content=content,
                    model=model_id,
                    usage=usage
                )
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"OpenRouter generate error: {e}. Payload: {payload}")
                raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")
    
    async def stream(self, messages: List[Dict[str, str]], model: str) -> AsyncGenerator[str, None]:
        """Generate streaming response."""
        import httpx
        
        model_id = resolve_model(model)
        
        payload = {
            "model": model_id,
            "messages": messages,
            "stream": True
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                ) as response:
                    if response.status_code in (401, 403):
                        raise HTTPException(status_code=401, detail="Invalid or unauthorized OpenRouter API key")
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_str = line[6:]  # Remove "data: " prefix
                            if data_str.strip() == "[DONE]":
                                break
                            try:
                                chunk = json.loads(data_str)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError as jde:
                                error_payload = {"error": f"JSON decode error: {str(jde)}", "raw": data_str}
                                logger.error(f"OpenRouter stream JSON decode error: {jde} - Raw data: {data_str}")
                                yield f"data: {json.dumps(error_payload)}\n\n"
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"OpenRouter stream error: {e}. Payload: {payload}")
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

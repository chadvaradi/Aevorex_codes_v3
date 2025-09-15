"""
OpenRouter LLM provider using OpenAI client
"""
from typing import List, Dict, AsyncGenerator
from openai import AsyncOpenAI as OpenAI
from .base import BaseLLMProvider
from api.settings import settings
from api.llm.catalogue import resolve_model, get_default_model_id
import logging

logger = logging.getLogger(__name__)

class OpenRouterProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = settings.openrouter_api_key
        if not self.api_key:
            raise RuntimeError("Missing OPENROUTER_API_KEY")
        
        # Diagnosztikai logolás
        print(f"[openrouter-llm] API key loaded: {self.api_key[:8]}...")
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
            timeout=30.0,
            default_headers={
                "HTTP-Referer": "http://localhost:8084",
                "X-Title": "Aevorex Local Dev",
            },
        )
        self.default_model = get_default_model_id()

    async def generate(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        model_id = resolve_model(model)
        completion = await self.client.chat.completions.create(
            model=model_id,
            messages=messages,
            max_tokens=kwargs.get("max_tokens", 1000),
            temperature=kwargs.get("temperature", 0.7),
        )
        return (completion.choices[0].message.content or "").strip()

    async def stream(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> AsyncGenerator[str, None]:
        try:
            model_id = resolve_model(model)
            resp = await self.client.chat.completions.create(
                model=model_id,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                stream=True,
            )
            
            async for chunk in resp:
                for choice in (chunk.choices or []):
                    delta = getattr(choice, "delta", None)
                    if delta and getattr(delta, "content", None):
                        yield delta.content
        except Exception as e:
            logger.error(f"OpenRouter stream error: {e}")
            raise

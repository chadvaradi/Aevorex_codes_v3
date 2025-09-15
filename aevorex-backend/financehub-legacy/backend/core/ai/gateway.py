from __future__ import annotations

import json
from typing import AsyncGenerator

import httpx

from backend.config import settings


class OpenRouterGateway:
    """Minimal OpenRouter streaming client wrapper (no mock)."""

    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def stream_completion(
        self,
        *,
        model: str,
        messages: list[dict],
        temperature: float,
        max_output_tokens: int,
    ) -> AsyncGenerator[str, None]:
        api_key = (
            settings.API_KEYS.OPENROUTER.get_secret_value()
            if settings.API_KEYS.OPENROUTER
            else None
        )
        if not api_key:
            raise RuntimeError("OpenRouter API key not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # OpenRouter recommends identifying the app via HTTP-Referer or X-Title
        try:
            if getattr(settings.AI, "SITE_URL", None):
                headers["HTTP-Referer"] = settings.AI.SITE_URL  # noqa: N815 (header casing)
            if getattr(settings.AI, "APP_NAME", None):
                headers["X-Title"] = settings.AI.APP_NAME
        except Exception:
            pass
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
            "stream": True,
        }
        url = "https://openrouter.ai/api/v1/chat/completions"

        async with self.client.stream(
            "POST",
            url,
            headers=headers,
            json=payload,
            timeout=settings.AI.TIMEOUT_SECONDS,
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    data = line[len("data: ") :]
                    if data.strip() == "[DONE]":
                        break
                    try:
                        obj = json.loads(data)
                        delta = (
                            obj.get("choices", [{}])[0].get("delta", {}).get("content")
                        )
                        if delta:
                            yield delta
                    except Exception:
                        # best‑effort: ignore malformed chunks
                        continue

    async def completion(
        self,
        *,
        model: str,
        messages: list[dict],
        temperature: float,
        max_output_tokens: int,
    ) -> str:
        """Non-streaming completion for single response generation."""
        api_key = (
            settings.API_KEYS.OPENROUTER.get_secret_value()
            if settings.API_KEYS.OPENROUTER
            else None
        )
        if not api_key:
            raise RuntimeError("OpenRouter API key not configured")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        # OpenRouter recommends identifying the app via HTTP-Referer or X-Title
        try:
            if getattr(settings.AI, "SITE_URL", None):
                headers["HTTP-Referer"] = settings.AI.SITE_URL  # noqa: N815 (header casing)
            if getattr(settings.AI, "APP_NAME", None):
                headers["X-Title"] = settings.AI.APP_NAME
        except Exception:
            pass
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_output_tokens,
            "stream": False,  # Non-streaming
        }
        url = "https://openrouter.ai/api/v1/chat/completions"

        response = await self.client.post(
            url, headers=headers, json=payload, timeout=settings.AI.TIMEOUT_SECONDS
        )
        response.raise_for_status()

        data = response.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "")

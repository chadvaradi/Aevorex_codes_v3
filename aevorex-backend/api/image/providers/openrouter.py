from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx

from api.settings import settings
from api.image.catalogue import resolve_model
from .base import BaseImageProvider, ImageGenResult


class OpenRouterImageProvider(BaseImageProvider):
    """
    OpenRouter alapú képgenerálás.

    Megjegyzés: 
    - Gemini modellek: /chat/completions endpoint (multimodal)
    - Egyéb modellek (SDXL, Flux): /images endpoint (text-to-image)
    """

    def __init__(self) -> None:
        self.api_key = settings.openrouter_api_key
        if not self.api_key:
            raise RuntimeError("Missing OPENROUTER_API_KEY")

        # Diagnosztikai logolás
        print(f"[openrouter-image] API key loaded: {self.api_key[:8]}...")

        self.base_url = "https://openrouter.ai/api/v1/"
        # Kliens megosztott connection pool-lal
        self._client = httpx.AsyncClient(timeout=60.0)

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "HTTP-Referer": "http://localhost:3000",
            "X-Title": "Aevorex Dev",
        }

    async def _post_with_retry(
        self,
        path: str,
        payload: Dict[str, Any],
        *,
        retries: int = 2,
        backoff: float = 0.8,
    ) -> httpx.Response:
        last_exc: Optional[Exception] = None
        url = f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"
        for attempt in range(retries + 1):
            try:
                resp = await self._client.post(url, headers=self._headers(), json=payload, timeout=30.0)
                
                # Diagnosztikai logolás
                ct = resp.headers.get("content-type", "")
                txt = await resp.aread()  # bytes
                snippet = txt[:500].decode("utf-8", errors="replace")
                
                print(f"[openrouter-image] POST → {resp.request.url} :: {resp.status_code} {ct}")
                print(f"[openrouter-image] Response snippet: {snippet}")
                
                # Speciális 401-es hiba kezelés
                if resp.status_code == 401:
                    print(f"[openrouter-image] 401 Unauthorized - API key issue detected")
                    print(f"[openrouter-image] Full response body: {txt.decode('utf-8', errors='replace')}")
                    print(f"[openrouter-image] API key (first 8 chars): {self.api_key[:8]}...")
                
                resp.raise_for_status()
                return resp
                    
            except (httpx.ReadTimeout, httpx.ConnectTimeout, httpx.RemoteProtocolError, httpx.HTTPStatusError) as e:
                last_exc = e
                # Csak 5xx és timeout esetén retry, 4xx esetén ne
                status = getattr(e, "response", None).status_code if hasattr(e, "response") else None
                if attempt < retries and (status is None or status >= 500):
                    await asyncio.sleep(backoff * (2 ** attempt))
                    continue
                raise
        assert last_exc  # csak mypy miatt
        raise last_exc

    async def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        n: int = 1,
        size: str = "1024x1024",
        **kwargs: Any,
    ) -> List[ImageGenResult]:
        model_id = resolve_model(model)
        
        # Ha Gemini modell, akkor /chat/completions endpoint-ot használunk
        if "gemini" in model_id.lower():
            return await self._generate_via_chat(prompt, model_id, **kwargs)
        else:
            # Egyéb modellek (SDXL, Flux) maradnak az /images endpoint-on
            return await self._generate_via_images(prompt, model_id, n, size, **kwargs)

    async def _generate_via_chat(
        self, 
        prompt: str, 
        model_id: str, 
        **kwargs: Any
    ) -> List[ImageGenResult]:
        """Gemini modell: /chat/completions endpoint használata"""
        payload = {
            "model": model_id,
            "messages": [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": prompt
                }]
            }],
            "max_tokens": 1000,
            "temperature": 0.7
        }
        
        resp = await self._post_with_retry("/chat/completions", payload)
        
        try:
            body = resp.json()
        except Exception as e:
            # Diagnosztikai információ
            ct = resp.headers.get("content-type", "")
            txt = await resp.aread()
            snippet = txt[:500].decode("utf-8", errors="replace")
            print(f"JSON parse failed in _generate_via_chat(). Status: {resp.status_code}, CT: {ct}")
            print(f"Response snippet: {snippet}")
            raise RuntimeError(f"OpenRouter API returned non-JSON response: {resp.status_code} {ct}")
        
        items = []
        # Válasz feldolgozás: szöveg + esetleges képek
        if "choices" in body and len(body["choices"]) > 0:
            message = body["choices"][0]["message"]
            if "content" in message:
                # Ha lista (multimodal), keressük a képeket
                if isinstance(message["content"], list):
                    for part in message["content"]:
                        if part.get("type") == "image_url" and "image_url" in part:
                            item = ImageGenResult(
                                url=part["image_url"].get("url"),
                                b64=None,
                                width=None,
                                height=None,
                                mime_type="image/png",
                                revised_prompt=prompt,
                                seed=None,
                            )
                            items.append(item)
                        elif part.get("type") == "inline_data" and "data" in part:
                            item = ImageGenResult(
                                url=None,
                                b64=part["data"],
                                width=None,
                                height=None,
                                mime_type="image/png",
                                revised_prompt=prompt,
                                seed=None,
                            )
                            items.append(item)
                # Ha string (szöveges leírás), akkor nincs kép
                elif isinstance(message["content"], str):
                    # Szöveges leírás, nincs generált kép
                    print(f"[openrouter-image] Gemini returned text description: {message['content'][:100]}...")
        
        return items

    async def _generate_via_images(
        self, 
        prompt: str, 
        model_id: str, 
        n: int, 
        size: str, 
        **kwargs: Any
    ) -> List[ImageGenResult]:
        """Egyéb modellek: /images endpoint használata (eredeti logika)"""
        payload = {
            "model": model_id,
            "prompt": prompt,
            "size": size,
            "n": max(1, min(int(n), 8)),
        }
        
        # opcionális paraméterek átengedése
        allowed_extra = (
            "user",
            "seed",
            "quality",
            "style",
            "negative_prompt",
        )
        for key in allowed_extra:
            if key in kwargs:
                payload[key] = kwargs[key]

        resp = await self._post_with_retry("/images", payload)
        
        try:
            body = resp.json()
        except Exception as e:
            # Diagnosztikai információ
            ct = resp.headers.get("content-type", "")
            txt = await resp.aread()
            snippet = txt[:500].decode("utf-8", errors="replace")
            print(f"JSON parse failed in _generate_via_images(). Status: {resp.status_code}, CT: {ct}")
            print(f"Response snippet: {snippet}")
            raise RuntimeError(f"OpenRouter API returned non-JSON response: {resp.status_code} {ct}")
        
        # OpenRouter Images API válasz feldolgozása
        items = []
        for item_data in body.get("data", []):
            item = ImageGenResult(
                url=item_data.get("url"),
                b64=item_data.get("b64_json"),
                width=item_data.get("width"),
                height=item_data.get("height"),
                mime_type=item_data.get("mime_type", "image/png"),
                revised_prompt=item_data.get("revised_prompt", prompt),
                seed=item_data.get("seed"),
            )
            items.append(item)
        
        return items

    async def aclose(self) -> None:
        await self._client.aclose()
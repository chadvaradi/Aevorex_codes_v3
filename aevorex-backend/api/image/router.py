from __future__ import annotations

import time
import os
import uuid
import binascii
from typing import List

from fastapi import APIRouter, HTTPException
from api.image.schemas import (
    ImageGenRequest,
    ImageGenResponse,
    ImageItem,
    ImageModelsResponse,
    ImageAnalyzeRequest,
    ImageAnalyzeResponse,
)
from api.image.utils import save_base64_image
from api.image.catalogue import (
    get_models_response,
    is_allowed,
    resolve_model,
    get_provider_hint,
    get_default_model_id,
)
from api.image.providers.openrouter import OpenRouterImageProvider
from api.image.providers.google_genai import GoogleGeminiImageProvider
from api.settings import settings

router = APIRouter()

# Provider inicializálás
_openrouter_provider = None
_google_provider = None

def get_openrouter_provider():
    global _openrouter_provider
    if _openrouter_provider is None:
        if not settings.openrouter_api_key:
            raise RuntimeError("OPENROUTER_API_KEY is required for OpenRouter models")
        _openrouter_provider = OpenRouterImageProvider()
    return _openrouter_provider

def get_google_provider():
    global _google_provider
    if _google_provider is None:
        if not settings.google_api_key:
            print(f"[image-router] ERROR: GEMINI_API_KEY is missing! Current value: '{settings.google_api_key}'")
            raise RuntimeError("GEMINI_API_KEY is required for Google models")
        print(f"[image-router] Google API key loaded: {settings.google_api_key[:8]}...")
        _google_provider = GoogleGeminiImageProvider()
    return _google_provider


@router.get("/models", response_model=ImageModelsResponse)
def list_models() -> ImageModelsResponse:
    """Képgeneráló modellek listája (alias→id) és a default."""
    return get_models_response()


def _validate_model(m: str | None):
    if m is None:
        return
    # elfogadjuk az alias-t és a feloldott id-t is
    if not is_allowed(m) and not is_allowed(resolve_model(m)):
        raise HTTPException(status_code=400, detail="Invalid image model")


@router.post("/generate", response_model=ImageGenResponse)
async def generate_image(req: ImageGenRequest) -> ImageGenResponse:
    """
    Kép(ek) generálása. URL-first (b64 fallback).
    Provider automatikus választás a modell alapján.
    """
    _validate_model(req.model)

    # Modell feloldása és provider választás
    model_id = resolve_model(req.model)
    provider_type = get_provider_hint(model_id)
    
    print(f"[image-router] Using {provider_type} provider for model: {model_id}")
    
    # Megfelelő provider kiválasztása
    if provider_type == "google":
        provider = get_google_provider()
    else:
        provider = get_openrouter_provider()

    started = time.perf_counter()
    try:
        print(f"[image-router] Starting generation with prompt: '{req.prompt[:50]}...'")
        results = await provider.generate(
            req.prompt,
            model=req.model,
            n=req.n,
            size=req.size,
            seed=req.seed,
            quality=req.quality,
            style=req.style,
            negative_prompt=req.negative_prompt,
            background=req.background,
            response_format=req.response_format,
        )
        print(f"[image-router] Generation completed, got {len(results)} results")
    except RuntimeError as e:
        print(f"[image-router] RuntimeError during generation: {e}")
        if str(e).startswith("429:"):
            raise HTTPException(status_code=429, detail=str(e)[4:].strip())
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    except Exception as e:
        print(f"[image-router] Exception during generation: {e}")
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")
    
    elapsed_ms = int((time.perf_counter() - started) * 1000)

    items: List[ImageItem] = []
    include_b64 = settings.image_include_b64
    
    for r in results:
        url = r.url
        mime = r.mime_type
        b64 = r.b64

        # Ha nincs URL, de van base64, akkor fájlba mentjük
        if not url and b64:
            try:
                fname, mime = save_base64_image(
                    b64=b64,
                    out_dir=settings.image_output_dir,
                    mime=mime or "image/png",
                )
                base = settings.image_base_url.rstrip("/")
                url = f"{base}/{fname}"
                if not include_b64:
                    b64 = None  # Ne küldjük vissza a több MB-ot
            except binascii.Error as e:
                raise HTTPException(status_code=400, detail=f"Invalid base64 image data: {str(e)}")

        items.append(ImageItem(
            url=url,
            b64=b64 if include_b64 else None,
            width=r.width,
            height=r.height,
            mime_type=mime,
            revised_prompt=r.revised_prompt,
            seed=r.seed,
        ))

    # Guard: ha nincs eredmény, dobjunk hibát
    if not items:
        print(f"[image-router] ERROR: No items generated! Results count: {len(results)}")
        for i, r in enumerate(results):
            print(f"[image-router] Result {i}: url={r.url}, b64_len={len(r.b64) if r.b64 else 0}, mime={r.mime_type}")
        raise HTTPException(status_code=500, detail="Image pipeline returned no result")

    return ImageGenResponse(
        model=model_id,
        items=items,
        processing_time_ms=elapsed_ms,
    )

@router.post("/analyze", response_model=ImageAnalyzeResponse)
async def analyze_image(req: ImageAnalyzeRequest) -> ImageAnalyzeResponse:
    """
    Kép elemzése a Google Gemini modellel.
    """
    try:
        provider = get_google_provider()
        analysis = await provider.analyze(req.image_data, req.question)
        
        return ImageAnalyzeResponse(
            analysis=analysis,
            model=get_default_model_id(),
            question=req.question
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")


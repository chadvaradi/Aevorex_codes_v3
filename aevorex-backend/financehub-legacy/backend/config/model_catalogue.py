"""
Centralized model catalogue for AI providers (OpenRouter, OpenAI, Google, Anthropic, stb.)
Supports both static defaults and dynamic refresh from OpenRouter API.
"""

from typing import Optional, Dict
from pydantic import BaseModel
import httpx
import os

class ModelInfo(BaseModel):
    id: str
    provider: str
    max_tokens: int
    price_input: Optional[float] = None   # USD / 1M tokens
    price_output: Optional[float] = None  # USD / 1M tokens


# --- Static default models (fallback when API is not reachable) ---
MODEL_CATALOGUE: Dict[str, ModelInfo] = {
    "deepseek/deepseek-chat-v3.1:free": ModelInfo(
        id="deepseek/deepseek-chat-v3.1:free",
        provider="deepseek",
        max_tokens=8192,
        price_input=None,
        price_output=None,
    ),
    "google/gemini-2.0-flash-001": ModelInfo(
        id="google/gemini-2.0-flash-001",
        provider="google",
        max_tokens=8192,
        price_input=0.10,
        price_output=0.40,
    ),
}


# --- Dynamic fetch from OpenRouter API ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def fetch_openrouter_models() -> Dict[str, ModelInfo]:
    """Fetch available models from OpenRouter API and return as dict."""
    if not OPENROUTER_API_KEY:
        return {}

    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
    url = "https://openrouter.ai/api/v1/models"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
    except Exception as e:
        print(f"⚠️ Failed to fetch models from OpenRouter: {e}")
        return {}

    models: Dict[str, ModelInfo] = {}
    for m in data.get("data", []):
        try:
            models[m["id"]] = ModelInfo(
                id=m["id"],
                provider=m.get("provider", "unknown"),
                max_tokens=m.get("context_length", 0),
                price_input=m.get("pricing", {}).get("prompt"),
                price_output=m.get("pricing", {}).get("completion"),
            )
        except Exception:
            continue

    return models


def refresh_model_catalogue() -> None:
    """Update the static catalogue with latest OpenRouter data (if available)."""
    updated = fetch_openrouter_models()
    if updated:
        MODEL_CATALOGUE.update(updated)
        print(f"✅ OpenRouter models refreshed: {len(updated)} available")
    else:
        print("⚠️ Using static MODEL_CATALOGUE (no dynamic update)")

# Export defaults for compatibility
MODEL_NAME_PRIMARY = MODEL_CATALOGUE["deepseek/deepseek-chat-v3.1:free"].id
MODEL_NAME_FALLBACK = MODEL_CATALOGUE["google/gemini-2.0-flash-001"].id

# --- Chat-specific model aliases ---
CHAT_MODELS = {
    "deepseek-free": "deepseek/deepseek-chat-v3.1:free",
    "gemini-2.0-flash": "google/gemini-2.0-flash-001",
}

CHAT_DEFAULT = "deepseek-free"


def get_default_model_id() -> str:
    """Get the default model ID for chat."""
    return CHAT_MODELS[CHAT_DEFAULT]


def resolve_model(alias_or_id: str | None) -> str:
    """Resolve model alias to full ID."""
    if not alias_or_id:
        return get_default_model_id()
    # alias -> ID; ha már teljes ID érkezik, úgy hagyjuk
    return CHAT_MODELS.get(alias_or_id, alias_or_id)


def is_allowed(alias_or_id: str) -> bool:
    """Check if model is allowed for chat."""
    return alias_or_id in CHAT_MODELS or alias_or_id in CHAT_MODELS.values()


def get_models_response() -> dict:
    """Get available models response for chat."""
    return {"models": CHAT_MODELS, "default": CHAT_DEFAULT}


def validate_model(model: str | None) -> str:
    """Validate and resolve model for chat."""
    if model is None:
        return get_default_model_id()
    if not is_allowed(model) and not is_allowed(resolve_model(model)):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid model")
    return resolve_model(model)

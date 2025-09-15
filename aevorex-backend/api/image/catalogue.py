from typing import Dict

# --- Modellkatalógus (alias -> Provider + Model ID) -------------------------
MODELS: Dict[str, str] = {
    # Google Gemini modellek (Google provider)
    "gemini-2.5-flash-image": "google/gemini-2.5-flash-image-preview",
    "gemini-2.0-flash-image": "google/gemini-2.0-flash-image-preview",
    "gemini-1.5-flash-image": "google/gemini-1.5-flash-image-preview",
    
    # OpenRouter modellek (OpenRouter provider)
    "flux-schnell": "black-forest-labs/flux-schnell",
    "sdxl": "stability-ai/sdxl",
}

DEFAULT = "gemini-2.5-flash-image"

# --- Provider választási logika ---------------------------------------------
def get_provider_hint(model_id: str) -> str:
    """
    Meghatározza, melyik provider-t kell használni a modellhez.
    
    Returns:
        "google" vagy "openrouter"
    """
    if model_id.startswith("google/") or any(
        alias in model_id for alias in ["gemini", "google"]
    ):
        return "google"
    return "openrouter"

# --- Helper függvények ------------------------------------------------------
def resolve_model(name_or_id: str | None) -> str:
    """
    Alias -> teljes model ID feloldás.
    Ha már teljes ID jött, akkor változtatás nélkül visszaadjuk.
    """
    if not name_or_id:
        return MODELS[DEFAULT]
    return MODELS.get(name_or_id, name_or_id)

def is_allowed(name_or_id: str | None) -> bool:
    """
    Engedélyezett-e a kérdéses modell? (alias vagy teljes ID)
    """
    if not name_or_id:
        return True
    return name_or_id in MODELS or name_or_id in MODELS.values()

def get_default_model_id() -> str:
    """Az alapértelmezett modell teljes ID-ja."""
    return resolve_model(DEFAULT)

def get_models_response() -> Dict[str, Dict[str, str] | str]:
    """
    Visszaadja a /api/image/models endpoint válaszát.
    """
    return {
        "models": MODELS,
        "default": DEFAULT,
    }
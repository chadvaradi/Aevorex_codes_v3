# LLM model catalogue (DeepSeek default + Gemini alt)

MODELS = {
    "deepseek-free": "deepseek/deepseek-chat-v3.1:free",
    "gemini-2.5-flash": "google/gemini-2.5-flash",
}

DEFAULT = "deepseek-free"

def get_default_model_id() -> str:
    return MODELS[DEFAULT]

def resolve_model(alias_or_id: str | None) -> str:
    if not alias_or_id:
        return get_default_model_id()
    # alias -> ID; ha már teljes ID érkezik, úgy hagyjuk
    return MODELS.get(alias_or_id, alias_or_id)

def is_allowed(alias_or_id: str) -> bool:
    return alias_or_id in MODELS or alias_or_id in MODELS.values()

def get_models_response() -> dict:
    return {"models": MODELS, "default": DEFAULT}

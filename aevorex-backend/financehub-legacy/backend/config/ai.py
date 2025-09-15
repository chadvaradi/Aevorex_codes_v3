"""
AI/LLM service settings.
"""

from pydantic import field_validator, BaseModel, Field
from pydantic_settings import SettingsConfigDict

from ._core import logger
from .model_catalogue import MODEL_NAME_PRIMARY, MODEL_NAME_FALLBACK


class AISettings(BaseModel):
    """AI/LLM szolgáltatások beállításai."""

    ENABLED: bool = True
    PROVIDER: str = "openrouter"
    MODEL_NAME_PRIMARY: str | None = MODEL_NAME_PRIMARY
    MODEL_NAME_FALLBACK: str | None = MODEL_NAME_FALLBACK
    MAX_TOKENS_PRIMARY: int = Field(default=8000)
    MAX_TOKENS_FALLBACK: int = Field(default=4000)
    TEMPERATURE: float = 0.3
    TEMPERATURE_PRIMARY: float | None = 0.35
    TEMPERATURE_FALLBACK: float | None = 0.3
    RETRY_MAX_ATTEMPTS: int = 3
    RETRY_MIN_WAIT_SECONDS: int = 1
    RETRY_MAX_WAIT_SECONDS: int = 10
    RETRY_BACKOFF_FACTOR: float = 1.5
    TIMEOUT_SECONDS: float = 180.0
    RETRY_ON_NO_DATA_WITH_SUCCESS_STATUS: bool = Field(default=True)
    AI_PRICE_DAYS_FOR_PROMPT: int = Field(default=60)

    @field_validator("PROVIDER")
    @classmethod
    def _validate_provider_identifier(cls, v: str) -> str:
        provider = v.strip().lower()
        if not provider:
            logger.warning(
                "AI.PROVIDER is empty. If AI.ENABLED is True, this will be an issue."
            )
        return provider

    model_config = SettingsConfigDict(
        env_prefix="FINBOT_AI__", env_file="env.local", extra="ignore"
    )

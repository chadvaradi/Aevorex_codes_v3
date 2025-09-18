"""
API Key settings for external services.
"""

from pydantic import field_validator, Field
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings

from backend.config._core import logger


class APIKeysSettings(BaseSettings):
    """API kulcsok külső szolgáltatásokhoz."""

    ALPHA_VANTAGE: str | None = Field(
        default=None, description="Alpha Vantage API kulcs."
    )
    OPENROUTER: str | None = Field(
        default=None, description="OpenRouter API kulcs."
    )
    MARKETAUX: str | None = Field(
        default=None, description="MarketAux API kulcs."
    )
    FMP: str | None = Field(
        default=None, description="Financial Modeling Prep (FMP) API kulcs."
    )
    NEWSAPI: str | None = Field(
        default=None, description="NewsAPI.org API kulcs."
    )
    EODHD: str | None = Field(
        default=None, description="EOD Historical Data API kulcs."
    )
    FRED: str | None = Field(
        default=None, description="Federal Reserve (FRED) API key."
    )

    @field_validator("*", mode="before")
    @classmethod
    def _check_api_key_format_if_string(
        cls, v: str | None
    ) -> str | None:
        """Ellenőrzi az API kulcsok formátumát, ha stringként érkeznek."""
        if v is None or v == "":
            return None

        if isinstance(v, str):
            v_stripped = v.strip()
            if len(v_stripped) < 10:  # Túl rövid API kulcs
                logger.warning(
                    f"API key appears to be too short (length: {len(v_stripped)}). This might be a configuration error."
                )
            elif (
                not v_stripped.replace("-", "").replace("_", "").isalnum()
            ):  # Nem alfanumerikus karakterek
                logger.warning(
                    "API key contains unexpected characters. Ensure it's copied correctly."
                )

        return v

    model_config = SettingsConfigDict(env_prefix="FINBOT_API_KEYS__", extra="ignore")

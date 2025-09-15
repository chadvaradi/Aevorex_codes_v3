"""
API Key settings for external services.
"""

from pydantic import field_validator, Field
from pydantic.types import SecretStr
from pydantic_settings import SettingsConfigDict
from pydantic_settings import BaseSettings

from ._core import logger


class APIKeysSettings(BaseSettings):
    """API kulcsok külső szolgáltatásokhoz."""

    ALPHA_VANTAGE: SecretStr | None = Field(
        default=None, description="Alpha Vantage API kulcs (SecretStr)."
    )
    OPENROUTER: SecretStr | None = Field(
        default=None, description="OpenRouter API kulcs (SecretStr)."
    )
    MARKETAUX: SecretStr | None = Field(
        default=None, description="MarketAux API kulcs (SecretStr)."
    )
    FMP: SecretStr | None = Field(
        default=None, description="Financial Modeling Prep (FMP) API kulcs (SecretStr)."
    )
    NEWSAPI: SecretStr | None = Field(
        default=None, description="NewsAPI.org API kulcs (SecretStr)."
    )
    EODHD: SecretStr | None = Field(
        default=None, description="EOD Historical Data API kulcs (SecretStr)."
    )
    FRED: SecretStr | None = Field(
        default=None, description="Federal Reserve (FRED) API key (SecretStr)."
    )

    @field_validator("*", mode="before")
    @classmethod
    def _check_api_key_format_if_string(
        cls, v: str | SecretStr | None
    ) -> str | SecretStr | None:
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

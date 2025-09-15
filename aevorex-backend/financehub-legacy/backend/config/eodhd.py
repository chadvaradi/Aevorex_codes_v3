"""
EODHD configuration.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from ._core import logger


class EODHDSettings(BaseSettings):
    """EODHD API és feature beállítások."""

    # API
    API_KEY: str = Field(..., env="FINBOT_EODHD__API_KEY")
    BASE_URL: str = Field("https://eodhd.com/api", env="FINBOT_EODHD__BASE_URL")

    # Feature flags
    USE_FOR_COMPANY_INFO: bool = Field(default=False)
    USE_FOR_FINANCIALS: bool = Field(default=False)
    USE_FOR_OHLCV_DAILY: bool = Field(default=False)
    USE_FOR_OHLCV_INTRADAY: bool = Field(default=False)

    model_config = SettingsConfigDict(env_prefix="FINBOT_EODHD__")

    def log_features(self) -> None:
        enabled = [
            field.replace("USE_FOR_", "").lower().replace("_", " ")
            for field in self.model_fields
            if field.startswith("USE_FOR_") and getattr(self, field)
        ]
        if enabled:
            logger.info(f"EODHD Features enabled: {', '.join(enabled)}")
        else:
            logger.info("EODHD Features: all disabled.")


# Globális config instance
settings = EODHDSettings()
settings.log_features()

"""
Environment and developer settings.
"""

from typing import Literal
from pydantic import field_validator, BaseModel, Field, model_validator

from ._core import logger


class EnvironmentSettings(BaseModel):
    """Futási környezet és fejlesztői beállítások."""

    NODE_ENV: Literal["development", "production", "test"] = "production"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    DEBUG_MODE: bool = Field(default=False)
    RELOAD_UVICORN: bool = Field(default=False)

    @field_validator("LOG_LEVEL")
    @classmethod
    def _validate_and_normalize_log_level(cls, v: str) -> str:
        level = v.strip().upper()
        if level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise ValueError(f"Invalid LOG_LEVEL: {level}")
        return level

    @model_validator(mode="after")
    def _check_environment_consistency(self) -> "EnvironmentSettings":
        if self.NODE_ENV == "development":
            if self.LOG_LEVEL not in ["DEBUG", "INFO"]:
                logger.warning(
                    f"In development, LOG_LEVEL is '{self.LOG_LEVEL}'. Consider using 'DEBUG' or 'INFO'."
                )
            if not self.DEBUG_MODE:
                self.DEBUG_MODE = True
                logger.info(
                    "DEBUG_MODE automatically enabled in development environment."
                )
            if not self.RELOAD_UVICORN:
                self.RELOAD_UVICORN = True
                logger.info(
                    "RELOAD_UVICORN automatically enabled in development environment."
                )

        if self.NODE_ENV == "production" and self.DEBUG_MODE:
            raise RuntimeError(
                "Running in production with DEBUG_MODE enabled is not allowed."
            )

        logger.info(
            f"Environment loaded: NODE_ENV={self.NODE_ENV}, LOG_LEVEL={self.LOG_LEVEL}, DEBUG_MODE={self.DEBUG_MODE}, RELOAD_UVICORN={self.RELOAD_UVICORN}"
        )

        return self

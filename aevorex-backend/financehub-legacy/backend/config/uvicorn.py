"""
Uvicorn ASGI server settings.
"""

from pydantic import field_validator, BaseModel, Field, model_validator
from pydantic.types import PositiveInt
from pydantic_settings import SettingsConfigDict

from .environment import EnvironmentSettings


class UvicornSettings(BaseModel):
    """Uvicorn ASGI szerver beállítások."""

    HOST: str = Field(default="localhost")
    PORT: PositiveInt = Field(default=8084)
    RELOAD: bool = Field(default=False)
    LOG_LEVEL: str = Field(default="info")
    ACCESS_LOG: bool = Field(default=False)
    WORKERS: PositiveInt = Field(default=1)

    model_config = SettingsConfigDict(
        env_prefix="FINBOT_UVICORN__", env_file="env.local", extra="ignore"
    )

    @field_validator("LOG_LEVEL")
    @classmethod
    def _validate_log_level(cls, v: str) -> str:
        level = v.strip().lower()
        valid_levels = ["debug", "info", "warning", "error", "critical", "trace"]
        if level not in valid_levels:
            raise ValueError(
                f"Invalid Uvicorn LOG_LEVEL: '{level}'. Must be one of {valid_levels}"
            )
        return level

    @model_validator(mode="after")
    def _adjust_for_environment(self) -> "UvicornSettings":
        env_settings = EnvironmentSettings()  # Get default or env-loaded settings

        if env_settings.NODE_ENV == "development" and not self.RELOAD:
            self.RELOAD = True

        # Sync Uvicorn's log level with the application's log level if more verbose
        app_log_level = env_settings.LOG_LEVEL.lower()
        if app_log_level == "debug" and self.LOG_LEVEL != "debug":
            self.LOG_LEVEL = "debug"

        return self

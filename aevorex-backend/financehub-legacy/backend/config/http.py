"""
HTTP client settings.
"""

from pydantic import BaseModel, Field
from pydantic.types import PositiveFloat, NonNegativeFloat, PositiveInt, NonNegativeInt
from pydantic.networks import AnyHttpUrl
from pydantic_settings import SettingsConfigDict


class HttpClientSettings(BaseModel):
    """HTTP kliens beállítások."""

    REQUEST_TIMEOUT_SECONDS: PositiveFloat = Field(default=45.0)
    CONNECT_TIMEOUT_SECONDS: PositiveFloat = Field(default=10.0)
    POOL_TIMEOUT_SECONDS: PositiveFloat = Field(default=5.0)
    MAX_CONNECTIONS: PositiveInt | None = Field(default=100)
    MAX_KEEPALIVE_CONNECTIONS: PositiveInt | None = Field(default=20)
    USER_AGENT: str = Field(
        default="AevorexFinBot/UnsetVersion (Backend; +https://aevorex.com/finbot)"
    )
    DEFAULT_REFERER: AnyHttpUrl = Field(default=AnyHttpUrl("https://aevorex.com/"))
    RETRY_COUNT: NonNegativeInt = Field(default=2)
    RETRY_BACKOFF_FACTOR: NonNegativeFloat = Field(default=0.5)

    model_config = SettingsConfigDict(
        env_prefix="FINBOT_HTTP_CLIENT__", env_file="env.local", extra="ignore"
    )

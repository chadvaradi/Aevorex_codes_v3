"""
Redis server and database settings.
"""

from pydantic import BaseModel, Field
from pydantic.types import PositiveInt, NonNegativeInt
from pydantic_settings import SettingsConfigDict


class RedisSettings(BaseModel):
    """Redis szerver és adatbázis beállítások."""

    HOST: str = Field(default="localhost")
    PORT: PositiveInt = Field(default=6379)
    DB_CACHE: NonNegativeInt = Field(default=0)
    DB_CELERY_BROKER: NonNegativeInt = Field(default=1)
    DB_CELERY_BACKEND: NonNegativeInt = Field(default=2)
    CONNECT_TIMEOUT_SECONDS: PositiveInt = Field(default=5)
    SOCKET_TIMEOUT_SECONDS: PositiveInt = Field(default=10)
    DEFAULT_TTL_SECONDS: PositiveInt = Field(default=300)
    LOCK_TTL_SECONDS: PositiveInt = Field(default=120)
    LOCK_RETRY_DELAY_SECONDS: PositiveInt = Field(default=1)

    @property
    def CELERY_BROKER_URL(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.DB_CELERY_BROKER}"

    @property
    def CELERY_RESULT_BACKEND(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.DB_CELERY_BACKEND}"

    model_config = SettingsConfigDict(env_prefix="FINBOT_REDIS__")

"""
Caching settings.
"""

from pydantic import BaseModel, Field
from pydantic.types import PositiveInt, NonNegativeFloat, PositiveFloat


class CacheSettings(BaseModel):
    """Gyorsítótárazási beállítások."""

    ENABLED: bool = Field(default=True)
    DEFAULT_TTL_SECONDS: PositiveInt = Field(default=300)
    LOCK_TTL_SECONDS: PositiveInt = Field(default=2 * 60)
    LOCK_BLOCKING_TIMEOUT_SECONDS: NonNegativeFloat = Field(default=6.0)
    LOCK_RETRY_DELAY_SECONDS: PositiveFloat = Field(default=0.5)
    MAX_SIZE: PositiveInt | None = Field(default=1024)

    # Specific TTLs
    FETCH_TTL_COMPANY_INFO_SECONDS: PositiveInt = Field(default=24 * 3600)
    FETCH_TTL_FINANCIALS_SECONDS: PositiveInt = Field(default=12 * 3600)
    FETCH_TTL_NEWS_SECONDS: PositiveInt = Field(default=1 * 3600)
    FETCH_TTL_OHLCV_SECONDS: PositiveInt = Field(default=1 * 3600)
    NEWS_RAW_FETCH_TTL_SECONDS: PositiveInt = Field(default=15 * 60)
    EODHD_DAILY_OHLCV_TTL: PositiveInt = Field(default=4 * 3600)
    EODHD_INTRADAY_OHLCV_TTL: PositiveInt = Field(default=5 * 60)
    AGGREGATED_TTL_SECONDS: PositiveInt = Field(default=15 * 60)
    FETCH_FAILURE_TTL_SECONDS: PositiveInt = Field(default=10 * 60)

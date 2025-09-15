"""
News processing settings.
"""

from pydantic import field_validator, BaseModel, Field, model_validator
from pydantic.types import PositiveInt, NonNegativeInt, NonNegativeFloat

from ._core import _parse_env_list_str_utility


class NewsProcessingSettings(BaseModel):
    """Hírek feldolgozásának beállításai."""

    FETCH_LIMIT: PositiveInt = Field(default=30)
    MAX_AGE_DAYS_FILTER: PositiveInt | None = Field(default=90)
    MIN_ITEMS_FOR_PROMPT: NonNegativeInt = Field(default=3)
    TARGET_COUNT_FOR_PROMPT: PositiveInt = Field(default=7)
    MAX_ITEMS_FOR_PROMPT: PositiveInt = Field(default=15)
    SENTIMENT_THRESHOLD_PROMPT: NonNegativeFloat = Field(default=0.1, ge=0.0, le=1.0)
    RELEVANCE_THRESHOLD_PROMPT: NonNegativeFloat = Field(default=0.15, ge=0.0, le=1.0)
    ENABLED_SOURCES: list[str] = Field(default_factory=list)
    SOURCE_PRIORITY: list[str] = Field(default_factory=list)
    MIN_UNIQUE_TARGET: PositiveInt = Field(default=5)

    @field_validator("ENABLED_SOURCES", "SOURCE_PRIORITY", mode="before")
    @classmethod
    def _parse_news_string_list_to_lower(cls, v: any) -> list[str]:
        return _parse_env_list_str_utility(v, "news sources", lowercase_items=True)

    @model_validator(mode="after")
    def _check_prompt_limits_consistency(self) -> "NewsProcessingSettings":
        if self.MIN_ITEMS_FOR_PROMPT > self.TARGET_COUNT_FOR_PROMPT:
            raise ValueError(
                "MIN_ITEMS_FOR_PROMPT cannot be greater than TARGET_COUNT_FOR_PROMPT."
            )
        if self.TARGET_COUNT_FOR_PROMPT > self.MAX_ITEMS_FOR_PROMPT:
            raise ValueError(
                "TARGET_COUNT_FOR_PROMPT cannot be greater than MAX_ITEMS_FOR_PROMPT."
            )
        return self

"""
Data source settings.
"""

from pydantic import field_validator, BaseModel, Field

from ._core import logger


class DataSourceSettings(BaseModel):
    """Data source configuration settings."""

    # Market data
    PRIMARY_MARKET: str = Field(default="eodhd", description="Primary market data source.")
    SECONDARY_MARKET: str | None = Field(
        default="fmp,marketaux,alphavantage",
        description="Secondary market data sources (comma-separated).",
    )

    # Fundamentals data
    PRIMARY_FUNDAMENTALS: str | None = Field(default=None, description="Primary fundamentals data source.")
    SECONDARY_FUNDAMENTALS: str = Field(
        default="yfinance",
        description="Secondary fundamentals data source."
    )

    # Macro data
    PRIMARY_MACRO: str = Field(default="ecb", description="Primary macroeconomic data source.")
    SECONDARY_MACRO: str | None = Field(default="fred", description="Secondary macro data source.")

    INFO_TEXT: str = Field(
        default="Data sources configuration", description="Information text."
    )

    @field_validator("*", mode="before")
    @classmethod
    def _validate_and_normalize_source(cls, v: str | None) -> str | None:
        if v is None:
            return None
        source = str(v).strip().lower()
        if not source:
            logger.warning("Data source identifier is empty.")
            return None
        return source

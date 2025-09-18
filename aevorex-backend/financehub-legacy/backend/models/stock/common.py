# =============================================================================
# === From: common.py ===
# =============================================================================

import logging
from datetime import date as Date, datetime
from typing import Optional, Any, List, Annotated
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    AwareDatetime,
)
from ...core.helpers import _clean_value

# Pydantic v2 compatible strict types
StrictStr = Annotated[str, Field(strict=True)]

# --- Logger Beállítása ---
logger = logging.getLogger("aevorex_finbot.models.stock_common")

# --- Konstansok ---
VALID_SENTIMENT_LABELS = {"bullish", "neutral", "bearish"}


class TickerSentiment(BaseModel):
    """Egy adott tickerhez tartozó hangulati adatokat tárolja."""

    model_config = ConfigDict(extra="ignore", validate_assignment=True)

    symbol: str
    sentiment_score: Optional[float] = Field(
        None, description="Sentiment score (-1 to 1)."
    )
    sentiment_label: Optional[str] = Field(
        None, description="Sentiment label ('bullish', 'neutral', 'bearish')."
    )
    last_updated: Optional[AwareDatetime] = Field(
        None, description="Last update timestamp."
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def validate_and_normalize_ticker(cls, v: Any) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Ticker must be a non-empty string.")
        return v.strip().upper()

    @field_validator("sentiment_label", mode="before")
    @classmethod
    def validate_sentiment_label(cls, v: Any) -> Optional[str]:
        cleaned_v = _clean_value(v)
        if cleaned_v is None:
            return None
        lower_v = str(cleaned_v).lower()
        if lower_v not in VALID_SENTIMENT_LABELS:
            logger.warning(f"Invalid sentiment label '{v}'. Setting to None.")
            return None
        return lower_v


class StockSplitData(BaseModel):
    """Részvényfelaprózási adatokat tartalmaz."""

    execution_date: Date = Field(..., alias="executionDate")
    from_factor: float = Field(..., alias="fromFactor")
    to_factor: float = Field(..., alias="toFactor")


class DividendData(BaseModel):
    """Osztalékadatokat tartalmaz."""

    ex_date: Date = Field(..., alias="exDate")
    payment_date: Date = Field(..., alias="paymentDate")
    record_date: Date = Field(..., alias="recordDate")
    value: float = Field(..., alias="value")
    currency: str = Field(..., alias="currency")


class ErrorResponse(BaseModel):
    """General error message model."""

    error: str = Field(..., description="Error message description.")
    details: Optional[Any] = None


class NewsItem(BaseModel):
    """Model representing a single news item."""

    model_config = ConfigDict(extra="ignore")

    id: Optional[str] = Field(None, description="Unique identifier for the news item.")
    title: Optional[str] = Field(None, description="News item title.")
    publisher: Optional[str] = Field(None, description="Publisher name.")
    link: Optional[str] = Field(
        None, alias="article_url", description="URL to the full article."
    )
    published_utc: Optional[AwareDatetime] = Field(
        None, alias="published_utc", description="Publication timestamp in UTC."
    )
    tickers: List[str] = Field(
        default_factory=list, description="Tickers associated with the news item."
    )
    summary: Optional[str] = Field(
        None, alias="description", description="Short summary of the news item."
    )
    image_url: Optional[str] = Field(
        None, alias="image_url", description="Image URL associated with the news item."
    )

    @field_validator("published_utc", mode="before")
    @classmethod
    def validate_published_date(cls, v: Any) -> AwareDatetime:
        if isinstance(v, (datetime, Date)):
            return v
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        raise ValueError(f"Cannot parse date: {v}")


class StockQuote(BaseModel):
    """
    Represents a real-time stock quote.
    """

    symbol: str
    price: float
    change: float
    change_percent: float
    timestamp: datetime


class ForexQuote(BaseModel):
    """Placeholder model for forex quote data."""

    symbol: str
    rate: float
    timestamp: str

    class Config:
        extra = "allow"

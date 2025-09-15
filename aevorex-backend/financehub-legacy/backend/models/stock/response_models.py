# =============================================================================
# === From: response_models.py ===
# =============================================================================
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from .common import NewsItem
from .fundamentals import CompanyOverview, FinancialsData, EarningsData
from .indicator_models import TechnicalAnalysis


class LatestOHLCV(BaseModel):
    """Contains the latest OHLCV data and changes."""

    c: Optional[float] = Field(None, description="Current or last closing price.")
    h: Optional[float] = Field(None, description="Daily high.")
    low: Optional[float] = Field(None, description="Daily low.")
    o: Optional[float] = Field(None, description="Daily opening price.")
    v: Optional[int] = Field(None, description="Daily volume.")
    pc: Optional[float] = Field(None, description="Previous day closing price.")
    d: Optional[float] = Field(None, description="Change.")
    dp: Optional[float] = Field(None, description="Percentage change.")
    c_timestamp: Optional[datetime] = Field(
        None, description="Timestamp of the 'c' (price) value."
    )


class NewsData(BaseModel):
    """Model containing news items and aggregated sentiment data."""

    items: List[NewsItem] = Field(default_factory=list)
    sentiment_score: Optional[float] = Field(
        None, description="Aggregated sentiment score based on news."
    )
    sentiment_label: Optional[str] = Field(
        None,
        description="Aggregated sentiment label ('bullish', 'neutral', 'bearish').",
    )


class FinBotStockResponse(BaseModel):
    """
    Main unified response model for a specific stock query.
    This model aggregates all relevant data points.
    """

    symbol: str = Field(..., description="Unique symbol of the stock.")
    company_overview: Optional[CompanyOverview] = None
    latest_ohlcv: Optional[LatestOHLCV] = None
    financials: Optional[FinancialsData] = None
    earnings: Optional[EarningsData] = None
    news: Optional[NewsData] = None
    technical_analysis: Optional[TechnicalAnalysis] = None
    # --- Új mezők a kompatibilitásért ---
    request_timestamp_utc: Optional[datetime] = Field(
        None,
        description="UTC timestamp recorded when building the response (for offline / cache validation).",
    )
    data_source_info: Optional[str] = Field(
        None,
        description="Brief meta information about the data source combination used (e.g. 'mixed-sources-parallel').",
    )
    is_data_stale: Optional[bool] = Field(
        None, description="True if the data is stale (e.g. refetch required)."
    )
    history_ohlcv: Optional[list[dict]] = Field(
        None, description="Complete OHLCV time series prepared for charting."
    )
    latest_indicators: Optional[dict[str, float]] = Field(
        None,
        description="Latest technical indicator values as key-value pairs.",
    )

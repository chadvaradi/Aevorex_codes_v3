# =============================================================================
# === From: price_models.py ===
# =============================================================================
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from .common import DividendData, StockSplitData


class ChartDataPoint(BaseModel):
    """Single data point for historical price chart."""

    t: datetime = Field(..., alias="timestamp", description="Timestamp.")
    o: float = Field(..., alias="open", description="Opening price.")
    h: float = Field(..., alias="high", description="High price.")
    low: float = Field(..., alias="low", description="Low price.")
    c: float = Field(..., alias="close", description="Closing price.")
    v: int = Field(..., alias="volume", description="Volume.")


class CompanyPriceHistoryEntry(BaseModel):
    """Contains historical data for a single day."""

    date: str = Field(..., description="Date in 'YYYY-MM-DD' format.")
    o: float = Field(..., description="Opening price.")
    h: float = Field(..., description="High price.")
    low: float = Field(..., description="Low price.")
    c: float = Field(..., description="Closing price.")
    v: int = Field(..., description="Volume.")
    dividends: List[DividendData] = Field(default_factory=list)
    splits: List[StockSplitData] = Field(default_factory=list)

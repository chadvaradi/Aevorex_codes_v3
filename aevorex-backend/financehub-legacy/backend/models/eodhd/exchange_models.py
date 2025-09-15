"""
EODHD Exchange Models - Pydantic v2
===================================

Pydantic v2 models for EODHD exchange data including trading hours.
"""

from typing import Annotated, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class TradingSession(BaseModel):
    """Trading session information (regular, pre-market, after-hours)."""
    
    open: Annotated[str, Field(description="Opening time in HH:MM format")]
    close: Annotated[str, Field(description="Closing time in HH:MM format")]
    timezone: Annotated[str, Field(description="Timezone identifier (e.g., America/New_York)")]
    days: Annotated[List[str], Field(description="Days of the week when this session is active")]


class Holiday(BaseModel):
    """Market holiday information."""
    
    date: Annotated[str, Field(description="Holiday date in YYYY-MM-DD format")]
    name: Annotated[str, Field(description="Holiday name")]
    type: Annotated[str, Field(description="Holiday type: full_day or early_close")]


class TradingHours(BaseModel):
    """Complete trading hours information for an exchange."""
    
    regular: Annotated[TradingSession, Field(description="Regular trading hours")]
    pre_market: Annotated[Optional[TradingSession], Field(description="Pre-market trading hours")]
    after_hours: Annotated[Optional[TradingSession], Field(description="After-hours trading hours")]


class ExchangeHoursResponse(BaseModel):
    """Response model for exchange trading hours endpoint."""
    
    exchange: Annotated[str, Field(description="Exchange code")]
    trading_hours: Annotated[TradingHours, Field(description="Trading hours information")]
    holidays: Annotated[List[Holiday], Field(description="List of market holidays")]
    metadata: Annotated[dict, Field(description="Response metadata")]


class ExchangeInfo(BaseModel):
    """Basic exchange information."""
    
    name: Annotated[str, Field(description="Exchange name")]
    code: Annotated[str, Field(description="Exchange code")]
    country: Annotated[str, Field(description="Country")]
    currency: Annotated[str, Field(description="Currency code")]
    timezone: Annotated[str, Field(description="Exchange timezone")]


class ExchangeListResponse(BaseModel):
    """Response model for exchange list endpoint."""
    
    exchanges: Annotated[List[ExchangeInfo], Field(description="List of exchanges")]
    total: Annotated[int, Field(description="Total number of exchanges")]
    metadata: Annotated[dict, Field(description="Response metadata")]



"""
Consolidated Macro Models
========================

All Pydantic models for macroeconomic data endpoints.
Consolidated from backend/models/macro_models.py and backend/api/endpoints/macro/ecb/models.py
to maintain clean architecture and avoid duplication.
"""

from datetime import date
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field
from enum import Enum

# =============================================================================
# Forex Models (from original macro_models.py)
# =============================================================================


class ForexSnapshot(BaseModel):
    """Represents a snapshot of a forex pair rate."""

    pair: str = Field(..., description="The forex pair symbol.", example="EURUSD")
    rate: float = Field(..., description="The current exchange rate.", example=1.0855)
    timestamp: str = Field(
        ..., description="The timestamp of the data.", example="2023-10-27T10:00:00Z"
    )


class ForexPairsResponse(BaseModel):
    """Response model for available forex pairs."""

    pairs: Dict[str, Any] = Field(
        ..., description="Dictionary of available forex pairs and their details."
    )


# =============================================================================
# ECB Enums (from ECB models.py)
# =============================================================================


class ECBPeriod(str, Enum):
    """Valid ECB data periods."""

    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"
    # Short-form aliases (frontend-friendly)
    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"


class ECBCurrency(str, Enum):
    """Supported currencies for ECB FX rates."""

    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    CNY = "CNY"
    CAD = "CAD"
    AUD = "AUD"
    SEK = "SEK"
    NOK = "NOK"
    DKK = "DKK"


class ECBCountry(str, Enum):
    """Supported countries for ECB government bonds."""

    GERMANY = "DE"
    FRANCE = "FR"
    ITALY = "IT"
    SPAIN = "ES"
    NETHERLANDS = "NL"
    AUSTRIA = "AT"
    BELGIUM = "BE"
    FINLAND = "FI"
    IRELAND = "IE"
    PORTUGAL = "PT"


class ECBMaturity(str, Enum):
    """Supported maturities for ECB yield curves."""

    ONE_YEAR = "1Y"
    TWO_YEAR = "2Y"
    THREE_YEAR = "3Y"
    FIVE_YEAR = "5Y"
    TEN_YEAR = "10Y"
    TWENTY_YEAR = "20Y"
    THIRTY_YEAR = "30Y"


# =============================================================================
# Core ECB Data Models
# =============================================================================


class ECBDataPoint(BaseModel):
    """Single ECB data point."""

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    value: float = Field(..., description="Data value")


class ECBMetadata(BaseModel):
    """Metadata model for ECB responses."""

    total_records: int = Field(..., description="Total number of records")
    start_date: str = Field(..., description="Data start date")
    end_date: str = Field(..., description="Data end date")
    last_updated: Optional[str] = Field(None, description="Last update timestamp")
    data_source: str = Field("ECB SDMX API", description="Data source")
    cache_hit: bool = Field(False, description="Whether data was served from cache")


# =============================================================================
# ECB Response Models
# =============================================================================


class ECBPolicyRatesResponse(BaseModel):
    """Response model for ECB policy rates."""

    success: bool = Field(True, description="Request success status")
    data: Dict[str, Dict[str, float]] = Field(
        ..., description="Policy rates data by date and rate type"
    )
    metadata: Dict[str, Union[str, int]] = Field(
        default_factory=dict, description="Response metadata"
    )


class ECBYieldCurveResponse(BaseModel):
    """Response model for ECB yield curve."""

    success: bool = Field(True, description="Request success status")
    data: Dict[str, Dict[str, float]] = Field(
        ..., description="Yield curve data by date and maturity"
    )
    metadata: Dict[str, Union[str, int]] = Field(
        default_factory=dict, description="Response metadata"
    )


class ECBFXRatesResponse(BaseModel):
    """Response model for ECB FX rates."""

    success: bool = Field(True, description="Request success status")
    data: Dict[str, Dict[str, float]] = Field(
        ..., description="FX rates data by date and currency"
    )
    metadata: Dict[str, Union[str, int]] = Field(
        default_factory=dict, description="Response metadata"
    )


class ECBComprehensiveResponse(BaseModel):
    """Response model for comprehensive ECB data."""

    success: bool = Field(True, description="Request success status")
    data: Dict[str, Dict[str, Dict[str, float]]] = Field(
        ..., description="Comprehensive economic data by category"
    )
    metadata: Dict[str, Union[str, int]] = Field(
        default_factory=dict, description="Response metadata"
    )


class ECBBOPResponse(BaseModel):
    """Response model for ECB Balance of Payments data."""

    success: bool = Field(True, description="Request success status")
    data: Dict[str, Dict[str, float]] = Field(
        ..., description="BOP data by date and component"
    )
    metadata: Dict[str, Union[str, int]] = Field(
        default_factory=dict, description="Response metadata"
    )


class ECBSTSResponse(BaseModel):
    """Response model for ECB Short-term Statistics data."""

    success: bool = Field(True, description="Request success status")
    data: Dict[str, Dict[str, float]] = Field(
        ..., description="STS data by date and indicator"
    )
    metadata: Dict[str, Union[str, int]] = Field(
        default_factory=dict, description="Response metadata"
    )


class ECBErrorResponse(BaseModel):
    """Error response model."""

    success: bool = Field(False, description="Request success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")


class ECBHealthResponse(BaseModel):
    """Health check response model."""

    success: bool = Field(True, description="Service health status")
    service: str = Field("ECB SDMX API", description="Service name")
    timestamp: str = Field(..., description="Response timestamp")
    version: str = Field("1.0", description="API version")


# =============================================================================
# ECB Query Parameter Models
# =============================================================================


class ECBPeriodQuery(BaseModel):
    """Query parameters for ECB period-based requests."""

    period: Optional[ECBPeriod] = Field(ECBPeriod.MONTHLY, description="Data period")
    start_date: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")


class ECBFXQuery(BaseModel):
    """Query parameters for ECB FX rates."""

    currencies: Optional[List[ECBCurrency]] = Field(
        default=[ECBCurrency.USD, ECBCurrency.GBP, ECBCurrency.JPY, ECBCurrency.CHF],
        description="List of currencies to fetch",
    )
    start_date: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")


class ECBYieldCurveQuery(BaseModel):
    """Query parameters for ECB yield curve."""

    countries: Optional[List[ECBCountry]] = Field(
        default=[
            ECBCountry.GERMANY,
            ECBCountry.FRANCE,
            ECBCountry.ITALY,
            ECBCountry.SPAIN,
        ],
        description="List of countries to fetch",
    )
    maturities: Optional[List[ECBMaturity]] = Field(
        default=[
            ECBMaturity.ONE_YEAR,
            ECBMaturity.TWO_YEAR,
            ECBMaturity.FIVE_YEAR,
            ECBMaturity.TEN_YEAR,
        ],
        description="List of maturities to fetch",
    )
    start_date: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")


class ECBBOPQuery(BaseModel):
    """Query parameters for ECB Balance of Payments."""

    components: Optional[List[str]] = Field(
        default=[
            "current_account",
            "trade_balance",
            "services_balance",
            "income_balance",
            "capital_account",
            "direct_investment",
            "portfolio_investment",
            "financial_derivatives",
        ],
        description="List of BOP components to fetch",
    )
    start_date: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")


class ECBSTSQuery(BaseModel):
    """Query parameters for ECB Short-term Statistics."""

    indicators: Optional[List[str]] = Field(
        default=[
            "industrial_production",
            "retail_sales",
            "construction_output",
            "unemployment_rate",
            "employment_rate",
            "business_confidence",
            "consumer_confidence",
            "capacity_utilization",
        ],
        description="List of STS indicators to fetch",
    )
    start_date: Optional[date] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date (YYYY-MM-DD)")


# =============================================================================
# BUBOR Models (new additions for clean architecture)
# =============================================================================


class BuborResponse(BaseModel):
    """Response model for BUBOR rates."""

    status: str = Field(..., description="Response status")
    metadata: Dict[str, Any] = Field(
        ..., description="Metadata including source and timestamp"
    )
    rates: Dict[str, Dict[str, float]] = Field(
        ..., description="BUBOR rates data by date and tenor"
    )
    message: str = Field(..., description="Response message")


# =============================================================================
# Yield Curve Models (new additions for clean architecture)
# =============================================================================


class YieldCurveResponse(BaseModel):
    """Response model for yield curve data."""

    status: str = Field(..., description="Response status")
    source: str = Field(..., description="Data source (ecb or ust)")
    curve: Dict[str, float] = Field(..., description="Yield curve data by maturity")
    date: str = Field(..., description="Data date")
    message: Optional[str] = Field(None, description="Optional message")
    error: Optional[str] = Field(None, description="Optional error details")


# =============================================================================
# Generic Macro Models (new additions for clean architecture)
# =============================================================================


class MacroDataResponse(BaseModel):
    """Generic response model for macro data."""

    status: str = Field(..., description="Response status")
    data: Dict[str, Any] = Field(..., description="Macro data")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Response metadata"
    )
    message: Optional[str] = Field(None, description="Optional message")


class MacroErrorResponse(BaseModel):
    """Generic error response model for macro endpoints."""

    status: str = Field("error", description="Response status")
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )

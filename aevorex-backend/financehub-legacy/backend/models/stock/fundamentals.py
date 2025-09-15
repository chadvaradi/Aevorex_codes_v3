import logging
from datetime import date as Date
from typing import Optional, Any, List, Dict, Annotated
from pydantic import (
    BaseModel,
    Field,
    field_validator,
    ConfigDict,
    ValidationInfo,
)
from ...core.helpers import (
    parse_optional_float,
    parse_optional_int,
    _validate_date_string,
)

# Pydantic v2 compatible strict types
StrictFloat = Annotated[float, Field(strict=True)]
StrictInt = Annotated[int, Field(strict=True)]
StrictStr = Annotated[str, Field(strict=True)]
from .common import TickerSentiment

# --- Logger ---
logger = logging.getLogger("aevorex_finbot.models.stock_fundamentals")

# StockSplitData and DividendData are now imported from .common


class RatingPoint(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True, extra="ignore", validate_assignment=True
    )
    symbol: str = Field(..., description="Stock symbol (uppercase).")
    date: Date = Field(..., description="Rating date.")
    rating_score: Optional[int] = Field(None, alias="ratingScore", ge=1, le=5)
    rating_recommendation: Optional[str] = Field(
        None, alias="ratingRecommendation"
    )

    @field_validator("symbol", mode="before")
    @classmethod
    def validate_and_normalize_symbol(cls, v: Any) -> str:
        return TickerSentiment.validate_and_normalize_ticker(v)

    @field_validator("date", mode="before")
    @classmethod
    def validate_generic_date(cls, v: Any, info: ValidationInfo) -> Date:
        date_obj = _validate_date_string(v, f"{cls.__name__}.{info.field_name}")
        if date_obj is None:
            raise ValueError(f"Required date field '{info.field_name}' cannot be None.")
        return date_obj


class CompanyOverview(BaseModel):
    model_config = ConfigDict(
        extra="ignore", validate_assignment=True, populate_by_name=True
    )
    symbol: str
    asset_type: Optional[str] = Field(None, alias="AssetType")
    name: Optional[str] = Field(None, alias="Name")
    description: Optional[str] = Field(None, alias="Description")
    country: Optional[str] = Field(None, alias="Country")
    sector: Optional[str] = Field(None, alias="Sector")
    industry: Optional[str] = Field(None, alias="Industry")
    market_cap: Optional[float] = Field(None, alias="MarketCapitalization")
    pe_ratio: Optional[float] = Field(None, alias="PERatio")
    beta: Optional[float] = Field(None, alias="Beta")
    shares_outstanding: Optional[int] = Field(None, alias="SharesOutstanding")

    @field_validator("market_cap", "pe_ratio", "beta", mode="before")
    @classmethod
    def parse_float(cls, v: Any) -> Optional[float]:
        return parse_optional_float(v)

    @field_validator("shares_outstanding", mode="before")
    @classmethod
    def parse_int(cls, v: Any) -> Optional[int]:
        return parse_optional_int(v)


class FinancialsData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    annual_reports: Optional[List[Dict[str, Any]]] = Field(None, alias="annualReports")
    quarterly_reports: Optional[List[Dict[str, Any]]] = Field(
        None, alias="quarterlyReports"
    )
    # New optional pandas DataFrame-like dicts used by AI prompt generators
    balance_sheet: Optional[Any] = None  # type: ignore
    income_statement: Optional[Any] = None  # type: ignore
    cash_flow: Optional[Any] = None  # type: ignore


class EarningsPeriodData(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)
    date: Optional[Date] = Field(None, description="Period end date.")
    eps_actual: Optional[float] = Field(None, alias="epsActual")
    eps_estimate: Optional[float] = Field(None, alias="epsEstimate")
    revenue_actual: Optional[int] = Field(None, alias="revenueActual")
    revenue_estimate: Optional[int] = Field(None, alias="revenueEstimate")

    @field_validator("date", mode="before")
    @classmethod
    def validate_date(cls, v: Any) -> Optional[Date]:
        if v:
            return _validate_date_string(v, "EarningsPeriodData.date")
        return None

    @field_validator("eps_actual", "eps_estimate", mode="before")
    @classmethod
    def parse_float(cls, v: Any) -> Optional[float]:
        return parse_optional_float(v)

    @field_validator("revenue_actual", "revenue_estimate", mode="before")
    @classmethod
    def parse_int(cls, v: Any) -> Optional[int]:
        return parse_optional_int(v)


class EarningsData(BaseModel):
    model_config = ConfigDict(extra="ignore")
    annual_earnings: Optional[List[EarningsPeriodData]] = Field(
        None, alias="annualEarnings"
    )
    quarterly_earnings: Optional[List[EarningsPeriodData]] = Field(
        None, alias="quarterlyEarnings"
    )
    history: Optional[List[EarningsPeriodData]] = None

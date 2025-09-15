"""
EODHD Stock API Response Models
"""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class ExchangeTicker(BaseModel):
    """Model for exchange ticker data from EODHD API"""
    
    code: Optional[str] = Field(None, alias="Code", description="Ticker symbol")
    name: Optional[str] = Field(None, alias="Name", description="Company or instrument name")
    country: Optional[str] = Field(None, alias="Country", description="Country of listing")
    exchange: Optional[str] = Field(None, alias="Exchange", description="Exchange code")
    currency: Optional[str] = Field(None, alias="Currency", description="Trading currency")
    type: Optional[str] = Field(None, alias="Type", description="Type of asset (e.g. Common Stock, ETF, Fund)")
    isin: Optional[str] = Field(None, alias="Isin", description="International Securities Identification Number")
    
    model_config = ConfigDict(
        populate_by_name=True,

        str_strip_whitespace=True
    )
    
    @classmethod
    def from_eodhd_data(cls, data: dict) -> "ExchangeTicker":
        """Create ExchangeTicker from EODHD API data with proper field mapping"""
        return cls(
            code=data.get("Code"),
            name=data.get("Name"),
            country=data.get("Country"),
            exchange=data.get("Exchange"),
            currency=data.get("Currency"),
            type=data.get("Type"),
            isin=data.get("Isin")
        )


class StockEODData(BaseModel):
    """Model for End of Day stock data from EODHD API"""
    
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="Highest price")
    low: Optional[float] = Field(None, description="Lowest price")
    close: Optional[float] = Field(None, description="Closing price")
    adjusted_close: Optional[float] = Field(None, alias="adjusted_close", description="Adjusted closing price")
    volume: Optional[int] = Field(None, description="Trading volume")


class StockIntradayData(BaseModel):
    """Model for intraday stock data from EODHD API"""
    
    datetime: str = Field(..., description="Datetime in YYYY-MM-DD HH:MM:SS format")
    open: Optional[float] = Field(None, description="Opening price")
    high: Optional[float] = Field(None, description="Highest price")
    low: Optional[float] = Field(None, description="Lowest price")
    close: Optional[float] = Field(None, description="Closing price")
    volume: Optional[int] = Field(None, description="Trading volume")


class StockSplitData(BaseModel):
    """Model for stock split data from EODHD API"""
    
    date: str = Field(..., description="Split date in YYYY-MM-DD format")
    split_ratio: Optional[str] = Field(None, description="Split ratio (e.g. '2:1')")
    from_factor: Optional[float] = Field(None, description="From factor")
    to_factor: Optional[float] = Field(None, description="To factor")


class StockDividendData(BaseModel):
    """Model for stock dividend data from EODHD API"""
    
    date: str = Field(..., description="Dividend date in YYYY-MM-DD format")
    value: Optional[float] = Field(None, description="Dividend value")
    currency: Optional[str] = Field(None, description="Currency code")


# Response wrapper models
class ExchangeTickersResponse(BaseModel):
    """Response model for exchange tickers endpoint"""
    
    data: List[ExchangeTicker] = Field(..., description="List of tickers")
    metadata: Optional[dict] = Field(None, description="Response metadata")


class StockEODResponse(BaseModel):
    """Response model for EOD stock data"""
    
    data: List[StockEODData] = Field(..., description="List of EOD data points")
    metadata: Optional[dict] = Field(None, description="Response metadata")


class StockIntradayResponse(BaseModel):
    """Response model for intraday stock data"""
    
    data: List[StockIntradayData] = Field(..., description="List of intraday data points")
    metadata: Optional[dict] = Field(None, description="Response metadata")


class StockSplitsResponse(BaseModel):
    """Response model for stock splits data"""
    
    data: List[StockSplitData] = Field(..., description="List of split events")
    metadata: Optional[dict] = Field(None, description="Response metadata")


class StockDividendsResponse(BaseModel):
    """Response model for stock dividends data"""
    
    data: List[StockDividendData] = Field(..., description="List of dividend payments")
    metadata: Optional[dict] = Field(None, description="Response metadata")


class CryptoTicker(BaseModel):
    """Model for cryptocurrency ticker data from EODHD API"""
    
    code: Optional[str] = Field(None, alias="Code", description="Cryptocurrency symbol")
    name: Optional[str] = Field(None, alias="Name", description="Cryptocurrency name")
    country: Optional[str] = Field(None, alias="Country", description="Country of origin")
    exchange: Optional[str] = Field(None, alias="Exchange", description="Exchange code")
    currency: Optional[str] = Field(None, alias="Currency", description="Trading currency")
    type: Optional[str] = Field(None, alias="Type", description="Type of asset")
    isin: Optional[str] = Field(None, alias="Isin", description="International Securities Identification Number")
    
    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )
    
    @classmethod
    def from_eodhd_data(cls, data: dict) -> "CryptoTicker":
        """Create CryptoTicker from EODHD API data with proper field mapping"""
        return cls(
            code=data.get("Code"),
            name=data.get("Name"),
            country=data.get("Country"),
            exchange=data.get("Exchange"),
            currency=data.get("Currency"),
            type=data.get("Type"),
            isin=data.get("Isin")
        )

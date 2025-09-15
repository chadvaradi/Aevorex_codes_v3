"""
This package exports the core Pydantic models for stock data.

By explicitly defining `__all__`, we provide a clear public API
for this package and avoid issues with linters and wildcard imports.
"""

from .common import (
    DividendData,
    ErrorResponse,
    ForexQuote,
    NewsItem,
    StockSplitData,
    TickerSentiment,
)
from .fundamentals import (
    CompanyOverview,
    EarningsData,
    EarningsPeriodData,
    FinancialsData,
    RatingPoint,
)
from .financials import (
    FinancialStatementItem,
    FinancialStatementData,
    FinancialStatementDataContainer,
)
from .indicator_models import (
    BBandsSet,
    EMASet,
    IndicatorHistory,
    IndicatorPoint,
    LatestIndicators,
    MACDHistPoint,
    MACDSeries,
    RSISeries,
    SMASet,
    STOCHPoint,
    STOCHSeries,
    TechnicalAnalysis,
    VolumePoint,
    VolumeSeries,
    VolumeSMASeries,
)
from .price_models import (
    ChartDataPoint,
    CompanyPriceHistoryEntry,
)
from .response_models import (
    FinBotStockResponse,
    LatestOHLCV,
    NewsData,
)
from .technicals import (
    EmaCross,
    IndicatorMetadata,
    IndicatorType,
)

__all__ = [
    # from .common
    "TickerSentiment",
    "StockSplitData",
    "DividendData",
    "ErrorResponse",
    "ForexQuote",
    "NewsItem",
    # from .fundamentals
    "CompanyOverview",
    "FinancialsData",
    "EarningsData",
    "RatingPoint",
    "EarningsPeriodData",
    # from .financials
    "FinancialStatementItem",
    "FinancialStatementData",
    "FinancialStatementDataContainer",
    # from .indicator_models
    "TechnicalAnalysis",
    "LatestIndicators",
    "IndicatorHistory",
    "IndicatorPoint",
    "VolumePoint",
    "MACDHistPoint",
    "STOCHPoint",
    "SMASet",
    "EMASet",
    "BBandsSet",
    "RSISeries",
    "VolumeSeries",
    "MACDSeries",
    "STOCHSeries",
    "VolumeSMASeries",
    # from .price_models
    "ChartDataPoint",
    "CompanyPriceHistoryEntry",
    # from .response_models
    "FinBotStockResponse",
    "LatestOHLCV",
    "NewsData",
    # from .technicals
    "EmaCross",
    "IndicatorMetadata",
    "IndicatorType",
]


class StockQuote:
    pass

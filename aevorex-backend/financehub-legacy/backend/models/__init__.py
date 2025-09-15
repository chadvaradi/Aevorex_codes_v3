"""
This package aggregates all Pydantic models for the FinanceHub backend.

It re-exports models from the .stock and .chat submodules to provide a
unified namespace for the rest of the application, simplifying imports.
"""

# Direct imports from the refactored stock model files
from .stock.common import (
    TickerSentiment,
    StockSplitData,
    DividendData,
    ErrorResponse,
    NewsItem,
)
from .stock.fundamentals import (
    RatingPoint,
    CompanyOverview,
    FinancialsData,
    EarningsPeriodData,
    EarningsData,
)
from .stock.indicator_models import (
    IndicatorPoint,
    VolumePoint,
    MACDHistPoint,
    STOCHPoint,
    SMASet,
    EMASet,
    BBandsSet,
    RSISeries,
    VolumeSeries,
    MACDSeries,
    STOCHSeries,
    IndicatorHistory,
    TechnicalAnalysis,
    LatestIndicators,
)
from .stock.price_models import (
    CompanyPriceHistoryEntry,
)
from .stock.response_models import LatestOHLCV, NewsData, FinBotStockResponse
# from backend.models.chat import (
#     ChatRole, ChatMessage, ChatSession
# )

# Dynamically build the public API of the entire models package
__all__ = [
    # from .stock
    "TickerSentiment",
    "StockSplitData",
    "DividendData",
    "ErrorResponse",
    "NewsItem",
    "RatingPoint",
    "CompanyOverview",
    "FinancialsData",
    "EarningsPeriodData",
    "EarningsData",
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
    "IndicatorHistory",
    "TechnicalAnalysis",
    "LatestIndicators",
    "CompanyPriceHistoryEntry",
    "LatestOHLCV",
    "NewsData",
    "FinBotStockResponse",
    # from .chat
    # "ChatRole", "ChatMessage", "ChatSession",
]

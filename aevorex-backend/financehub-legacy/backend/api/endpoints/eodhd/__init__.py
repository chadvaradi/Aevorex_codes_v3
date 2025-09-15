"""
EODHD API endpoints package.

Provides EODHD (End of Day Historical Data) API integration endpoints.
"""

from .crypto_router import router as crypto_router
from .stock_router import router as stock_router
from .technical_router import router as technical_router
from .news_router import router as news_router
from .forex_router import router as forex_router
from .exchanges_router import router as exchanges_router
from .intraday_router import router as intraday_router
from .macro_router import router as macro_router
from .screener_router import router as screener_router

__all__ = [
    "crypto_router",
    "stock_router", 
    "technical_router",
    "news_router",
    "forex_router",
    "exchanges_router",
    "intraday_router",
    "macro_router",
    "screener_router"
]

"""TradingView UDF-compatible API endpoints for official ECB/MNB data feeds."""

from fastapi import APIRouter

from .symbols import router as symbols_router
from .bars import router as bars_router

tradingview_router = APIRouter(prefix="/tv", tags=["TradingView UDF"])

tradingview_router.include_router(symbols_router)
tradingview_router.include_router(bars_router)

__all__ = ["tradingview_router"]

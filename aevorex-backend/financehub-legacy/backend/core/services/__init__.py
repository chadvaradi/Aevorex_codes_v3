"""
Stock Service Package - Modular Architecture

This package replaces the monolithic stock_service.py (3,774 LOC)
with a modular, maintainable architecture following the 160 LOC rule.

Modules:
- orchestrator.py: Main orchestration logic
- fundamentals_service.py: Fundamentals data processing
- technical_service.py: Technical analysis and indicators
- news_service.py: News data processing
- chart_service.py: OHLCV chart data processing
- response_builder.py: Response object construction
- data_fetcher.py: Parallel data fetching
- cache_manager.py: Caching logic
"""

# ---------------------------------------------------------------------------
# NumPy >=2.0 removed the public ``NaN`` alias that several third-party
# libraries (e.g. ``pandas_ta``) still import via ``from numpy import NaN``.
# Creating the alias **once** at package import time guarantees that every
# subsequent submodule import sees the attribute and prevents runtime
# ``ImportError: cannot import name 'NaN' from numpy``.
# ---------------------------------------------------------------------------
import numpy as _np  # noqa: N813  # keep underscore prefix internal

if not hasattr(_np, "NaN"):
    _np.NaN = _np.nan  # type: ignore[attr-defined]

# Legacy import compatibility layer **must** be registered before the remaining imports
import importlib
import sys as _sys

_legacy_modules = {
    "backend.core.services.macro_service": "backend.core.services.macro.macro_service",
    "backend.core.services.chart_service": "backend.core.services.stock.chart_service",
    "backend.core.services.technical_service": "backend.core.services.stock.technical_service",
    "backend.core.services.news_service": "backend.core.services.stock.news_service",
    "backend.core.services.news_fetcher": "backend.core.services.stock.news_fetcher",
    "backend.core.services.fundamentals_service": "backend.core.services.stock.fundamentals_service",
    "backend.core.services.fundamentals_processors": "backend.core.services.stock.fundamentals_processors",
    "backend.core.services.technical_processors": "backend.core.services.stock.technical_processors",
    "backend.core.services.chart_data_handler": "backend.core.services.stock.chart_data_handler",
    "backend.core.services.orchestrator": "backend.core.orchestrator",
}
for _legacy, _target in _legacy_modules.items():
    if _legacy not in _sys.modules:
        try:
            _sys.modules[_legacy] = importlib.import_module(_target)
        except ImportError:
            pass

# -----------------------------------------------------------------------------
# Primary services imports (after alias map to prevent circular errors)
# -----------------------------------------------------------------------------
from ..orchestrator import StockOrchestrator
from backend.core.services.stock.fundamentals_service import FundamentalsService
from backend.core.services.stock.news_service import NewsService
from backend.core.services.shared.response_builder import (
    build_stock_response_from_parallel_data,
)
from backend.core.services.shared.response_helpers import (
    process_ohlcv_dataframe,
    process_technical_indicators,
)
from backend.core.services.stock.technical_service import TechnicalService
from backend.core.services.stock.chart_service import ChartService

__all__ = [
    "StockOrchestrator",
    "FundamentalsService",
    "TechnicalService",
    "NewsService",
    "ChartService",
    "build_stock_response_from_parallel_data",
    "process_ohlcv_dataframe",
    "process_technical_indicators",
]

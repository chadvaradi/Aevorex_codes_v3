"""
Fundamentals API Router

Main entry point for fundamental analysis endpoints.
Provides comprehensive stock fundamental data including company overview,
financial statements, ratios, and earnings information.
"""

from fastapi import APIRouter

# Create main fundamentals router
router = APIRouter()

# Include handler routers
from .handlers.overview_handler import router as overview_router
from .handlers.financials_handler import router as financials_router
from .handlers.ratios_handler import router as ratios_router
from .handlers.earnings_handler import router as earnings_router

router.include_router(overview_router)
router.include_router(financials_router)
router.include_router(ratios_router)
router.include_router(earnings_router)

__all__ = ["router"]

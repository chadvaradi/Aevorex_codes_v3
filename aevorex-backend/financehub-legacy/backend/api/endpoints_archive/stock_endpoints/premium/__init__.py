"""
Premium Endpoints Module
Aggregates all premium feature endpoints under the /premium prefix.
"""

from fastapi import APIRouter

# Routers
from .ai_summary.router import router as ai_summary_router
from .technical_analysis import technical_analysis_router

premium_router = APIRouter(prefix="/premium")

# Include premium feature routers
premium_router.include_router(ai_summary_router)
# Avoid double prefix – router already has prefix "/technical-analysis"
premium_router.include_router(technical_analysis_router)

# Re-export for main stock_router import
router = premium_router

# Public API for explicit imports
__all__ = [
    "router",
    "ai_summary_router",
    "technical_analysis_router",
]

"""
ECB Main Router
==============

Main router that combines unified ECB dataflows with special endpoints.
Clean, maintainable structure with no legacy code.
"""

from fastapi import APIRouter

# Unified configuration-driven router for standard ECB dataflows
from .ecb_unified_router import router as unified_router

# Special endpoints with custom business logic
from .specials.rates_router import rates_router
from .specials.yield_curve_router import yield_curve_router
from .specials.sts_router import router as sts_router
from .specials.fx_router import router as fx_router
from .specials.comprehensive_router import comprehensive_router
from .specials.bop_router import router as bop_router
from .specials.sec_router import router as sec_router

# Create main ECB router
router = APIRouter(prefix="/ecb", tags=["ECB", "European Central Bank"])

# Include unified router for standard dataflows
router.include_router(unified_router)

# Include special routers
router.include_router(rates_router)
router.include_router(yield_curve_router)
router.include_router(sts_router)
router.include_router(fx_router)
router.include_router(comprehensive_router)
router.include_router(bop_router)
router.include_router(sec_router)


# Lightweight policy-notes placeholder to avoid 404 in UI tooltips
@router.get("/policy-notes", tags=["ECB"], summary="Policy notes (placeholder)")
async def policy_notes_placeholder():
    return {
        "status": "success",
        "data": [
            {
                "date": "2025-01-08",
                "note": "ECB policy notes service not configured in dev; this is a placeholder.",
                "source": "ecb",
                "relevance_score": 0.7,
            }
        ],
    }

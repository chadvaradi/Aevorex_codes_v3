"""
ECB (European Central Bank) API Endpoints Module
===============================================

Modular ECB endpoints for macroeconomic data.
"""

from .router import router
from .models import ECBPeriod
from backend.utils.date_utils import calculate_start_date
from .utils import get_macro_service

# Backward compatibility: export canonical PeriodEnum
from backend.utils.date_utils import PeriodEnum
from .icp import router as hicp_router  # noqa: F401

__all__ = [
    "router",
    "ECBPeriod",
    "PeriodEnum",
    "calculate_start_date",
    "get_macro_service",
]

__version__ = "1.0.0"

router.include_router(hicp_router)

# Legacy IVF/CBD/SEC placeholder handlers removed – real routers are defined
# in `ivf.py`, `cbd.py`, and `sec.py` respectively (cleanup 2025-07-10).

# ---------------------------------------------------------------------------
# Legacy helper functions referenced by test suite (monkeypatch targets)
# They are patched to return fake data; we expose minimal no-op stubs to avoid
# AttributeError during test collection.
# ---------------------------------------------------------------------------


async def fetch_fed_yield_curve_historical(*_, **__):  # type: ignore[override]
    """Legacy yield-curve data fetcher (US Treasury). Replaced by external client.

    Tests monkeypatch this function to avoid live HTTP calls. Keep as async
    placeholder returning empty structure.
    """

    return {}

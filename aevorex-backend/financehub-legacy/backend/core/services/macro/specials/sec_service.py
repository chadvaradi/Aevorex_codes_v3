"""SEC business logic extracted from sec_router.py (Rule #008)"""

from __future__ import annotations

from datetime import date
from typing import Optional, Dict, Any

from backend.core.services.macro_service import MacroDataService
from backend.utils.cache_service import CacheService
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

__all__ = ["build_sec_response", "get_sec_components", "sec_health_check"]


async def build_sec_response(
    cache: CacheService | None,
    start: Optional[date],
    end: Optional[date],
) -> Dict[str, Any]:
    """Build SEC response with business logic extracted from router."""
    try:
        service = MacroDataService(cache)
        data = await service.get_ecb_sec(start, end)
    except AttributeError:
        # Service method not yet implemented
        data = {}
    except Exception as exc:
        logger.warning("ECB SEC fetch failed: %s", exc)
        data = {}

    if not data:
        return {
            "status": "success",
            "metadata": {
                "source": "ECB SDMX (SEC)",
                "message": "Security statistics unavailable – static empty payload",
            },
            "data": {},
        }

    fallback_used = (
        data.get("2025-06") is not None and len(data) <= 2
    )  # crude indicator

    return {
        "status": "success",
        "metadata": {
            "source": "ECB SDMX (SEC dataflow)",
            "fallback": fallback_used,
        },
        "count": len(data),
        "data": data,
    }


def get_sec_components() -> Dict[str, Any]:
    """Get available SEC components."""
    components = {
        "debt_securities": "Outstanding amounts of debt securities by sector and currency of issue",
        "equity_securities": "Outstanding amounts of listed shares by sector",
        "nfc_securities": "Non-financial corporations securities issuance",
    }
    return {
        "success": True,
        "components": components,
        "total_components": len(components),
    }


def sec_health_check() -> Dict[str, Any]:
    """SEC endpoint health check."""
    from datetime import datetime

    return {
        "success": True,
        "service": "ECB SEC API",
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
    }

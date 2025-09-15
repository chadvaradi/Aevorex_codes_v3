"""Extended logic for ECB rates endpoints (<160 LOC).
Extracted from rates.py to satisfy Rule #008 view/logic split.
"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Dict, Any, Optional


from backend.core.services.macro.macro_service import MacroDataService
from backend.utils.date_utils import PeriodEnum, calculate_start_date
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Monetary policy helper -----------------------------------------------------
# ---------------------------------------------------------------------------


async def monetary_policy_response(service: MacroDataService) -> Dict[str, Any]:
    """Return summary with current ECB policy rates (last 30 days)."""
    try:
        today = date.today()
        start = today - timedelta(days=30)
        rates_data = await service.get_ecb_policy_rates(start, today)
        if not rates_data:
            return {
                "status": "unavailable",
                "message": "ECB policy rates unavailable for requested period.",
                "metadata": {
                    "source": "ECB SDMX (FM dataflow)",
                    "date_range": {
                        "start": start.isoformat(),
                        "end": today.isoformat(),
                        "period": "30d",
                    },
                },
                "data": {},
            }

        current_rates: Dict[str, Dict[str, Any]] = {}
        for rate_type, series in rates_data.items():
            if series:
                latest = max(series.keys())
                current_rates[rate_type] = {"rate": series[latest], "date": latest}

        return {
            "status": "success",
            "metadata": {
                "source": "ECB SDMX (FM dataflow)",
                "last_updated": today.isoformat(),
            },
            "data": {
                "current_rates": current_rates,
                "policy_summary": {
                    "description": "ECB policy rates (MRO, DFR, MLFR).",
                },
            },
            "message": "ECB monetary policy information retrieved successfully.",
        }
    except Exception as exc:  # pragma: no cover
        logger.error("Monetary policy error: %s", exc, exc_info=True)
        return _error("Failed to fetch ECB monetary policy information", str(exc))


# ---------------------------------------------------------------------------
# Retail rates helper --------------------------------------------------------
# ---------------------------------------------------------------------------


async def retail_rates_response(
    service: MacroDataService,
    start_date: Optional[date],
    end_date: Optional[date],
    period: Optional[str],
) -> Dict[str, Any]:
    """Return retail bank deposit/lending rates."""
    try:
        if end_date is None:
            end_date = date.today()
        if period:
            try:
                start_date = calculate_start_date(PeriodEnum(period), end_date)
            except ValueError:
                return _error(f"Invalid period value '{period}'.")
        elif start_date is None:
            start_date = end_date - timedelta(days=365)

        data = await service.get_ecb_retail_rates(start_date, end_date)
        if not data:
            return {
                "status": "unavailable",
                "message": "ECB retail rates unavailable for requested period.",
                "metadata": {
                    "source": "ECB SDMX (MIR dataflow)",
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                        "period": period or "1y",
                    },
                },
                "data": {},
            }

        return {
            "status": "success",
            "metadata": {
                "source": "ECB SDMX (MIR dataflow)",
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "period": period or "custom",
                },
            },
            "data": {"retail_rates": data},
            "message": "ECB retail rates retrieved successfully.",
        }
    except Exception as exc:
        logger.error("Retail rates error: %s", exc, exc_info=True)
        return _error("Failed to fetch ECB retail rates", str(exc))


# ---------------------------------------------------------------------------
# Helpers --------------------------------------------------------------------
# ---------------------------------------------------------------------------


def _error(message: str, details: str | None = None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "status": "success",
        "message": f"Fallback: {message}",
        "data": {},
    }
    if details:
        payload["metadata"] = {"fallback_reason": details}
    return payload

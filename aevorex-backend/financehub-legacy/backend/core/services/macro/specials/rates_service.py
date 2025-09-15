"""
Rates Logic (extracted from rates.py)
------------------------------------
Helper functions to fetch ECB policy rates and map them to the short-end tenor grid
(O/N … 12M) that mirrors the BUBOR structure.  This file MUST stay <160 LOC.
"""

from datetime import date, timedelta
from typing import Dict, Any, Optional

from backend.utils.date_utils import PeriodEnum, calculate_start_date
from backend.core.services.macro.macro_service import MacroDataService
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Public API ----------------------------------------------------------------
# ---------------------------------------------------------------------------

SHORT_TENORS = [
    "on",
    "1w",
    "2w",
    "1m",
    "2m",
    "3m",
    "4m",
    "5m",
    "6m",
    "7m",
    "8m",
    "9m",
    "10m",
    "11m",
    "12m",
]

POLICY_RATE_LABELS = {
    "MRR": "Main Refinancing Operations Rate",
    "DFR": "Deposit Facility Rate",
    "MLFR": "Marginal Lending Facility Rate",
    "ESTR": "Euro Short-Term Rate",  # new
}


def resolve_date_range(
    start_date: Optional[date],
    end_date: Optional[date],
    period: Optional[str],
) -> tuple[date, date]:
    """Derive a concrete (start, end) date range from optional inputs."""
    if end_date is None:
        end_date = date.today()
    if period:
        try:
            start_date = calculate_start_date(PeriodEnum(period), end_date)
        except ValueError:
            start_date = end_date - timedelta(days=30)
    elif start_date is None:
        start_date = end_date - timedelta(days=30)
    return start_date, end_date


def map_short_end_tenors(
    policy_rates: Dict[str, Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    """Take raw ECB policy rate dict and expand it into BUBOR-style tenor grid.

    For tenors where no direct ECB rate exists we replicate the latest known
    Deposit Facility Rate (O/N proxy) or interpolate using nearest value.
    """
    if not policy_rates:
        return {}

    # Use Deposit Facility Rate as default filler
    latest_date = max(policy_rates.keys())
    df_rate = policy_rates[latest_date].get("Deposit Facility Rate")

    grid: Dict[str, Dict[str, Any]] = {}
    for date_str, rates in policy_rates.items():
        row: Dict[str, Any] = {}
        for tenor in SHORT_TENORS:
            if tenor == "on":
                # Prefer ESTR if available, otherwise DFR
                row[tenor] = rates.get("Euro Short-Term Rate") or rates.get(
                    "Deposit Facility Rate", df_rate
                )
            elif tenor in ("1w", "2w"):
                row[tenor] = rates.get("Main Refinancing Operations Rate", df_rate)
            else:
                # Monthly tenors – use MRO as proxy
                row[tenor] = rates.get("Main Refinancing Operations Rate", df_rate)
        grid[date_str] = row
    return grid


def build_response(
    start: date,
    end: date,
    period: Optional[str],
    short_grid: Dict[str, Dict[str, Any]],
    source: str = "ECB SDMX (FM dataflow)",
) -> Dict[str, Any]:
    """Wrap the mapped data into the unified JSON response."""
    return {
        "status": "success",
        "metadata": {
            "source": source,
            "date_range": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "period": period or "custom",
            },
            "tenor_count": len(SHORT_TENORS),
        },
        "data": {"rates": short_grid},
        "message": "ECB short-end rates grid retrieved successfully.",
    }


async def get_short_end_rates(
    service: MacroDataService,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    period: Optional[str] = None,
) -> Dict[str, Any]:
    """Async helper that fetches policy & ESTR rates and maps them to tenor-grid."""

    start_date, end_date = resolve_date_range(start_date, end_date, period)

    try:
        raw_rates = await service.get_ecb_policy_rates(start_date, end_date)

        # Merge Euro Short-Term Rate (ON) if available
        estr_data = await service.get_ecb_estr_rate(start_date, end_date)
        if estr_data:
            for d, v in estr_data.items():
                raw_rates.setdefault(d, {})["Euro Short-Term Rate"] = v
    except Exception as exc:  # pragma: no cover
        logger.error("ECB policy rates fetch failed: %s", exc, exc_info=True)
        raw_rates = {}

    if not raw_rates:
        return {
            "status": "unavailable",
            "message": "ECB policy rates unavailable for requested period.",
            "metadata": {
                "source": "ECB SDMX (FM dataflow)",
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                    "period": period or "custom",
                },
            },
            "data": {},
        }

    grid = map_short_end_tenors(raw_rates)

    # Legacy summary fields expected by older dashboards/tests -----------------
    latest_date = max(raw_rates.keys()) if raw_rates else None
    if latest_date:
        grid["main_refinancing_rate"] = raw_rates[latest_date].get(
            "Main Refinancing Operations Rate"
        )

    return build_response(start_date, end_date, period, grid)

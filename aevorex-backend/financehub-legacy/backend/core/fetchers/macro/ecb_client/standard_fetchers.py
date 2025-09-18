"""
Standard ECB Fetchers (Auto-Generated)
======================================

Single entrypoint for all standard ECB dataflows.
Thin wrappers around `fetch_ecb_data` using config-driven approach.
No duplicate logic – all flows handled here.
"""

from __future__ import annotations
from datetime import date
from typing import Dict, Optional

from backend.utils.cache_service import CacheService
from .config import get_dataflow_config
from .generic_fetcher import fetch_ecb_data


# Dynamically build wrapper functions
def _make_fetcher(flow: str):
    async def _fetcher(
        cache: CacheService | None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Dict[str, float]]:
        config = get_dataflow_config(flow)
        if not config:
            raise ValueError(f"Unknown ECB dataflow: {flow}")
        return await fetch_ecb_data(
            cache=cache,
            dataflow=config["dataflow"],
            series=config.get("series", []),
            start=start_date,
            end=end_date,
        )

    _fetcher.__name__ = f"fetch_ecb_{flow}_data"
    _fetcher.__doc__ = f"Fetch data for ECB {flow.upper()} using generic fetcher."
    return _fetcher


# List of all standard flows (config-driven)
_STANDARD_FLOWS = [
    "bls",
    "bsi",
    "cbd",
    "ciss",
    "hicp",
    "hur",  # Unemployment rate
    "rpp",
    "trd",
    "irs",
    "mir",
    "ivf",
    "spf",
    "pss",
    "cpp",
    "sec",
    "estr",
]

# Generate all fetcher functions
globals().update(
    {f"fetch_ecb_{flow}_data": _make_fetcher(flow) for flow in _STANDARD_FLOWS}
)

# Export all dynamically created fetchers
__all__ = [f"fetch_ecb_{flow}_data" for flow in _STANDARD_FLOWS]

# Legacy compatibility mappings (for backward compatibility)
_legacy_mappings = {
    "fetch_bls_data": "fetch_ecb_bls_data",
    "fetch_cbd_data": "fetch_ecb_cbd_data",
    "fetch_ciss_data": "fetch_ecb_ciss_data",
    "fetch_hicp_data": "fetch_ecb_hicp_data",
    "fetch_rpp_data": "fetch_ecb_rpp_data",
    "fetch_trd_data": "fetch_ecb_trd_data",
    "fetch_irs_data": "fetch_ecb_irs_data",
    "fetch_mir_data": "fetch_ecb_mir_data",
    "fetch_ivf_data": "fetch_ecb_ivf_data",
    "fetch_spf_data": "fetch_ecb_spf_data",
    "fetch_pss_data": "fetch_ecb_pss_data",
    "fetch_cpp_data": "fetch_ecb_cpp_data",
    "fetch_sec_data": "fetch_ecb_sec_data",
    "fetch_estr_data": "fetch_ecb_estr_data",
    "fetch_bsi_data": "fetch_ecb_bsi_data",
}

# Add legacy function names to globals for backward compatibility
for legacy_name, new_name in _legacy_mappings.items():
    if new_name in globals():
        globals()[legacy_name] = globals()[new_name]
        __all__.append(legacy_name)

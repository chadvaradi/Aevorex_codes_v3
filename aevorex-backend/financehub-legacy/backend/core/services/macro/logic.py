"""Macro helper logic extracted from rates endpoint.

This module contains pure helper functions so the main FastAPI route file
remains concise (<160 LOC).

Created by o3 model – 2025-07-10
"""

from __future__ import annotations

from typing import Any
from datetime import date

# Extracted helper utilities to stay below LOC ⩽ 160 — see helpers.py
from .helpers import _interpolate_monthly, _short_tenor_map


def flatten_and_format_rates(
    ecb_policy: dict[str, dict[str, float]] | None,
    bubor_curve: dict[str, dict[str, float]] | None,
    ecb_yield: dict[str, dict[str, float]] | None = None,
) -> list[dict[str, Any]]:
    """Transform nested ECB + BUBOR data into frontend-friendly flat list."""
    flat: list[dict[str, Any]] = []

    # ECB policy
    if ecb_policy:
        last_date = max(ecb_policy)
        for tenor, rate in ecb_policy[last_date].items():
            flat.append(
                {
                    "country": "Eurozone",
                    "central_bank": "ECB",
                    "rate_type": tenor,
                    "current_rate": rate,
                    "last_change": last_date,
                    "next_meeting": "N/A",
                }
            )

    # ECB yield curve – fill synthetic months to align with BUBOR tenor list
    if ecb_yield:
        yc_date = max(ecb_yield)
        completed_curve = _interpolate_monthly(ecb_yield[yc_date])
        for maturity, rate in completed_curve.items():
            # Convert "1Y" to "12M" for strict tenor parity with BUBOR
            label = "12M" if maturity == "1Y" else maturity
            flat.append(
                {
                    "country": "Eurozone",
                    "central_bank": "ECB",
                    "rate_type": f"YC {label}",
                    "current_rate": rate,
                    "last_change": yc_date,
                    "next_meeting": "N/A",
                }
            )

    # Short-end O/N,1W,2W derived from policy rates → align with BUBOR grid
    short_rates = _short_tenor_map(ecb_policy, ecb_yield)
    if short_rates:
        last_date = max(ecb_policy) if ecb_policy else date.today().isoformat()
        for tenor, rate in short_rates.items():
            flat.append(
                {
                    "country": "Eurozone",
                    "central_bank": "ECB",
                    "rate_type": f"{tenor}",
                    "current_rate": rate,
                    "last_change": last_date,
                    "next_meeting": "N/A",
                }
            )

    # BUBOR
    if bubor_curve:
        bubor_date = max(bubor_curve)
        for tenor, rate in bubor_curve[bubor_date].items():
            flat.append(
                {
                    "country": "Hungary",
                    "central_bank": "MNB",
                    "rate_type": f"BUBOR {tenor}",
                    "current_rate": rate,
                    "last_change": bubor_date,
                    "next_meeting": "N/A",
                }
            )

    return flat

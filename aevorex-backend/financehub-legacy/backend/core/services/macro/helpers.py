from __future__ import annotations

from math import isfinite
from typing import Any

__all__ = [
    "_interpolate_monthly",
    "_short_tenor_map",
]


def _interpolate_monthly(curve: dict[str, float]) -> dict[str, float]:
    """Fill missing 2–11M maturities in a monthly yield-curve via linear interpolation.

    The input *curve* should at minimum contain the canonical ECB monthly points
    (1M, 3M, 6M, 9M, 12M). The function returns a **new dict** with synthetic
    monthly points so that BUBOR ↔ ECB parity O/N–12M is guaranteed.
    """

    ref_order = [
        "1M",
        "2M",
        "3M",
        "4M",
        "5M",
        "6M",
        "7M",
        "8M",
        "9M",
        "10M",
        "11M",
        "12M",
    ]

    def _lbl_to_num(lbl: str) -> int:
        if lbl.endswith("M"):
            return int(lbl[:-1])
        if lbl.endswith("Y"):
            return int(lbl[:-1]) * 12
        raise ValueError(f"Un-recognised maturity label: {lbl}")

    points = {_lbl_to_num(k): v for k, v in curve.items() if isfinite(v)}
    if not points:
        return curve  # empty or invalid – return original for graceful degrade

    filled = curve.copy()
    for lbl in ref_order:
        if lbl in filled:
            continue
        m = _lbl_to_num(lbl)
        lower = max((p for p in points if p < m), default=None)
        upper = min((p for p in points if p > m), default=None)
        if lower is not None and upper is not None:
            filled[lbl] = points[lower] + (points[upper] - points[lower]) * (
                (m - lower) / (upper - lower)
            )
        elif lower is not None:
            filled[lbl] = points[lower]
        elif upper is not None:
            filled[lbl] = points[upper]

    return filled


def _short_tenor_map(
    ecb_policy: dict[str, dict[str, float]] | None,
    ecb_yield: dict[str, dict[str, float]] | None,
) -> dict[str, float]:
    """Generate O/N, 1W, 2W synthetic short-end rates from ECB datasets.

    Mapping rules – must stay in parity with BUBOR short-tenor grid:
    • O/N  → Deposit Facility Rate (DFR)
    • 1W   → Main Refinancing Operations (MRO)
    • 2W   → Mean(1W, 1M YC) or fallback to 1W if YC point unavailable.
    """

    if not ecb_policy:
        return {}

    last_policy_date = max(ecb_policy)
    policy_rates = ecb_policy[last_policy_date]

    on_rate = policy_rates.get("deposit_facility_rate")
    one_w_rate = policy_rates.get("main_refinancing_rate")

    result: dict[str, float] = {}
    if on_rate is not None:
        result["O/N"] = on_rate
    if one_w_rate is not None:
        result["1W"] = one_w_rate

    two_w: float | None = None
    if one_w_rate is not None:
        one_m: float | None = None
        if ecb_yield:
            yc_date = max(ecb_yield)
            one_m = ecb_yield[yc_date].get("1M")
        two_w = (one_w_rate + one_m) / 2.0 if one_m is not None else one_w_rate

    if two_w is not None:
        result["2W"] = two_w

    return result


__all__.append("flatten_generic_macro_block")


def flatten_generic_macro_block(
    data: dict[str, dict[str, float]],
) -> list[dict[str, Any]]:
    """Flatten date→metric dict into list of records for frontend.

    Input::
        {
            "2025-06": {"M1": 123.4, "M2": 234.5},
            "2025-07": {"M1": 125.0, "M2": 236.0},
        }

    Output::
        [
            {"date": "2025-06", "metric": "M1", "value": 123.4},
            {"date": "2025-06", "metric": "M2", "value": 234.5},
            {"date": "2025-07", "metric": "M1", "value": 125.0},
            {"date": "2025-07", "metric": "M2", "value": 236.0},
        ]
    """

    flattened: list[dict[str, Any]] = []
    for date_key, metrics in data.items():
        for metric, value in metrics.items():
            if value is None:
                continue
            flattened.append({"date": date_key, "metric": metric, "value": value})
    return flattened

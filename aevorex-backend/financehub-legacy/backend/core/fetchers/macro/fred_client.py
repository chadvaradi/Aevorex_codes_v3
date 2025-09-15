"""
Lightweight FRED client helpers (async, no external deps beyond httpx).

Policy: no fallbacks. If key missing or provider fails, raise RuntimeError/HTTPException upstream.
"""

from __future__ import annotations

import asyncio
from datetime import date
from typing import Dict, List, Optional

import httpx

from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


async def _fetch_series_observations(
    client: httpx.AsyncClient,
    api_key: str,
    series_id: str,
    start: date,
    end: date,
    frequency: str | None = None,
    units: str | None = None,
) -> Dict[str, Optional[float]]:
    """Fetch a single FRED series and return {date_str: value|None} mapping.

    Values may be missing ("." in FRED). We convert to None in that case.
    """
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "observation_start": start.isoformat(),
        "observation_end": end.isoformat(),
    }
    if frequency:
        params["frequency"] = frequency
    if units:
        params["units"] = units
    url = "https://api.stlouisfed.org/fred/series/observations"
    resp = await client.get(url, params=params)
    resp.raise_for_status()
    data = resp.json()
    out: Dict[str, Optional[float]] = {}
    for obs in data.get("observations", []):
        v = obs.get("value")
        if v in (None, ".", ""):
            out[obs.get("date")] = None
        else:
            try:
                out[obs.get("date")] = float(v)
            except Exception:
                out[obs.get("date")] = None
    return out


async def fetch_fred_series_matrix(
    client: httpx.AsyncClient,
    api_key: str,
    series_ids: List[str],
    start: date,
    end: date,
    frequency: str | None = None,
    units: str | None = None,
) -> Dict[str, Dict[str, Optional[float]]]:
    """Fetch multiple series in parallel and merge by date.

    Returns: {date_str: {series_id: value|None}}
    """
    tasks = [
        _fetch_series_observations(client, api_key, s, start, end, frequency, units)
        for s in series_ids
    ]
    results = await asyncio.gather(*tasks)
    merged: Dict[str, Dict[str, Optional[float]]] = {}
    for s_id, series_map in zip(series_ids, results):
        for d, val in series_map.items():
            merged.setdefault(d, {})[s_id] = val
    return dict(sorted(merged.items()))

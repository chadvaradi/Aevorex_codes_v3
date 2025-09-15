from __future__ import annotations

"""Minimal DB-Nomics client used as fallback for ECB policy rates.
Keeps LOC < 80 as per FinanceHub #008 rules.
"""

import asyncio
from datetime import date
from typing import Dict, Optional

import httpx

# Mapping of human-readable policy rate names → DB-Nomics series codes
# (LEV = level, most recent observation)
_SERIES: dict[str, str] = {
    "Main refinancing operations": "ECB/FM.MRR_FR.LEV",
    "Deposit facility": "ECB/FM.DFR_LEV",
    "Marginal lending facility": "ECB/FM.MRR_MR.LEV",
}

_BASE = "https://api.db.nomics.world/v22/series/"


class DBNomicsClient:  # noqa: D101 – tiny helper
    def __init__(self):
        self._client: Optional[httpx.AsyncClient] = None

    async def _get(self, url: str) -> dict:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=20)
        r = await self._client.get(url, params={"observations": "1"})
        r.raise_for_status()
        return r.json()

    async def get_policy_rates(
        self, start_date: date | None = None, end_date: date | None = None
    ) -> Dict[str, Dict[str, float]]:
        """Fetch latest policy rates; DB-Nomics JSON gives last obs regardless of dates."""
        tasks = {name: self._get(f"{_BASE}{code}") for name, code in _SERIES.items()}
        raw = await asyncio.gather(*tasks.values(), return_exceptions=True)
        out: Dict[str, Dict[str, float]] = {}
        for (name, _), data in zip(tasks.items(), raw):
            if isinstance(data, Exception):
                continue
            try:
                obs = data["series"]["docs"][0]
                d, v = obs["period"], float(obs["value"])
                out.setdefault(d, {})[name] = v
            except Exception:
                continue
        return out

    async def close(self):
        if self._client:
            await self._client.aclose()

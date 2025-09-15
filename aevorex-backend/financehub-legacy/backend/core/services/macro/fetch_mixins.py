"""Mixin-gyűjtemény: minden *get_ecb_* metódus ide kerül.
Minden mixin logikailag csoportba rendezett, de egyetlen fájlban (<140 LOC).
"""

from __future__ import annotations

from datetime import date
from typing import Optional, Dict

from backend.core.fetchers.macro.ecb_client.standard_fetchers import (
    fetch_ecb_hicp_data,
    fetch_ecb_ivf_data,
    fetch_ecb_cbd_data,
)


class ECBStandardMixin:
    """Policy rates, yield curve, FX, retail, STS, BOP, etc.
    Feltételezi, hogy self.ecb_client és self._get_with_cache_fallback létezik.
    """

    # ---- Existing simple wrappers ---------------------------------
    async def get_ecb_policy_rates(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        from datetime import date as _d, timedelta as _td

        cache_key = f"ecb:policy_rates:{start_date}:{end_date or 'latest'}"
        if end_date is None:
            end_date = _d.today()
        if start_date is None:
            start_date = end_date - _td(days=90)
        return await self._get_with_cache_fallback(
            lambda: self.ecb_client.get_policy_rates(start_date, end_date),
            cache_key,
        )

    async def get_ecb_yield_curve(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        from datetime import date as _d, timedelta as _td

        cache_key = f"ecb:yield_curve:{start_date}:{end_date or 'latest'}"
        if end_date is None:
            end_date = _d.today()
        if start_date is None:
            start_date = end_date - _td(days=90)
        return await self._get_with_cache_fallback(
            lambda: self.ecb_client.get_yield_curve(start_date, end_date),
            cache_key,
        )

    async def get_ecb_fx_rates(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        from datetime import date as _d, timedelta as _td

        cache_key = f"ecb:fx_rates:{start_date}:{end_date or 'latest'}"
        if end_date is None:
            end_date = _d.today()
        if start_date is None:
            start_date = end_date - _td(days=90)
        return await self._get_with_cache_fallback(
            lambda: self.ecb_client.get_fx_rates(
                start_date=start_date, end_date=end_date
            ),
            cache_key,
        )

    async def get_ecb_retail_rates(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:retail_rates:{start_date}:{end_date or 'latest'}"

        async def _fetch():
            data = await self.ecb_client.get_retail_interest_rates(start_date, end_date)
            if not data:
                policy = await self.get_ecb_policy_rates(start_date, end_date)
                if policy:
                    data = {
                        d: {
                            "deposit_rate": v.get("deposit_facility_rate"),
                            "lending_rate": v.get("marginal_lending_facility_rate"),
                        }
                        for d, v in policy.items()
                    }
            return data

        return await self._get_with_cache_fallback(_fetch, cache_key)

    # ---- Previously added wrappers (MIR, STS, etc.) ----------------
    async def get_ecb_mir(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        return await self.get_ecb_retail_rates(start_date, end_date)

    async def get_ecb_sts(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:sts:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: self.ecb_client.get_sts_data(start_date, end_date),
            cache_key,
        )

    async def get_ecb_bop(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:bop:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: self.ecb_client.get_bop_data(start_date, end_date),
            cache_key,
        )

    # ---- New fetchers via generic_fetcher --------------------------
    async def get_ecb_sec(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        from backend.core.fetchers.macro.ecb_client.sec_fetcher import (
            fetch_ecb_sec_data,
        )

        cache_key = f"ecb:sec:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_sec_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_ivf(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:ivf:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_ivf_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_cbd(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:cbd:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_cbd_data(self._cache, start_date, end_date),
            cache_key,
        )

    # ---- Property & survey dataflows --------------------------------------
    async def get_ecb_rpp(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:rpp:{start_date}:{end_date or 'latest'}"
        from backend.core.fetchers.macro.ecb_client import fetch_ecb_rpp_data

        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_rpp_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_cpp(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:cpp:{start_date}:{end_date or 'latest'}"
        from backend.core.fetchers.macro.ecb_client import fetch_ecb_cpp_data

        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_cpp_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_bls(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:bls:{start_date}:{end_date or 'latest'}"
        from backend.core.fetchers.macro.ecb_client import fetch_ecb_bls_data

        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_bls_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_spf(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:spf:{start_date}:{end_date or 'latest'}"
        from backend.core.fetchers.macro.ecb_client import fetch_ecb_spf_data

        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_spf_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_ciss(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:ciss:{start_date}:{end_date or 'latest'}"
        from backend.core.fetchers.macro.ecb_client import fetch_ecb_ciss_data

        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_ciss_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_estr_rate(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:estr:{start_date}:{end_date or 'latest'}"
        from backend.core.fetchers.macro.ecb_client import fetch_ecb_estr_rate

        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_estr_rate(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_pss(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        from backend.core.fetchers.macro.ecb_client.pss_fetcher import (
            fetch_ecb_pss_data,
        )

        cache_key = f"ecb:pss:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_pss_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_irs(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        from backend.core.fetchers.macro.ecb_client.irs_fetcher import (
            fetch_ecb_irs_data,
        )

        cache_key = f"ecb:irs:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_irs_data(self._cache, start_date, end_date),
            cache_key,
        )

    async def get_ecb_hicp(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        cache_key = f"ecb:hicp:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_hicp_data(self._cache, start_date, end_date),
            cache_key,
        )

    # --- Utility -----------------------------------------------------------
    @staticmethod
    def curve_to_csv(curve: Dict) -> str:
        """Simple utility kept here to avoid extra files."""
        import csv
        from io import StringIO

        sio = StringIO()
        writer = csv.writer(sio)
        writer.writerow(["maturity", "value"])
        for k, v in curve.items():
            writer.writerow([k, v])
        return sio.getvalue()

    # ---- Newly added wrappers for BSI and inflation ----------------
    async def get_ecb_bsi(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        """Fetch Euro Area monetary aggregates (M1–M3) via ECB BSI dataflow.
        Gracefully falls back to cached snapshot on API error (handled by _get_with_cache_fallback).
        """
        cache_key = f"ecb:bsi:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: self.ecb_client.get_monetary_aggregates(start_date, end_date),
            cache_key,
        )

    async def get_ecb_inflation_indicators(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        """Fetch headline / core / energy HICP inflation indicators.
        Wrapper around ECBSDMXClient.get_inflation_indicators.
        """
        cache_key = f"ecb:inflation:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: self.ecb_client.get_inflation_indicators(start_date, end_date),
            cache_key,
        )

    async def get_ecb_trd(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ):
        from backend.core.fetchers.macro.ecb_client.trd_fetcher import (
            fetch_ecb_trd_data,
        )

        cache_key = f"ecb:trd:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_trd_data(self._cache, start_date, end_date),
            cache_key,
        )
        cache_key = f"ecb:trd:{start_date}:{end_date or 'latest'}"
        return await self._get_with_cache_fallback(
            lambda: fetch_ecb_trd_data(self._cache, start_date, end_date),
            cache_key,
        )

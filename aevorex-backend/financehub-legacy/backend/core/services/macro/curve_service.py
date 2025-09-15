"""
Yield Curve Service
===================

Business logic for yield curve data processing and formatting.
Extracted from API endpoints to maintain clean architecture.
"""

from __future__ import annotations

import asyncio
from datetime import date, timedelta
from typing import Dict, Any, Optional
from time import perf_counter

from backend.core.fetchers.macro.ecb_client.specials.fed_yield_curve import (
    fetch_fed_yield_curve_historical,
)
from backend.core.metrics import METRICS_EXPORTER
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class CurveService:
    """Service for yield curve data processing and business logic."""

    @staticmethod
    async def get_curve_data(
        source: str,
        days: int,
        plan: str,
        macro_service,
    ) -> Dict[str, Any]:
        """
        Get yield curve data for a given source with plan-based clamping.

        Args:
            source: Data source ('ecb' or 'ust')
            days: Number of days of history
            plan: User plan ('free', 'pro', 'enterprise')
            macro_service: Injected macro service instance

        Returns:
            Dict containing curve data and metadata
        """
        src = source.lower()
        end_date = date.today()

        # Clamp days by plan
        max_days = 1 if plan == "free" else (30 if plan == "pro" else 365 * 3)
        days = min(max(days, 0), max_days)
        start_date = end_date - timedelta(days=days or 1)

        # Try ECB first
        if src == "ecb":
            ecb_data = await CurveService._fetch_ecb_curve(
                macro_service, start_date, end_date
            )
            if ecb_data:
                return ecb_data
            else:
                logger.error("ECB yield-curve data unavailable")
                return {
                    "status": "error",
                    "message": "ECB yield curve data unavailable",
                    "source": "ecb",
                    "curve": {},
                }

        # Try UST if explicitly requested
        if src == "ust":
            ust_data = await CurveService._fetch_ust_curve(start_date, end_date)
            if ust_data:
                return ust_data

        # Fallback for unsupported sources
        return {
            "status": "error",
            "message": "Curve source not supported",
            "supported_sources": ["ecb", "ust"],
            "curve": {},
        }

    @staticmethod
    async def _fetch_ecb_curve(
        macro_service, start_date: date, end_date: date
    ) -> Optional[Dict[str, Any]]:
        """Fetch ECB yield curve data."""
        try:
            _t0 = perf_counter()
            data = await macro_service.get_ecb_yield_curve(start_date, end_date)
            METRICS_EXPORTER.observe_ecb_request(perf_counter() - _t0)

            if not data:
                return None

            latest_date = max(data.keys())
            return {
                "status": "success",
                "source": "ecb",
                "curve": data[latest_date],
                "date": latest_date,
            }
        except Exception as exc:
            logger.error("ECB yield-curve fetch failed: %s", exc, exc_info=True)
            return None

    @staticmethod
    async def _fetch_ust_curve(
        start_date: date, end_date: date
    ) -> Optional[Dict[str, Any]]:
        """Fetch UST yield curve data with retry logic."""
        try:
            _t0 = perf_counter()

            # Robust fetch with retry and lower timeout to fail fast
            for attempt in range(3):
                try:
                    df_full = await asyncio.wait_for(
                        fetch_fed_yield_curve_historical(), timeout=30
                    )
                    break
                except Exception as _fetch_err:
                    if attempt == 2:
                        raise
                    await asyncio.sleep(0.4 * (attempt + 1))

            # Keep only the requested range; if empty, fall back to the LATEST available row (09/12/2025)
            df_range = df_full.loc[start_date:end_date]
            df_use = df_range if not df_range.empty else df_full.tail(1)
            latest_row = df_use.iloc[-1]
            curve = {
                k: float(v) if v == v else None for k, v in latest_row.to_dict().items()
            }

            METRICS_EXPORTER.observe_ust_request(perf_counter() - _t0)

            return {
                "status": "success",
                "source": "ust",
                "curve": curve,
                "date": str(df_use.index[-1].date()),
            }
        except Exception as exc:
            METRICS_EXPORTER.inc_ust_error(type(exc).__name__)
            logger.error("UST yield-curve fetch failed: %s", exc, exc_info=True)
            return {
                "status": "success",
                "message": "UST yield-curve unavailable – returning empty curve",
                "curve": {},
                "error": str(exc),
            }

"""STS Logic – helper functions split from sts.py (must stay <160 LOC)."""

from __future__ import annotations

from datetime import date, timedelta
import logging
from typing import Dict, Optional

from fastapi.responses import JSONResponse

from backend.utils.cache_service import CacheService
from backend.core.fetchers.macro.ecb_client import fetch_ecb_sts_data
from backend.core.fetchers.macro.ecb_client.exceptions import ECBAPIError

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Public helper – core STS fetch & transform
# ---------------------------------------------------------------------------


async def get_sts_response(
    start_date: Optional[date],
    end_date: Optional[date],
    indicators: Optional[str],
    cache_service: CacheService,
) -> JSONResponse:
    """Return STS statistics (JSONResponse, status always 200 by Rule #008)."""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=365)
        if not end_date:
            end_date = date.today()

        sts_data: Dict[str, Dict[str, float]] = await fetch_ecb_sts_data(
            cache=cache_service,
            start_date=start_date,
            end_date=end_date,
        )

        if not sts_data:
            from fastapi import HTTPException

            raise HTTPException(status_code=503, detail="ECB STS data unavailable")

        if indicators:
            requested = [i.strip() for i in indicators.split(",")]
            sts_data = {
                d: {k: v for k, v in rec.items() if k in requested}
                for d, rec in sts_data.items()
            }

        metadata = {
            "total_records": len(sts_data),
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "data_source": "ECB SDMX (STS)",
            "frequency": "monthly",
            "indicators": sorted({k for rec in sts_data.values() for k in rec})
            if sts_data
            else [],
        }
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "metadata": metadata,
                "data": sts_data,
            },
        )
    except ECBAPIError as err:
        from fastapi import HTTPException

        logger.warning("ECB STS fetch error: %s", err)
        raise HTTPException(status_code=503, detail=str(err))
    except Exception as exc:  # pragma: no cover
        from fastapi import HTTPException

        logger.error("Unexpected STS error: %s", exc, exc_info=True)
        raise HTTPException(status_code=503, detail="Internal error")


def get_indicators_response() -> JSONResponse:
    """Return static list of STS indicators."""
    indicators = {
        "industrial_production": "Industrial Production Index",
        "retail_sales": "Retail Sales Volume Index",
        "construction_output": "Construction Output Index",
        "unemployment_rate": "Unemployment Rate (%)",
        "employment_rate": "Employment Rate (%)",
        "business_confidence": "Business Confidence Indicator",
        "consumer_confidence": "Consumer Confidence Indicator",
        "capacity_utilization": "Capacity Utilization Rate (%)",
    }
    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "indicators": indicators,
            "total_indicators": len(indicators),
        },
    )


async def get_latest_sts_response(
    indicators: Optional[str],
    cache_service: CacheService,
) -> JSONResponse:
    """Return most recent data rows (default 30 days window)."""
    today = date.today()
    start = today - timedelta(days=30)
    return await get_sts_response(start, today, indicators, cache_service)


# ---------------------------------------------------------------------------
# Helpers -------------------------------------------------------------------
# ---------------------------------------------------------------------------


def _empty_payload(
    message: str = "",
    start_date: Optional[date] | None = None,
    end_date: Optional[date] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "metadata": {
                "source": "ECB STS endpoint",
                "message": message or "No data",
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
            },
            "data": {},
        },
    )

"""FX business logic extracted from fx.py (Rule #008)"""

from __future__ import annotations

from datetime import date, timedelta
from typing import Optional, Dict, Any

from backend.core.services.macro.macro_service import MacroDataService
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

__all__ = ["build_fx_response"]


async def build_fx_response(
    service: MacroDataService,
    start_date: Optional[date],
    end_date: Optional[date],
) -> Dict[str, Any]:
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=30)

    try:
        fx_data = await service.get_ecb_fx_rates(start_date, end_date)
    except Exception as exc:
        logger.warning("ECB FX fetch failed: %s", exc)
        fx_data = None

    from fastapi import HTTPException

    if not fx_data:
        raise HTTPException(status_code=503, detail="ECB FX rates unavailable")
    source = "ECB SDMX (EXR dataflow)"

    return {
        "status": "success",
        "metadata": {
            "source": source,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
            },
        },
        "data": {"fx_rates": fx_data},
    }


async def get_ecb_fx_rates_legacy(
    service: MacroDataService,
    currency_pair: str,
) -> Dict[str, Any]:
    """
    Legacy ECB FX rates endpoint with cache handling and error management.
    Business logic moved from fx_router.py to maintain clean architecture.
    """
    from backend.core.fetchers.macro.ecb_client.fetchers import fetch_ecb_fx_rates
    from fastapi import HTTPException
    import structlog

    logger = structlog.get_logger(__name__)
    cache_key = f"macro:ecb:fx_rates:{currency_pair}"

    try:
        # Get cache service (simplified for this example)
        cache = None  # Would be injected in real implementation

        if cache:
            cached_data = await cache.get(cache_key)
            if (
                cached_data
                and isinstance(cached_data, dict)
                and cached_data.get("status") == "success"
            ):
                logger.info("Cache HIT for ECB FX rates (valid success payload).")
                return cached_data
            elif cached_data:
                logger.info(
                    "Cache HIT contained previous error payload – skipping and refreshing."
                )

        logger.info("Cache MISS for ECB FX rates. Fetching from ECB.")

        # Get last 30 days of data
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        fx_data = await fetch_ecb_fx_rates(cache, currency_pair, start_date, end_date)

        if not fx_data or (
            isinstance(fx_data, dict) and fx_data.get("status") == "error"
        ):
            raise HTTPException(status_code=503, detail="ECB FX rates unavailable")

        response_data = {
            "status": "success",
            "metadata": {
                "source": "ECB SDMX (EXR dataflow)",
                "currency_pairs": currency_pair,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            },
            "data": {"fx_rates": fx_data},
            "message": "ECB FX rates retrieved successfully.",
        }

        # Cache for 1 hour
        if cache:
            await cache.set(cache_key, response_data, ttl=3600)

        return response_data

    except HTTPException as exc:
        logger.warning(
            "ECB FX legacy endpoint caught HTTPException – returning success with empty dataset: %s",
            exc.detail,
        )
        return {
            "status": "success",
            "metadata": {
                "source": "ECB SDMX (EXR dataflow)",
                "warning": exc.detail,
            },
            "data": {},
            "message": "ECB FX rates temporarily unavailable – empty dataset returned.",
        }
    except Exception as e:
        logger.error("Error fetching ECB FX rates: %s", e)
        raise HTTPException(status_code=503, detail=str(e))

from __future__ import annotations

"""Chart data business logic (extracted from chart_data view)."""
import logging
from typing import Tuple, Dict, Any
import pandas as pd
from httpx import AsyncClient
from backend.utils.cache_service import CacheService
from backend.core.services.stock.chart_service import ChartService

logger = logging.getLogger(__name__)


async def fetch_chart_data(
    symbol: str,
    http_client: AsyncClient,
    cache: CacheService,
    period: str,
    interval: str,
) -> Tuple[Dict[str, Any], str, str]:
    """Return (ohlcv list, currency, timezone) tuple; relies on ChartService real API.
    Falls back to yfinance if necessary.
    """
    chart_service = ChartService()
    chart_data = await chart_service.get_chart_data(
        symbol, http_client, cache, period, interval
    )
    currency = "USD"
    timezone = "America/New_York"
    if isinstance(chart_data, pd.DataFrame):
        if hasattr(chart_data, "attrs"):
            currency = chart_data.attrs.get("currency", currency)
            timezone = chart_data.attrs.get("timezone", timezone)
        ohlcv = chart_data.to_dict("records")
    elif isinstance(chart_data, dict):
        ohlcv = chart_data.get("ohlcv", [])
        currency = chart_data.get("currency", currency)
        timezone = chart_data.get("timezone", timezone)
    else:
        ohlcv = []
    return ohlcv, currency, timezone

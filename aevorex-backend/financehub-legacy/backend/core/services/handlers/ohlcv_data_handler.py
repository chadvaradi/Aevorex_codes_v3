"""
Handler for fetching OHLCV data.
"""

import asyncio
from typing import Any
import httpx

from ....utils.cache_service import CacheService
from ....core import fetchers
from ....utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.handlers.ohlcv_data")
TIMEOUT_SECONDS = 30


async def fetch_ohlcv_data(
    symbol: str,
    period: str,
    interval: str,
    client: httpx.AsyncClient,
    cache: CacheService,
    request_id: str,
) -> list[dict[str, Any]] | None:
    """Fetch OHLCV data (dev-only fallback may apply upstream; prod: no fallback)."""
    try:
        yfinance_fetcher = await fetchers.get_fetcher("yfinance", client, cache)
        result = await asyncio.wait_for(
            yfinance_fetcher.fetch_ohlcv(
                ticker=symbol, period=period, interval=interval
            ),
            timeout=TIMEOUT_SECONDS,
        )

        if result is not None:
            logger.debug(f"[{request_id}] OHLCV data fetched for {symbol}")
            return result

        logger.warning(f"[{request_id}] No OHLCV data found for {symbol}")
        return None

    except TimeoutError:
        logger.warning(f"[{request_id}] OHLCV fetch timeout for {symbol}")
        return None
    except Exception as e:
        logger.error(
            f"[{request_id}] OHLCV fetch error for {symbol}: {e}", exc_info=True
        )
        return None

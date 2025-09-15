"""
Technical Analysis Service

This service handles the calculation of technical indicators for a stock.
It replaces the logic from `_calculate_indicators` and `_extract_latest_indicators`
in the monolithic `stock_service`.
"""

from typing import Any
import httpx

from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.core.services.stock.chart_service import ChartService  # fixed path
from backend.core.services.stock.technical_processors import TechnicalProcessor

logger = get_logger("aevorex_finbot.TechnicalService")


class TechnicalService:
    """Service for calculating technical analysis indicators."""

    def __init__(self):
        self.chart_service = ChartService()
        self.processor = TechnicalProcessor()
        self.cache_ttl = 1800  # 30 minutes

    async def get_technical_analysis(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        force_refresh: bool = False,
    ) -> dict[str, Any] | None:
        """
        Calculates and returns the latest technical indicators for a symbol.
        """
        log_prefix = f"[TechnicalService:{symbol}]"
        cache_key = f"technicals:{symbol}"

        if not force_refresh:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug(f"{log_prefix} Cache HIT for technical indicators.")
                return cached_data

        try:
            # Technical analysis depends on historical chart data
            ohlcv_df = await self.chart_service.get_chart_data(
                symbol,
                client,
                cache,
                period="1y",
                interval="1d",
                force_refresh=force_refresh,
            )

            if ohlcv_df is None or ohlcv_df.empty:
                logger.warning(
                    f"{log_prefix} Cannot calculate technicals, no OHLCV data found."
                )
                return None

            # Use the processor to calculate indicators
            indicators_df = self.processor.calculate_all_indicators(ohlcv_df)

            # Extract the latest values
            latest_indicators = self.processor.extract_latest_values(indicators_df)

            await cache.set(cache_key, latest_indicators, ttl=self.cache_ttl)
            logger.info(
                f"{log_prefix} Successfully calculated and cached {len(latest_indicators)} technical indicators."
            )

            return latest_indicators

        except Exception as e:
            logger.error(
                f"{log_prefix} Error calculating technical indicators: {e}",
                exc_info=True,
            )
            return None

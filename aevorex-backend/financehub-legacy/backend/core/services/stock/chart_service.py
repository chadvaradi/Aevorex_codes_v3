"""
Chart Service

Handles chart/OHLCV data fetching, processing, and caching for stock symbols.
This service ensures that only pandas DataFrames are cached and returned,
abstracting away the dictionary-based format from the underlying handlers.
"""

from typing import Any
import httpx
import pandas as pd
from backend.utils.cache_service import CacheService
from backend.utils.logger_config import get_logger
from backend.core.services.stock.chart_data_handler import ChartDataHandler
from backend.core.services.shared.response_helpers import process_ohlcv_dataframe

logger = get_logger("aevorex_finbot.ChartService")


class ChartService:
    """Service for handling chart and OHLCV data operations."""

    def __init__(self):
        self.cache_ttl = 600  # 10 minutes for chart data
        self.chart_handler = ChartDataHandler()

    async def get_chart_data(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        period: str = "1y",
        interval: str = "1d",
        force_refresh: bool = False,
    ) -> pd.DataFrame | None:
        """
        Get chart/OHLCV data for a stock symbol.
        This is the single source of truth for fetching OHLCV DataFrames.
        It handles caching of the DataFrame itself.
        """
        cache_key = f"chart_data:{symbol}:{period}:{interval}"

        if not force_refresh:
            cached_df = await cache.get(cache_key)
            if isinstance(cached_df, pd.DataFrame):
                logger.debug(f"Chart DataFrame cache hit for {symbol}")
                return cached_df

        try:
            # The handler returns a dictionary containing the DataFrame and other info
            chart_data_dict = await self.chart_handler.get_chart_data(
                symbol, period, interval, client, cache
            )

            if chart_data_dict and "ohlcv_df" in chart_data_dict:
                ohlcv_df = chart_data_dict["ohlcv_df"]
                if isinstance(ohlcv_df, pd.DataFrame) and not ohlcv_df.empty:
                    # Cache the DataFrame directly for future requests
                    await cache.set(cache_key, ohlcv_df, ttl=self.cache_ttl)
                    logger.debug(f"Fetched and cached chart DataFrame for {symbol}")
                    return ohlcv_df

            logger.warning(f"Could not retrieve a valid OHLCV DataFrame for {symbol}")
            return None

        except Exception as e:
            logger.error(f"Error in get_chart_data for {symbol}: {e}", exc_info=True)
            return None

    async def get_basic_chart_data(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        days: int = 30,
    ) -> dict[str, Any] | None:
        """Get basic chart data for quick display, using the main get_chart_data."""
        # This method can have its own cache if the processed data is expensive to generate
        cache_key = f"basic_chart:{symbol}:{days}"
        cached_data = await cache.get(cache_key)
        if cached_data:
            return cached_data

        try:
            period = "1mo" if days <= 30 else "3mo"
            ohlcv_df = await self.get_chart_data(symbol, client, cache, period, "1d")

            if ohlcv_df is None or ohlcv_df.empty:
                return None

            # Use a helper to process the DataFrame into the desired format
            history, latest_ohlcv = process_ohlcv_dataframe(
                ohlcv_df.tail(days), f"basic_chart-{symbol}"
            )

            latest_price = latest_ohlcv.get("close") if latest_ohlcv else None

            basic_data = {
                "symbol": symbol,
                "current_price": latest_price,
                "price_history": history,
                "latest_ohlcv": latest_ohlcv,
                "data_points": len(history),
            }

            await cache.set(cache_key, basic_data, ttl=300)  # 5 min cache
            return basic_data

        except Exception as e:
            logger.error(
                f"Error fetching basic chart data for {symbol}: {e}", exc_info=True
            )
            return None

    async def get_price_history(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        period: str = "1y",
    ) -> dict[str, Any] | None:
        """Get price history data only."""
        try:
            ohlcv_df = await self.get_chart_data(symbol, client, cache, period, "1d")

            if ohlcv_df is None or ohlcv_df.empty:
                return None

            history, latest_ohlcv = process_ohlcv_dataframe(
                ohlcv_df, f"price_hist-{symbol}"
            )
            latest_price = latest_ohlcv.get("close") if latest_ohlcv else None

            return {
                "symbol": symbol,
                "price_history": history,
                "latest_price": latest_price,
                "period": period,
            }

        except Exception as e:
            logger.error(
                f"Error fetching price history for {symbol}: {e}", exc_info=True
            )
            return None

    async def get_latest_price(
        self, symbol: str, client: httpx.AsyncClient, cache: CacheService
    ) -> float | None:
        """Get just the latest price for a symbol."""
        try:
            # Fetching 5d is enough to get the latest close
            ohlcv_df = await self.get_chart_data(symbol, client, cache, "5d", "1d")

            if ohlcv_df is not None and not ohlcv_df.empty:
                return ohlcv_df.iloc[-1]["close"]

            return None

        except Exception as e:
            logger.error(
                f"Error fetching latest price for {symbol}: {e}", exc_info=True
            )
            return None

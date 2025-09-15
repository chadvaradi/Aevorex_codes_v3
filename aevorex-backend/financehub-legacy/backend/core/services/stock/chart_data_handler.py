"""
Chart Data Handler - Handles OHLCV data fetching and processing.
Split from technical_service.py to maintain 160 LOC limit.
"""

from typing import Any
import httpx
from backend.utils.cache_service import CacheService
from backend.utils.logger_config import get_logger
from backend.core.services.stock.chart_validators import ChartDataValidator

logger = get_logger("aevorex_finbot.ChartDataHandler")


class ChartDataHandler:
    """Handles chart data (OHLCV) operations."""

    def __init__(self):
        self.validator = ChartDataValidator()

    async def get_chart_data(
        self,
        symbol: str,
        period: str,
        interval: str,
        client: httpx.AsyncClient,
        cache: CacheService,
    ) -> dict[str, Any] | None:
        """Get chart data (OHLCV) for the symbol."""
        request_id = f"chart_{symbol}_{period}_{interval}"

        try:
            # Fetch fresh data using existing fetchers
            ohlcv_data = await self._fetch_ohlcv_data(
                symbol, period, interval, client, cache, request_id
            )

            # Handle None or empty DataFrame explicitly to avoid ambiguous truth value errors
            if ohlcv_data is None or (
                hasattr(ohlcv_data, "empty") and getattr(ohlcv_data, "empty", False)
            ):
                logger.error(
                    f"[{request_id}] All OHLCV sources failed or returned empty data"
                )
                return None

            # Process and format the data
            chart_ready_list = await self._process_ohlcv_data(
                ohlcv_data, request_id, symbol
            )
            if not chart_ready_list:
                return None

            # Validate and convert to DataFrame
            ohlcv_df = await self.validator.validate_ohlcv_dataframe(
                chart_ready_list, request_id
            )
            if ohlcv_df is None:
                return None

            # Prepare response format
            (
                price_history,
                latest_ohlcv,
                latest_price_str,
                latest_price_float,
            ) = await self.validator.prepare_ohlcv_for_response(
                chart_ready_list, request_id
            )

            result = {
                "price_history": price_history,
                "latest_ohlcv": latest_ohlcv,
                "latest_price": latest_price_str,
                "latest_price_float": latest_price_float,
                "ohlcv_df": ohlcv_df,
            }

            return result

        except Exception as e:
            logger.error(
                f"[{request_id}] Chart data processing failed: {e}", exc_info=True
            )
            return None

    async def _fetch_ohlcv_data(
        self,
        symbol: str,
        period: str,
        interval: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        request_id: str,
    ):
        """Fetch OHLCV data from multiple sources with fallback."""
        # Import the fetcher factory lazily to avoid circular imports
        from backend.core.fetchers.factory import get_fetcher

        eodhd_fetcher = await get_fetcher("eodhd", http_client=client, cache=cache)
        yfinance_fetcher = await get_fetcher(
            "yfinance", http_client=client, cache=cache
        )

        # Try EODHD first (preferred for accuracy)
        try:
            ohlcv_data = await eodhd_fetcher.fetch_ohlcv(
                ticker=symbol, period=period, interval=interval
            )
            if ohlcv_data is not None:
                return ohlcv_data
        except Exception as e:
            logger.warning(f"[{request_id}] EODHD fetch failed: {e}")

        # Fallback to yfinance
        try:
            return await yfinance_fetcher.fetch_ohlcv(
                ticker=symbol, period=period, interval=interval
            )
        except Exception as e:
            logger.warning(f"[{request_id}] YFinance fetch failed: {e}")

        return None

    async def _process_ohlcv_data(
        self, ohlcv_data: Any, request_id: str, symbol: str | None = None
    ) -> list[dict[str, Any]] | None:
        """Process raw OHLCV data into chart-ready format."""
        try:
            from backend.core import mappers

            if hasattr(ohlcv_data, "to_dict"):  # DataFrame
                return mappers.map_yfinance_ohlcv_df_to_chart_list(
                    ohlcv_data, request_id, symbol
                )
            else:  # Dict or other format
                return mappers.map_eodhd_data_to_chart_ready_format(ohlcv_data)

        except Exception as e:
            logger.error(f"[{request_id}] OHLCV processing failed: {e}", exc_info=True)
            return None

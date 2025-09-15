"""
OHLCV Data Processor

This module contains the logic for processing raw OHLCV data into a
chart-ready format. It is used by various services that handle historical price data.
"""

from typing import Any
from backend.utils.logger_config import get_logger
from backend.core import mappers

logger = get_logger("aevorex_finbot.OHLCVProcessor")


class OHLCVProcessor:
    """
    Handles the conversion of OHLCV data from various sources into a standardized
    list of dictionaries suitable for charting libraries.
    """

    async def process_ohlcv_data(
        self, ohlcv_data: Any, request_id: str
    ) -> list[dict[str, Any]] | None:
        """Process raw OHLCV data into chart-ready format."""
        try:
            if hasattr(ohlcv_data, "to_dict"):  # DataFrame
                logger.debug(
                    f"[{request_id}] Mapping yfinance OHLCV DataFrame to chart list."
                )
                return mappers.map_yfinance_ohlcv_df_to_chart_list(
                    ohlcv_data, request_id
                )
            else:  # Assume EODHD dict format
                logger.debug(f"[{request_id}] Mapping EODHD OHLCV data to chart list.")
                return mappers.map_eodhd_data_to_chart_ready_format(ohlcv_data)

        except Exception as e:
            logger.error(f"[{request_id}] OHLCV processing failed: {e}", exc_info=True)
            return None
            return None

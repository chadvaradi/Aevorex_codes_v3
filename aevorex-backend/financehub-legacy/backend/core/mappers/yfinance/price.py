# Aevorex_codes/modules/financehub/backend/core/mappers/yfinance/price.py
import pandas as pd
from typing import Any

from backend.core.mappers._mapper_base import logger

_OHLCV_COLUMN_MAP: dict[str, str] = {
    "open": "open",
    "high": "high",
    "low": "low",
    "close": "close",
    "volume": "volume",
}


def map_yfinance_ohlcv_df_to_chart_list(
    ohlcv_df: pd.DataFrame | None, request_id: str, symbol: str | None = "N/A_SYMBOL"
) -> list[dict[str, Any]] | None:
    """
    Maps a yfinance OHLCV DataFrame to a list of dictionaries suitable for charting libraries.
    Normalizes column names and converts timestamps to Unix seconds.
    """
    func_name = "map_yfinance_ohlcv_df_to_chart_list"
    log_prefix = f"[{request_id}][{func_name}][{symbol}]"

    if not isinstance(ohlcv_df, pd.DataFrame) or ohlcv_df.empty:
        logger.warning(
            f"{log_prefix} Input OHLCV DataFrame is invalid or empty. Cannot create chart list."
        )
        return None

    df = ohlcv_df.copy()

    # Normalize column names to lowercase
    df.columns = [col.lower() for col in df.columns]

    # Check for required columns
    required_cols = set(_OHLCV_COLUMN_MAP.keys())
    if not required_cols.issubset(df.columns):
        missing_cols = required_cols - set(df.columns)
        logger.error(
            f"{log_prefix} Missing required OHLCV columns after normalization: {missing_cols}. Cannot proceed."
        )
        return None

    # Rename columns to short format
    df_renamed = df.rename(columns=_OHLCV_COLUMN_MAP)

    # Ensure index is a DatetimeIndex
    if not isinstance(df_renamed.index, pd.DatetimeIndex):
        logger.error(
            f"{log_prefix} DataFrame index is not a DatetimeIndex. Cannot convert timestamps."
        )
        return None

    # Convert timestamp to Unix seconds and create list of dicts
    try:
        df_renamed["timestamp"] = (df_renamed.index.astype(int) / 10**9).astype(int)

        # Select and reorder columns for the final output
        final_cols = ["timestamp"] + list(_OHLCV_COLUMN_MAP.values())
        chart_list = df_renamed[final_cols].to_dict(orient="records")

        logger.info(
            f"{log_prefix} Successfully mapped OHLCV DataFrame to a list of {len(chart_list)} chart points."
        )
        return chart_list

    except Exception as e:
        logger.error(
            f"{log_prefix} An unexpected error occurred during final mapping: {e}",
            exc_info=True,
        )
        return None

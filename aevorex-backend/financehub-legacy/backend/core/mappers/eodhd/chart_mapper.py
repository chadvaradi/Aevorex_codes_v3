# backend/core/mappers/eodhd/chart_mapper.py
# ==============================================================================
# Orchestrator mapper to combine various EODHD data types into a single,
# chart-ready format for the frontend.
# ==============================================================================
import pandas as pd
from typing import Any
from datetime import datetime

from ._mapper_base import logger
from .helpers import preprocess_ohlcv_dataframe
from .events_mapper import (
    map_eodhd_splits_data_to_models,
    map_eodhd_dividends_data_to_models,
)


def map_eodhd_data_to_chart_ready_format(
    ohlcv_df: pd.DataFrame,
    splits_df: pd.DataFrame | None,
    dividends_df: pd.DataFrame | None,
    request_id: str,
    interval: str = "d",
) -> list[dict[str, Any]]:
    """
    Combines OHLCV, splits, and dividends data into a single, chart-ready list of dictionaries.
    """
    log_prefix = f"[{request_id}][map_eodhd_data_to_chart_ready_format]"
    logger.info(f"{log_prefix} Starting combined mapping for chart-ready format.")

    if not isinstance(ohlcv_df, pd.DataFrame) or ohlcv_df.empty:
        logger.warning(
            f"{log_prefix} OHLCV DataFrame is missing or empty. Returning empty list."
        )
        return []

    # 1. Preprocess the main OHLCV dataframe
    processed_ohlcv_df = preprocess_ohlcv_dataframe(
        ohlcv_df, request_id, interval, log_prefix
    )
    if processed_ohlcv_df is None or processed_ohlcv_df.empty:
        logger.error(
            f"{log_prefix} OHLCV DataFrame is empty or invalid after preprocessing."
        )
        return []

    chart_list = processed_ohlcv_df.reset_index().to_dict("records")

    for item in chart_list:
        date_idx = item.pop("index")  # from reset_index()
        ts_dt = pd.to_datetime(date_idx, utc=True)
        if pd.isna(ts_dt):
            item["timestamp"] = None
            item["t"] = None
        else:
            item["timestamp"] = ts_dt.isoformat()
            item["t"] = int(ts_dt.timestamp() * 1000)

        # Rename OHLCV keys
        item["open"] = item.pop("Open", None)
        item["high"] = item.pop("High", None)
        item["low"] = item.pop("Low", None)
        item["close"] = item.pop("Close", None)
        item["volume"] = item.pop("Volume", None)
        item["adjClose"] = item.pop("Adj Close", item.get("close"))
        item["split"] = None
        item["dividend"] = None

    # 2. Splits lookup
    splits_map = {}
    if splits_df is not None and not splits_df.empty:
        for split in map_eodhd_splits_data_to_models(splits_df, request_id) or []:
            if split and split.date:
                splits_map[split.date] = f"{split.split_to}:{split.split_from}"

    # 3. Dividends lookup
    dividends_map = {}
    if dividends_df is not None and not dividends_df.empty:
        for dividend in (
            map_eodhd_dividends_data_to_models(dividends_df, request_id) or []
        ):
            if dividend and dividend.date:
                dividends_map[dividend.date] = dividend.dividend

    # 4. Merge
    for item in chart_list:
        timestamp_str = item.get("timestamp")
        if timestamp_str:
            try:
                item_date = datetime.fromisoformat(timestamp_str).date()
                if item_date in splits_map:
                    item["split"] = splits_map[item_date]
                if item_date in dividends_map:
                    item["dividend"] = dividends_map[item_date]
            except (TypeError, ValueError):
                continue

    logger.info(
        f"{log_prefix} Finished mapping {len(chart_list)} data points with events."
    )
    return chart_list

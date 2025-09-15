# backend/core.ppers/eodhd/ohlcv_mapper.py
# ==============================================================================
# Mappers for EODHD OHLCV (Open, High, Low, Close, Volume) data.
# ==============================================================================
import pandas as pd
from typing import Any, TYPE_CHECKING
import time

from ....core.helpers import parse_optional_float, parse_optional_int
from .helpers import preprocess_ohlcv_dataframe

# --- Base Mapper Imports ---
from ._mapper_base import logger

# --- Pydantic Models ---
if TYPE_CHECKING:
    from ..models.stock import CompanyPriceHistoryEntry

# --- Configuration Import ---


# MAPPER 1: Pydantic Models (CompanyPriceHistoryEntry) - Uses 'time' (seconds), 'adj_close'
def map_eodhd_ohlcv_to_price_history_entries(
    ohlcv_df: pd.DataFrame | None, request_id: str, interval: str
) -> list["CompanyPriceHistoryEntry"] | None:
    """
    Maps an OHLCV DataFrame to a list of CompanyPriceHistoryEntry Pydantic models.
    """
    # Actual import for runtime
    from ..models.stock import CompanyPriceHistoryEntry

    log_prefix_base = "PriceHistoryMapper"
    log_prefix = f"[{request_id}][{log_prefix_base}:{interval}]"
    logger.info(f"{log_prefix} Starting mapping to Pydantic models..")

    processed_df = preprocess_ohlcv_dataframe(
        ohlcv_df, request_id, interval, log_prefix_base
    )

    if processed_df is None:
        logger.error(f"{log_prefix} Mapping failed due to preprocessing error.")
        return None
    if processed_df.empty:
        logger.info(
            f"{log_prefix} DataFrame is empty after preprocessing. Returning empty list."
        )
        return []

    price_history_entries: list[CompanyPriceHistoryEntry] = []
    skipped_count = 0
    processed_count = 0
    time.monotonic()

    if "Adj Close" not in processed_df.columns:
        logger.warning(f"{log_prefix} 'Adj Close' column missing. Adding as NaN.")
        processed_df["Adj Close"] = pd.NA
    if "Volume" not in processed_df.columns:
        logger.error(
            f"{log_prefix} 'Volume' column missing after preprocessing, this should not happen."
        )
        processed_df["Volume"] = 0

    for row in processed_df.itertuples(index=True, name="OHLCVRow"):
        point_log_prefix = (
            f"{log_prefix}[Date:{row.Index.strftime('%Y-%m-%d %H:%M:%S%Z')}]"
        )
        try:
            unix_ts_seconds = int(row.Index.timestamp())

            if unix_ts_seconds <= 0:
                skipped_count += 1
                continue

            o = parse_optional_float(
                getattr(row, "Open", None), context=f"{point_log_prefix}:Open"
            )
            h = parse_optional_float(
                getattr(row, "High", None), context=f"{point_log_prefix}:High"
            )
            low = parse_optional_float(
                getattr(row, "Low", None), context=f"{point_log_prefix}:Low"
            )
            c = parse_optional_float(
                getattr(row, "Close", None), context=f"{point_log_prefix}:Close"
            )
            adj_c = parse_optional_float(
                getattr(row, "Adj_Close", None), context=f"{point_log_prefix}:AdjClose"
            )
            v = parse_optional_int(
                getattr(row, "Volume", 0), context=f"{point_log_prefix}:Volume"
            )

            if o is None or h is None or low is None or c is None:
                skipped_count += 1
                continue

            entry_data = {
                "time": unix_ts_seconds,
                "open": o,
                "high": h,
                "low": low,
                "close": c,
                "adj_close": adj_c,
                "volume": v,
            }
            price_history_entries.append(CompanyPriceHistoryEntry(**entry_data))
            processed_count += 1
        except Exception as e_point:
            logger.error(
                f"{point_log_prefix} Skipping row due to unexpected error: {e_point}.",
                exc_info=True,
            )
            skipped_count += 1

    logger.info(
        f"{log_prefix} Pydantic mapping complete. Mapped: {processed_count}, Skipped: {skipped_count}."
    )
    return price_history_entries


# MAPPER 2: Frontend/Chart List (t, o, h, l, c, v) - Uses 't' (milliseconds)
def map_eodhd_ohlcv_df_to_frontend_list(
    ohlcv_df: pd.DataFrame | None, request_id: str, interval: str
) -> list[dict[str, Any]] | None:
    """
    Maps an OHLCV DataFrame to a list of standardized dictionaries for frontend/charting.
    """
    log_prefix_base = "FrontendListMapper"
    log_prefix = f"[{request_id}][{log_prefix_base}:{interval}]"
    logger.info(f"{log_prefix} Starting mapping to frontend list format..")

    processed_df = preprocess_ohlcv_dataframe(
        ohlcv_df, request_id, interval, log_prefix_base
    )

    if processed_df is None:
        logger.error(f"{log_prefix} Mapping failed due to preprocessing error.")
        return None
    if processed_df.empty:
        logger.info(
            f"{log_prefix} DataFrame is empty after preprocessing. Returning empty list."
        )
        return []

    mapped_list: list[dict[str, Any]] = []
    skipped_count = 0
    processed_count = 0

    for row in processed_df.itertuples(index=True, name="OHLCVRow"):
        point_log_prefix = (
            f"{log_prefix}[Date:{row.Index.strftime('%Y-%m-%d %H:%M:%S%Z')}]"
        )
        try:
            unix_ts_milliseconds = int(row.Index.timestamp() * 1000)

            if unix_ts_milliseconds <= 0:
                skipped_count += 1
                continue

            o = parse_optional_float(
                getattr(row, "Open", None), context=f"{point_log_prefix}:Open"
            )
            h = parse_optional_float(
                getattr(row, "High", None), context=f"{point_log_prefix}:High"
            )
            low = parse_optional_float(
                getattr(row, "Low", None), context=f"{point_log_prefix}:Low"
            )
            c = parse_optional_float(
                getattr(row, "Close", None), context=f"{point_log_prefix}:Close"
            )
            v = parse_optional_int(
                getattr(row, "Volume", 0), context=f"{point_log_prefix}:Volume"
            )

            if o is None or h is None or low is None or c is None:
                skipped_count += 1
                continue

            mapped_point = {
                "t": unix_ts_milliseconds,
                "o": o,
                "h": h,
                "l": low,
                "c": c,
                "v": v,
            }
            mapped_list.append(mapped_point)
            processed_count += 1
        except Exception as e_point:
            logger.error(
                f"{point_log_prefix} Skipping row due to unexpected error: {e_point}.",
                exc_info=True,
            )
            skipped_count += 1

    logger.info(
        f"{log_prefix} Frontend list mapping complete. Mapped: {processed_count}, Skipped: {skipped_count}."
    )
    return mapped_list

# backend/core.ppers/eodhd/helpers.py
# ==============================================================================
# Helper functions for processing data from the EOD Historical Data API.
# This module contains shared preprocessing logic used by other mappers.
# ==============================================================================
import pandas as pd
import time

# --- Base Mapper Imports (e.g., Logger) ---
try:
    from ._mapper_base import logger
except ImportError:
    # Fallback logger if run standalone, though not expected in production
    import logging

    logging.basicConfig(level="INFO")
    logger = logging.getLogger(__name__)

# --- Configuration Import ---
try:
    from ..config import settings
except ImportError:
    logger.warning(
        "Could not import settings from config. Using dummy settings for NODE_ENV."
    )

    class DummySettings:
        class DummyEnv:
            NODE_ENV = "production"

        ENVIRONMENT = DummyEnv()

    settings = DummySettings()


def preprocess_ohlcv_dataframe(
    ohlcv_df: pd.DataFrame, request_id: str, interval: str, log_prefix_base: str
) -> pd.DataFrame | None:
    """
    Helper function to preprocess OHLCV DataFrame: validation, UTC conversion,
    DWM filtering, sorting, and deduplication.
    Returns the processed DataFrame or None if critical validation fails.
    """
    func_name = "preprocess_ohlcv_dataframe"  # Renamed to be public
    log_prefix = f"[{request_id}][{log_prefix_base}:{func_name}:{interval}]"

    if ohlcv_df is None or not isinstance(ohlcv_df, pd.DataFrame):
        logger.error(
            f"{log_prefix} Preprocessing failed: Input is None or not a DataFrame."
        )
        return None
    if ohlcv_df.empty:
        logger.info(f"{log_prefix} Input DataFrame is empty. No preprocessing needed.")
        return ohlcv_df.copy()

    logger.debug(f"{log_prefix} Initial input DF shape: {ohlcv_df.shape}")

    df_copy = ohlcv_df.copy()  # Work on a copy

    # --- Index Validation and UTC Conversion ---
    if not isinstance(df_copy.index, pd.DatetimeIndex):
        try:
            original_index_type = type(df_copy.index)
            df_copy.index = pd.to_datetime(df_copy.index, utc=True)
            if not isinstance(df_copy.index, pd.DatetimeIndex):
                raise TypeError("Conversion to DatetimeIndex failed.")
            logger.warning(
                f"{log_prefix} Converted DataFrame index from {original_index_type} to DatetimeIndex (UTC)."
            )
        except Exception as e_conv:
            logger.error(
                f"{log_prefix} Preprocessing failed: DataFrame index is not DatetimeIndex (Type: {type(df_copy.index)}) and conversion failed: {e_conv}."
            )
            return None
    else:
        if df_copy.index.tz is None:
            logger.warning(
                f"{log_prefix} Input DatetimeIndex is timezone-naive. Assuming and localizing to UTC."
            )
            try:
                df_copy.index = df_copy.index.tz_localize("UTC")
            except TypeError:  # Already localized or ambiguous time
                logger.warning(
                    f"{log_prefix} Could not localize naive index to UTC, attempting tz_convert."
                )
                try:
                    df_copy.index = df_copy.index.tz_convert("UTC")
                except Exception as e_tz_convert:
                    logger.error(
                        f"{log_prefix} Preprocessing failed: Failed to convert index to UTC: {e_tz_convert}"
                    )
                    return None
        elif str(df_copy.index.tz).upper() != "UTC":
            logger.warning(
                f"{log_prefix} Input DatetimeIndex has timezone '{df_copy.index.tz}'. Converting to UTC."
            )
            try:
                df_copy.index = df_copy.index.tz_convert("UTC")
            except Exception as e_tz_convert:
                logger.error(
                    f"{log_prefix} Preprocessing failed: Failed to convert index to UTC: {e_tz_convert}"
                )
                return None

    # --- Column Validation ---
    required_cols = {"Open", "High", "Low", "Close"}
    available_cols = set(df_copy.columns)
    missing_required = required_cols - available_cols

    if missing_required:
        logger.error(
            f"{log_prefix} Preprocessing failed: Missing critical UPPERCASE OHLC columns: {missing_required}. Available: {list(available_cols)}."
        )
        return None

    # Ensure Volume column exists, fill with 0 if missing (as int)
    if "Volume" not in df_copy.columns:
        logger.warning(f"{log_prefix} 'Volume' column missing. Adding as 0.")
        df_copy["Volume"] = 0
    df_copy["Volume"] = (
        pd.to_numeric(df_copy["Volume"], errors="coerce").fillna(0).astype(int)
    )

    pre_processing_start = time.monotonic()

    # --- Weekend Filtering (DWM) ---
    normalized_interval = interval.upper() if interval else ""
    is_dwm_interval = any(char in normalized_interval for char in ["D", "W", "M"])
    len(df_copy)

    if is_dwm_interval:
        try:
            if df_copy.index.tz is None or str(df_copy.index.tz).upper() != "UTC":
                df_copy.index = df_copy.index.tz_convert("UTC")

            original_index_name = df_copy.index.name
            df_copy = df_copy[df_copy.index.dayofweek < 5]  # Monday=0, Sunday=6
            df_copy.index.name = original_index_name
        except Exception as e_filter_dwm:
            logger.error(
                f"{log_prefix} ERROR during weekend filter: {e_filter_dwm}",
                exc_info=True,
            )
            logger.warning(
                f"{log_prefix} Proceeding without weekend filter due to error."
            )

    # --- Sorting and Deduplication ---
    if not df_copy.index.is_monotonic_increasing:
        df_copy.sort_index(inplace=True)

    rows_before_dedup = len(df_copy)
    if not df_copy.index.is_unique:
        logger.warning(
            f"{log_prefix} Index contains duplicates. Deduplicating, keeping 'last' entry.."
        )
        df_copy = df_copy[~df_copy.index.duplicated(keep="last")]
        dedup_rows_removed = rows_before_dedup - len(df_copy)
        logger.info(
            f"{log_prefix} Deduplication removed {dedup_rows_removed} duplicate rows."
        )

    logger.debug(
        f"{log_prefix} Pre-processing duration: {time.monotonic() - pre_processing_start:.4f}s. Final DF shape: {df_copy.shape}"
    )
    return df_copy

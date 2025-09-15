# backend/core.ppers/eodhd/events_mapper.py
# ==============================================================================
# Mappers for EODHD corporate events data (Splits, Dividends).
# ==============================================================================
import pandas as pd
from typing import TYPE_CHECKING
from datetime import date, datetime

# --- Core Helper Imports ---
try:
    from ....core.helpers import parse_optional_float
except ImportError as e:
    import logging

    logging.basicConfig(level="CRITICAL")
    logging.getLogger(__name__).critical(
        f"FATAL ERROR: Cannot import helpers: {e}", exc_info=True
    )
    raise RuntimeError(f"EODHD Events mapper failed initialization: {e}") from e

# --- Base Mapper Imports ---
try:
    from ._mapper_base import logger
except ImportError:
    import logging

    logging.basicConfig(level="INFO")
    logger = logging.getLogger(__name__)

# --- Pydantic Models ---
if TYPE_CHECKING:
    from ..models.stock import StockSplitData, DividendData


# --- Splits Mapper ---
def map_eodhd_splits_data_to_models(
    splits_df: pd.DataFrame | None, request_id: str
) -> list["StockSplitData"] | None:
    from ..models.stock import StockSplitData

    func_name = "map_eodhd_splits_data_to_models"
    log_prefix = f"[{request_id}][{func_name}]"
    logger.info(f"{log_prefix} Starting mapping..")

    if splits_df is None or not isinstance(splits_df, pd.DataFrame):
        logger.error(f"{log_prefix} Mapping failed: Input is None or not a DataFrame.")
        return None
    if splits_df.empty:
        logger.info(f"{log_prefix} Input DataFrame is empty. Returning empty list.")
        return []

    df_copy = splits_df.copy()

    if not isinstance(df_copy.index, pd.DatetimeIndex):
        try:
            df_copy.index = pd.to_datetime(df_copy.index)
        except Exception as e_conv:
            logger.error(
                f"{log_prefix} Mapping failed: Splits index not DatetimeIndex and conversion failed: {e_conv}"
            )
            return None

    if "split_ratio_str" not in df_copy.columns:
        logger.error(f"{log_prefix} Mapping failed: Missing 'split_ratio_str' column.")
        return None

    split_data_list: list[StockSplitData] = []
    skipped_count = 0
    processed_count = 0

    for idx_date, row in df_copy.iterrows():
        point_log_prefix = f"{log_prefix}[Date:{idx_date.strftime('%Y-%m-%d')}]"
        try:
            split_date: date | None = None
            if isinstance(idx_date, (pd.Timestamp, datetime)):
                split_date = idx_date.date()
            else:
                skipped_count += 1
                continue

            ratio_str = row["split_ratio_str"]
            if not isinstance(ratio_str, str) or ":" not in ratio_str:
                skipped_count += 1
                continue

            parts = ratio_str.split(":", 1)
            split_to_val = parse_optional_float(parts[0].strip())
            split_from_val = parse_optional_float(parts[1].strip())

            if split_to_val is None or split_from_val is None or split_from_val == 0:
                skipped_count += 1
                continue

            entry_data = {
                "date": split_date,
                "split_ratio_str": ratio_str,
                "split_to": split_to_val,
                "split_from": split_from_val,
            }
            split_data_list.append(StockSplitData(**entry_data))
            processed_count += 1
        except Exception as e_point:
            logger.error(
                f"{point_log_prefix} Skipping row due to unexpected error: {e_point}.",
                exc_info=True,
            )
            skipped_count += 1

    logger.info(
        f"{log_prefix} Mapping complete. Mapped: {processed_count}, Skipped: {skipped_count}."
    )
    return split_data_list


# --- Dividends Mapper ---
def map_eodhd_dividends_data_to_models(
    dividends_df: pd.DataFrame | None, request_id: str
) -> list["DividendData"] | None:
    from ..models.stock import DividendData

    func_name = "map_eodhd_dividends_data_to_models"
    log_prefix = f"[{request_id}][{func_name}]"
    logger.info(f"{log_prefix} Starting mapping..")

    if dividends_df is None or not isinstance(dividends_df, pd.DataFrame):
        logger.error(f"{log_prefix} Mapping failed: Input is None or not a DataFrame.")
        return None
    if dividends_df.empty:
        logger.info(f"{log_prefix} Input DataFrame is empty. Returning empty list.")
        return []

    df_copy = dividends_df.copy()
    required_cols = {"date", "dividend_amount"}
    if not required_cols.issubset(df_copy.columns):
        return None

    dividend_data_list: list[DividendData] = []
    skipped_count = 0
    processed_count = 0
    optional_date_cols = {"declarationDate", "recordDate", "paymentDate"}

    for index, row in df_copy.iterrows():
        point_log_prefix = f"{log_prefix}[Row:{index}]"
        try:
            ex_div_date = pd.to_datetime(row["date"]).date()
            amount = parse_optional_float(row["dividend_amount"])
            if amount is None:
                skipped_count += 1
                continue

            entry_data = {
                "date": ex_div_date,
                "dividend": amount,
                "currency": str(row.get("currency"))
                if pd.notna(row.get("currency"))
                else None,
                "unadjusted_value": parse_optional_float(row.get("unadjustedValue")),
                "declaration_date": None,
                "record_date": None,
                "payment_date": None,
            }

            for col_name in optional_date_cols:
                pydantic_col_name = col_name.replace("Date", "_date")
                if col_name in row and pd.notna(row[col_name]):
                    entry_data[pydantic_col_name] = pd.to_datetime(row[col_name]).date()

            dividend_data_list.append(DividendData(**entry_data))
            processed_count += 1
        except Exception as e_point:
            logger.error(
                f"{point_log_prefix} Skipping row due to unexpected error: {e_point}.",
                exc_info=True,
            )
            skipped_count += 1

    logger.info(
        f"{log_prefix} Mapping complete. Mapped: {processed_count}, Skipped: {skipped_count}."
    )
    return dividend_data_list

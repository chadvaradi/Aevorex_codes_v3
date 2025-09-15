# Aevorex_codes/modules/financehub/backend/core/mappers/eodhd/price.py
from __future__ import annotations

import pandas as pd
from typing import Any, TYPE_CHECKING

from backend.core.helpers import parse_optional_float
from backend.core.mappers._mapper_base import logger
from backend.models.stock import CompanyPriceHistoryEntry

if TYPE_CHECKING:
    from ....models import CompanyPriceHistoryEntry


def _preprocess_ohlcv_dataframe(
    ohlcv_df: pd.DataFrame, request_id: str, interval: str, log_prefix_base: str
) -> pd.DataFrame | None:
    func_name = "_preprocess_ohlcv_dataframe"
    log_prefix = f"[{request_id}][{log_prefix_base}:{func_name}:{interval}]"

    if ohlcv_df is None or not isinstance(ohlcv_df, pd.DataFrame):
        logger.error(
            f"{log_prefix} Preprocessing failed: Input is None or not a DataFrame."
        )
        return None
    if ohlcv_df.empty:
        return ohlcv_df.copy()

    df_copy = ohlcv_df.copy()

    if not isinstance(df_copy.index, pd.DatetimeIndex):
        try:
            df_copy.index = pd.to_datetime(df_copy.index, utc=True)
        except Exception as e_conv:
            logger.error(
                f"{log_prefix} Preprocessing failed: DataFrame index is not DatetimeIndex and conversion failed: {e_conv}."
            )
            return None
    else:
        if df_copy.index.tz is None:
            df_copy.index = df_copy.index.tz_localize("UTC")
        elif str(df_copy.index.tz).upper() != "UTC":
            df_copy.index = df_copy.index.tz_convert("UTC")

    required_cols = {"Open", "High", "Low", "Close"}
    if not required_cols.issubset(set(df_copy.columns)):
        missing_required = required_cols - set(df_copy.columns)
        logger.error(
            f"{log_prefix} Preprocessing failed: Missing critical UPPERCASE OHLC columns: {missing_required}."
        )
        return None

    if "Volume" not in df_copy.columns:
        df_copy["Volume"] = 0
    df_copy["Volume"] = (
        pd.to_numeric(df_copy["Volume"], errors="coerce").fillna(0).astype(int)
    )

    df_copy.sort_index(inplace=True)
    df_copy = df_copy[~df_copy.index.duplicated(keep="last")]

    return df_copy


def map_eodhd_ohlcv_to_price_history_entries(
    ohlcv_df: pd.DataFrame | None, request_id: str, interval: str
) -> list["CompanyPriceHistoryEntry"] | None:
    from ....models import CompanyPriceHistoryEntry

    log_prefix_base = "PriceHistoryMapper"
    log_prefix = f"[{request_id}][{log_prefix_base}:{interval}]"

    processed_df = _preprocess_ohlcv_dataframe(
        ohlcv_df, request_id, interval, log_prefix_base
    )

    if processed_df is None:
        return None
    if processed_df.empty:
        return []

    price_history_entries: list[CompanyPriceHistoryEntry] = []

    if "Adj Close" not in processed_df.columns:
        processed_df["Adj Close"] = pd.NA

    for row in processed_df.itertuples(index=True, name="OHLCVRow"):
        try:
            unix_ts_seconds = int(row.Index.timestamp())

            open_val = parse_optional_float(row.Open)
            high_val = parse_optional_float(row.High)
            low_val = parse_optional_float(row.Low)
            close_val = parse_optional_float(row.Close)
            adj_close_val = parse_optional_float(row._asdict().get("Adj Close"))

            entry_data = {
                "time": unix_ts_seconds,
                "open": open_val if open_val is not None else 0.0,
                "high": high_val if high_val is not None else 0.0,
                "low": low_val if low_val is not None else 0.0,
                "close": close_val if close_val is not None else 0.0,
                "adj_close": adj_close_val,
                "volume": row.Volume,
            }
            price_history_entries.append(CompanyPriceHistoryEntry(**entry_data))
        except Exception as e:
            logger.error(
                f"{log_prefix} Error processing row {row.Index}: {e}", exc_info=True
            )

    return price_history_entries


def map_eodhd_ohlcv_df_to_frontend_list(
    ohlcv_df: pd.DataFrame | None, request_id: str, interval: str
) -> list[dict[str, Any]] | None:
    log_prefix_base = "FrontendListMapper"
    log_prefix = f"[{request_id}][{log_prefix_base}:{interval}]"

    processed_df = _preprocess_ohlcv_dataframe(
        ohlcv_df, request_id, interval, log_prefix_base
    )

    if processed_df is None:
        return None
    if processed_df.empty:
        return []

    try:
        df_renamed = processed_df.rename(
            columns={"Open": "o", "High": "h", "Low": "l", "Close": "c", "Volume": "v"}
        )
        df_renamed["t"] = (df_renamed.index.astype(int) / 10**9).astype(int)

        final_cols = ["t", "o", "h", "l", "c", "v"]
        chart_list = df_renamed[final_cols].to_dict(orient="records")

        return chart_list
    except Exception as e:
        logger.error(
            f"{log_prefix} An unexpected error occurred during final mapping: {e}",
            exc_info=True,
        )
        return None


def map_eodhd_data_to_chart_ready_format(
    ohlcv_df: pd.DataFrame,
    splits_df: pd.DataFrame | None,
    dividends_df: pd.DataFrame | None,
    request_id: str,
    interval: str = "d",
) -> list[dict[str, Any]]:
    # This is a placeholder for a more complex implementation.
    # For now, it just maps the OHLCV data.
    return map_eodhd_ohlcv_df_to_frontend_list(ohlcv_df, request_id, interval) or []


def map_eodhd_ohlcv_to_company_price_history(
    ohlcv_df: pd.DataFrame | None, request_id: str, interval: str
) -> list["CompanyPriceHistoryEntry"] | None:
    return map_eodhd_ohlcv_to_price_history_entries(ohlcv_df, request_id, interval)

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def safe_get(
    df: pd.DataFrame | None,
    index: Any,
    column: str,
    default: Any = None,
    *,
    context: str = "",
) -> Any:
    """
    Safely retrieves a value from a DataFrame by index and column, returning a
    default value if the index/column doesn't exist or the value is NaN.
    """
    if df is None or df.empty:
        return default
    try:
        if index not in df.index:
            return default

        value = df.at[index, column]

        return default if pd.isna(value) else value
    except (KeyError, IndexError):
        return default
    except Exception as e:
        logger.error(
            f"Unexpected error in safe_get for index '{index}', column '{column}': {e}",
            exc_info=True,
        )
        return default


def _ensure_datetime_index(
    df: pd.DataFrame, function_name: str = "caller"
) -> pd.DataFrame | None:
    """
    Ensures that the DataFrame has a DatetimeIndex. Tries to set it from common
    date/timestamp columns if not already set.
    """
    if isinstance(df.index, pd.DatetimeIndex):
        return df

    common_date_cols = ["date", "timestamp", "Date", "reportDate", "filing_date"]

    for col in common_date_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                df = df.dropna(subset=[col])
                df = df.set_index(col)
                if isinstance(df.index, pd.DatetimeIndex):
                    logger.debug(
                        f"Set DatetimeIndex from column '{col}' for {function_name}."
                    )
                    return df
            except Exception:
                continue

    logger.error(f"Could not ensure DatetimeIndex for DataFrame in {function_name}.")
    return None

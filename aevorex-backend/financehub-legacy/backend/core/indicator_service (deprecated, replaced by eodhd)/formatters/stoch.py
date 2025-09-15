import pandas as pd
import time
import logging
from typing import List, Optional

from backend.models.stock import STOCHPoint
from backend.core.helpers import parse_optional_float

logger = logging.getLogger(__name__)


def format_stoch_series(
    df: pd.DataFrame, k_col: str, d_col: str
) -> Optional[List[STOCHPoint]]:
    """
    Formats a DataFrame with Stochastic Oscillator data (%K and %D) into a list of STOCHPoint objects.
    """
    func_name = "format_stoch_series"
    required_cols = {k_col, d_col}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        logger.warning(f"[{func_name}] Missing columns: {missing}. Cannot proceed.")
        return None
    if not isinstance(df.index, pd.DatetimeIndex):
        logger.error(f"[{func_name}] Index must be a DatetimeIndex.")
        return None
    try:
        if df.index.tz is None:
            df = df.tz_localize("UTC", ambiguous="infer", nonexistent="shift_forward")
        elif str(df.index.tz) != "UTC":
            df = df.tz_convert("UTC")
    except Exception as tz_e:
        logger.error(f"[{func_name}] Failed to ensure UTC timezone. Error: {tz_e}")
        return None
    if df.empty:
        logger.warning(f"[{func_name}] Input DataFrame is empty. Returning None.")
        return None

    points: List[STOCHPoint] = []
    valid_count = 0
    error_count = 0
    start_time = time.monotonic()

    for timestamp, row in df[[k_col, d_col]].iterrows():
        try:
            k_val = parse_optional_float(row[k_col])
            d_val = parse_optional_float(row[d_col])

            if k_val is None or d_val is None:
                error_count += 1
                continue

            unix_timestamp_seconds = int(timestamp.timestamp())
            points.append(STOCHPoint(t=unix_timestamp_seconds, k=k_val, d=d_val))
            valid_count += 1
        except Exception as e:
            logger.error(
                f"[{func_name}] Error processing row at {timestamp}. Error: {e}",
                exc_info=True,
            )
            error_count += 1

    duration = time.monotonic() - start_time
    if not points:
        logger.warning(
            f"[{func_name}] Formatted 0 valid points (Errors: {error_count}, Time: {duration:.4f}s)."
        )
        return None

    logger.info(
        f"[{func_name}] Formatted {valid_count} points (Errors: {error_count}, Time: {duration:.4f}s)."
    )
    return points

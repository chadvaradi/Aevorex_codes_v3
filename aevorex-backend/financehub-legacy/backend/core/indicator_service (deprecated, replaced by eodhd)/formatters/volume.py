import pandas as pd
import time
import logging
from typing import List, Optional, Final
from pydantic import ValidationError

from backend.models.stock import VolumePoint
from backend.core.helpers import parse_optional_float

logger = logging.getLogger(__name__)

VOLUME_UP_COLOR: Final[str] = "#26A69A"
VOLUME_DOWN_COLOR: Final[str] = "#EF5350"


def format_volume_series(
    df: pd.DataFrame, vol_col: str, open_col: str, close_col: str
) -> Optional[List[VolumePoint]]:
    func_name = "format_volume_series"
    required_cols = {vol_col, open_col, close_col}
    if not required_cols.issubset(df.columns):
        missing = required_cols - set(df.columns)
        logger.warning(
            f"[{func_name}] Missing columns for volume formatting: {missing}. Cannot proceed."
        )
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

    points: List[VolumePoint] = []
    valid_count = 0
    conversion_errors = 0
    validation_errors = 0
    nan_inf_count = 0
    start_time = time.monotonic()

    for timestamp, row in df[[vol_col, open_col, close_col]].iterrows():
        try:
            volume_f = parse_optional_float(row[vol_col])
            open_f = parse_optional_float(row[open_col])
            close_f = parse_optional_float(row[close_col])

            if volume_f is None or open_f is None or close_f is None:
                nan_inf_count += 1
                continue

            volume_int = int(round(volume_f))
            color = VOLUME_UP_COLOR if close_f >= open_f else VOLUME_DOWN_COLOR
            unix_timestamp_seconds = int(timestamp.timestamp())

            volume_point = VolumePoint(
                t=unix_timestamp_seconds, value=volume_int, color=color
            )
            points.append(volume_point)
            valid_count += 1

        except (ValueError, TypeError, OverflowError) as e_conv:
            logger.warning(
                f"[{func_name}] Skipping point at {timestamp}: Could not convert value. Error: {e_conv}"
            )
            conversion_errors += 1
        except ValidationError as e_val:
            logger.warning(
                f"[{func_name}] Skipping point at {timestamp}: VolumePoint validation failed. Error: {e_val}"
            )
            validation_errors += 1

    duration = time.monotonic() - start_time
    total_errors = conversion_errors + validation_errors + nan_inf_count
    if not points:
        logger.warning(
            f"[{func_name}] Formatted 0 valid points. Total Errors: {total_errors}, Time: {duration:.4f}s."
        )
        return None
    else:
        logger.info(
            f"[{func_name}] Formatted {valid_count} valid points. Total Errors: {total_errors}, Time: {duration:.4f}s."
        )
        return points

import pandas as pd
import math
import time
import logging
from typing import List, Optional

from backend.models.stock import IndicatorPoint
from ._base_formatter import validate_series

logger = logging.getLogger(__name__)


def format_simple_series(
    series: Optional[pd.Series], series_name: str
) -> Optional[List[IndicatorPoint]]:
    """
    Formats a validated pandas Series into a list of IndicatorPoint objects.
    Assumes series has been pre-validated by validate_series.
    """
    validated_series = validate_series(series, series_name)
    if validated_series is None:
        return None

    points: List[IndicatorPoint] = []
    valid_count = 0
    nan_count = 0
    inf_count = 0
    error_count = 0
    start_time = time.monotonic()

    try:
        timestamps = validated_series.index
        values = validated_series.values
    except Exception as e:
        logger.error(
            f"Error accessing series index/values for '{series_name}': {e}",
            exc_info=True,
        )
        return None

    for i in range(len(timestamps)):
        ts = timestamps[i]
        raw_value = values[i]

        try:
            value_f = float(raw_value)
            if math.isnan(value_f):
                nan_count += 1
                continue
            if math.isinf(value_f):
                inf_count += 1
                continue

            unix_timestamp_seconds = int(ts.timestamp())
            points.append(IndicatorPoint(t=unix_timestamp_seconds, value=value_f))
            valid_count += 1

        except (ValueError, TypeError):
            error_count += 1
        except Exception as e:
            logger.error(
                f"Unexpected error formatting point for '{series_name}': Time={ts}, Value={raw_value}. Error: {e}",
                exc_info=True,
            )
            error_count += 1

    duration = time.monotonic() - start_time
    if not points:
        logger.warning(
            f"Formatted 0 valid points for indicator '{series_name}' (NaNs: {nan_count}, Infs: {inf_count}, Errors: {error_count}, Time: {duration:.4f}s). Returning None."
        )
        return None
    else:
        logger.info(
            f"Formatted {valid_count} valid points for indicator '{series_name}' (NaNs: {nan_count}, Infs: {inf_count}, Errors: {error_count}, Time: {duration:.4f}s)."
        )
        return points

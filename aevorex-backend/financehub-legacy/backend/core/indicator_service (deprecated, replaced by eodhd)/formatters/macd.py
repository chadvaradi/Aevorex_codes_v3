import pandas as pd
import math
import time
import logging
from typing import List, Optional, Final

from backend.models.stock import MACDHistPoint
from ._base_formatter import validate_series

logger = logging.getLogger(__name__)

MACD_HIST_UP_COLOR: Final[str] = "#26A69A"
MACD_HIST_DOWN_COLOR: Final[str] = "#EF5350"


def format_macd_hist_series(
    series: Optional[pd.Series], series_name: str
) -> Optional[List[MACDHistPoint]]:
    """
    Formats a validated pandas Series into a list of MACDHistPoint objects.
    """
    validated_series = validate_series(series, series_name)
    if validated_series is None:
        return None

    points: List[MACDHistPoint] = []
    valid_count = 0
    nan_inf_error_count = 0
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
            if math.isnan(value_f) or math.isinf(value_f):
                nan_inf_error_count += 1
                continue

            color = MACD_HIST_UP_COLOR if value_f >= 0 else MACD_HIST_DOWN_COLOR
            unix_timestamp_seconds = int(ts.timestamp())
            points.append(
                MACDHistPoint(t=unix_timestamp_seconds, value=value_f, color=color)
            )
            valid_count += 1
        except (ValueError, TypeError):
            nan_inf_error_count += 1
        except Exception as e:
            logger.error(
                f"Unexpected error formatting MACD Hist point: Time={ts}, Value={raw_value}. Error: {e}",
                exc_info=True,
            )
            nan_inf_error_count += 1

    duration = time.monotonic() - start_time
    if not points:
        logger.warning(
            f"Formatted 0 valid points for '{series_name}' (Errors: {nan_inf_error_count}, Time: {duration:.4f}s)."
        )
        return None

    logger.info(
        f"Formatted {valid_count} points for '{series_name}' (Errors: {nan_inf_error_count}, Time: {duration:.4f}s)."
    )
    return points

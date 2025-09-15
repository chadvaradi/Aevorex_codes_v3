import pandas as pd
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def validate_series(series: pd.Series, series_name: str) -> Optional[pd.Series]:
    """
    Validates a pandas Series for formatting. Checks for None, type, emptiness, and DatetimeIndex.
    Converts index to UTC if necessary.
    Returns the validated (and possibly timezone-converted) Series, or None if validation fails.
    """
    if series is None:
        return None
    if not isinstance(series, pd.Series):
        logger.warning(
            f"Cannot format '{series_name}': Input is not a pandas Series (type: {type(series).__name__})."
        )
        return None
    if series.empty:
        logger.debug(f"Cannot format '{series_name}': Input Series is empty.")
        return None
    if not isinstance(series.index, pd.DatetimeIndex):
        logger.error(
            f"Cannot format '{series_name}': Input Series must have a DatetimeIndex."
        )
        return None

    # Ensure index timezone is UTC
    try:
        if series.index.tz is None:
            series = series.tz_localize(
                "UTC", ambiguous="infer", nonexistent="shift_forward"
            )
        elif str(series.index.tz) != "UTC":
            series = series.tz_convert("UTC")
        return series
    except Exception as tz_e:
        logger.error(
            f"Cannot format '{series_name}': Failed to convert index to UTC. Error: {tz_e}"
        )
        return None

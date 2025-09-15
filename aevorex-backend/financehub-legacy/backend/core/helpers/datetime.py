"""
DateTime Helper Functions
========================

Centralized datetime utilities for the FinanceHub application.
Consolidated from various utils/helpers modules.
"""

import logging
from datetime import datetime, timezone, tzinfo
from typing import Any

import pandas as pd

try:
    from backend.utils.logger_config import get_logger

    package_logger = get_logger(f"aevorex_finbot.core.helpers.{__name__}")
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    package_logger = logging.getLogger(
        f"aevorex_finbot.core.helpers_fallback.{__name__}"
    )

MIN_VALID_TIMESTAMP_THRESHOLD_SECONDS: float = 631152000.0  # 1990-01-01 00:00:00 UTC


def parse_string_to_aware_datetime(
    value: Any, *, context: str = "", target_tz: tzinfo = timezone.utc
) -> datetime | None:
    """
    Különböző bemeneti formátumokból (string, int/float timestamp, datetime)
    "aware" Python datetime objektumot hoz létre, a megadott cél időzónában (alapértelmezetten UTC).
    """
    log_prefix = f"[{context}] " if context and context.strip() else ""

    if value is None:
        return None

    dt_object: datetime | None = None

    try:
        if isinstance(value, datetime):
            dt_object = value

        elif isinstance(value, (int, float)):
            numeric_ts = float(value)
            if numeric_ts < MIN_VALID_TIMESTAMP_THRESHOLD_SECONDS:
                return None
            dt_object = datetime.fromtimestamp(numeric_ts, tz=timezone.utc)

        elif isinstance(value, str):
            # Prevent ghost parsing of invalid dates like "0000-00-00"
            if value.strip() in ["0000-00-00", "00-00-0000", "0000/00/00"]:
                return None

            pd_ts = pd.to_datetime(
                value,
                errors="coerce",
                utc=True,
                infer_datetime_format=True,
                dayfirst=False,
            )
            if pd.isna(pd_ts):
                return None
            else:
                dt_object = pd_ts.to_pydatetime()

        if dt_object is None:
            return None

        if dt_object.tzinfo is None:
            dt_object = dt_object.replace(tzinfo=target_tz)
        else:
            dt_object = dt_object.astimezone(target_tz)

        return dt_object

    except (ValueError, TypeError, pd.errors.ParserError):
        return None
    except Exception as e:
        package_logger.error(
            f"{log_prefix}parse_string_to_aware_datetime: Unexpected error parsing '{value}': {e}",
            exc_info=True,
        )
        return None


def parse_timestamp_to_iso_utc(
    timestamp: Any, *, default_tz: tzinfo | None = None, context: str = ""
) -> str | None:
    """
    Bármilyen dátum-szerű inputot (timestamp, string, datetime) UTC ISO 8601 formátumú stringgé alakít.
    """
    log_prefix = f"[{context}] " if context and context.strip() else ""
    aware_dt = parse_string_to_aware_datetime(
        timestamp, context=log_prefix, target_tz=timezone.utc
    )
    if aware_dt:
        return aware_dt.isoformat().replace("+00:00", "Z")
    return None


def format_datetime_for_api(dt: datetime) -> str:
    """
    Format datetime for API responses.

    Args:
        dt: Datetime object

    Returns:
        ISO formatted string
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def get_current_utc() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)

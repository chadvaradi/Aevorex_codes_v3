"""
Response Helpers - Utility functions for building stock responses.
Split from response_builder.py to maintain 160 LOC limit.
"""

from typing import Any
import pandas as pd
from backend.models.stock import CompanyPriceHistoryEntry
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.ResponseHelpers")


def safe_float(val: Any) -> float | None:
    """Safely convert value to float."""
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        parsed = float(val)
        return parsed if pd.notna(parsed) else None
    except Exception:
        return None


def safe_int(val: Any) -> int | None:
    """Safely convert value to int."""
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        parsed = int(val)
        return parsed
    except Exception:
        return None


def process_ohlcv_dataframe(ohlcv_df: pd.DataFrame, log_prefix: str) -> tuple:
    """Process OHLCV DataFrame into response components."""
    latest_ohlcv = None
    history_entries: list[CompanyPriceHistoryEntry] = []

    try:
        if ohlcv_df is not None and not ohlcv_df.empty:
            # Build history list
            for ts, row in ohlcv_df.iterrows():
                try:
                    entry = CompanyPriceHistoryEntry(
                        time=int(float(ts.timestamp()))
                        if hasattr(ts, "timestamp")
                        else int(ts),
                        open=float(row.get("open", row.get("o", 0) or 0)),
                        high=float(row.get("high", row.get("h", 0) or 0)),
                        low=float(row.get("low", row.get("l", 0) or 0)),
                        close=float(row.get("close", row.get("c", 0) or 0)),
                        adj_close=float(
                            row.get(
                                "adj_close",
                                row.get("adjClose", row.get("ac", 0) or 0) or 0,
                            )
                        ),
                        volume=int(row.get("volume", row.get("v", 0) or 0)),
                    )
                    history_entries.append(entry)
                except Exception:
                    # Skip malformed rows silently
                    continue

            # Latest OHLCV (simple dict allowed by model)
            last_row = ohlcv_df.iloc[-1]
            latest_ohlcv = {
                "t": int(float(last_row.name.timestamp()))
                if hasattr(last_row.name, "timestamp")
                else None,
                "o": safe_float(last_row.get("open")),
                "h": safe_float(last_row.get("high")),
                "l": safe_float(last_row.get("low")),
                "c": safe_float(last_row.get("close")),
                "v": safe_int(last_row.get("volume")),
                "time_iso": last_row.name.isoformat()
                if hasattr(last_row.name, "isoformat")
                else None,
            }
        else:
            logger.debug("%s ohlcv_df empty – history_ohlcv will be []", log_prefix)
    except Exception as exc:
        logger.warning("%s OHLCV processing failed: %s", log_prefix, exc, exc_info=True)

    return history_entries, latest_ohlcv


def process_technical_indicators(
    technical_indicators: dict[str, Any] | None, log_prefix: str
) -> dict[str, float] | None:
    """Process technical indicators into response format."""
    latest_indicators_obj: dict[str, float] | None = None
    try:
        if isinstance(technical_indicators, dict) and technical_indicators:
            latest_indicators_obj = {
                k: float(v)
                for k, v in technical_indicators.items()
                if v is not None and not pd.isna(v)
            }
            if not latest_indicators_obj:
                latest_indicators_obj = None
        else:
            logger.debug(
                "%s technical_indicators missing/invalid – set to None", log_prefix
            )
    except Exception as exc:
        logger.warning(
            "%s technical indicator processing failed: %s",
            log_prefix,
            exc,
            exc_info=True,
        )
        latest_indicators_obj = None

    return latest_indicators_obj

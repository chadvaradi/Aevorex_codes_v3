import pandas as pd
from backend.utils.logger_config import get_logger

logger = get_logger(f"aevorex_finbot.{__name__}")


def ensure_datetime_index(
    df: pd.DataFrame, function_name: str = "caller"
) -> pd.DataFrame | None:
    if not isinstance(df, pd.DataFrame):
        logger.error(
            f"[{function_name}] Invalid input: Expected pandas DataFrame, got {type(df).__name__}."
        )
        return None
    if df.empty:
        logger.warning(
            f"[{function_name}] Input DataFrame is empty. Returning empty DataFrame."
        )
        return df.copy()

    df_copy = df.copy()

    try:
        if isinstance(df_copy.index, pd.DatetimeIndex):
            logger.debug(
                f"[{function_name}] DataFrame already has DatetimeIndex. Checking timezone.."
            )
            if df_copy.index.tz is None:
                logger.debug(f"[{function_name}] Localizing naive index to UTC.")
                df_copy.index = df_copy.index.tz_localize(
                    "UTC", ambiguous="infer", nonexistent="shift_forward"
                )
            elif str(df_copy.index.tz) != "UTC":
                logger.debug(
                    f"[{function_name}] Converting existing index timezone to UTC from {df_copy.index.tz}."
                )
                df_copy.index = df_copy.index.tz_convert("UTC")
            else:
                logger.debug(f"[{function_name}] Index is already UTC.")
            return df_copy.sort_index()

        time_col = None
        possible_time_cols = ["time", "Date", "datetime", "timestamp"]
        for col in possible_time_cols:
            if col in df_copy.columns:
                time_col = col
                break
            if col.lower() in df_copy.columns:
                time_col = col.lower()
                break

        if time_col:
            logger.debug(
                f"[{function_name}] Found potential time column: '{time_col}'. Converting to DatetimeIndex (UTC).."
            )
            df_copy[time_col] = pd.to_datetime(
                df_copy[time_col], errors="coerce", utc=True, infer_datetime_format=True
            )
            original_rows = len(df_copy)
            df_copy.dropna(subset=[time_col], inplace=True)
            dropped_rows = original_rows - len(df_copy)
            if dropped_rows > 0:
                logger.warning(
                    f"[{function_name}] Dropped {dropped_rows} rows with invalid values in time column '{time_col}'."
                )

            if df_copy.empty:
                logger.warning(
                    f"[{function_name}] DataFrame became empty after handling invalid time values."
                )
                return df_copy

            df_copy = df_copy.set_index(time_col).sort_index()

            if not isinstance(df_copy.index, pd.DatetimeIndex):
                raise ValueError(
                    f"[{function_name}] Index conversion unexpectedly failed after setting '{time_col}'."
                )
            logger.debug(
                f"[{function_name}] Successfully set '{time_col}' column as DatetimeIndex (UTC)."
            )
            return df_copy
        else:
            if not isinstance(df_copy.index, pd.DatetimeIndex):
                logger.debug(
                    f"[{function_name}] No standard time column found. Attempting to convert existing index to DatetimeIndex (UTC).."
                )
                try:
                    original_index_name = df_copy.index.name
                    df_copy.index = pd.to_datetime(
                        df_copy.index,
                        errors="coerce",
                        utc=True,
                        infer_datetime_format=True,
                    )
                    df_copy.index.name = original_index_name
                    original_rows = len(df_copy)
                    df_copy.dropna(subset=[df_copy.index.name], inplace=True)
                    dropped_rows = original_rows - len(df_copy)
                    if dropped_rows > 0:
                        logger.warning(
                            f"[{function_name}] Dropped {dropped_rows} rows with invalid index values after conversion."
                        )

                    if df_copy.empty:
                        logger.warning(
                            f"[{function_name}] DataFrame became empty after index conversion."
                        )
                        return df_copy

                    if isinstance(df_copy.index, pd.DatetimeIndex):
                        logger.debug(
                            f"[{function_name}] Successfully converted existing index to DatetimeIndex (UTC)."
                        )
                        return df_copy.sort_index()
                    else:
                        raise ValueError(
                            "Index conversion attempted but did not result in DatetimeIndex."
                        )

                except Exception as idx_conv_e:
                    logger.error(
                        f"[{function_name}] Failed to convert existing index to DatetimeIndex: {idx_conv_e}",
                        exc_info=True,
                    )
                    return None
            else:
                logger.error(
                    f"[{function_name}] Unexpected state: Index is DatetimeIndex but wasn't handled."
                )
                return None

    except Exception as e:
        logger.error(
            f"[{function_name}] Failed during DatetimeIndex preparation: {e}",
            exc_info=True,
        )
        return None


def validate_ohlcv_dataframe(
    df: pd.DataFrame, context: str = ""
) -> pd.DataFrame | None:
    """Ensures DataFrame has a UTC DatetimeIndex and required OHLCV columns."""
    log_prefix = f"[{context}][validate_ohlcv_dataframe]"

    df_indexed = ensure_datetime_index(df, context)
    if df_indexed is None or df_indexed.empty:
        logger.error(
            f"{log_prefix} DataFrame preparation failed or resulted in empty DF."
        )
        return None

    df_indexed.columns = [col.lower() for col in df_indexed.columns]
    required_cols = {"open", "high", "low", "close", "volume"}
    if not required_cols.issubset(df_indexed.columns):
        missing_cols = required_cols - set(df_indexed.columns)
        logger.error(
            f"{log_prefix} Missing required OHLCV columns (lowercase): {missing_cols}. Found: {df_indexed.columns.tolist()}"
        )
        return None

    return df_indexed[list(required_cols)].copy()

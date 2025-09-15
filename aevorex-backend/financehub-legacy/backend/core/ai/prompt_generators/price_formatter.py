import json
import pandas as pd

from ....config import settings
from ....utils.logger_config import get_logger
from .constants import AI_PRICE_DAYS_FOR_PROMPT_DEFAULT, FALLBACK_PRICE_DATA

logger = get_logger(__name__)


async def format_price_data_for_prompt(
    symbol: str, df_recent: pd.DataFrame | None
) -> str:
    """
    Formats recent price data into a structured JSON string for the AI prompt.
    Handles potential errors gracefully and ALWAYS returns a string.
    Uses settings.AI.AI_PRICE_DAYS_FOR_PROMPT.
    """
    func_name = "format_price_data_for_prompt"
    logger.debug(f"[{symbol}] Running {func_name}..")
    if df_recent is None or df_recent.empty or "close" not in df_recent.columns:
        msg = f"[{symbol}] {func_name}: Skipping, DataFrame is None, empty, or 'close' column missing."
        logger.warning(msg)
        return "{ Nincs elérhető friss árfolyamadat }"

    try:
        # Get configuration, fallback to default if not available
        ai_settings = getattr(settings, "AI", None)
        price_days_to_show = (
            getattr(
                ai_settings,
                "AI_PRICE_DAYS_FOR_PROMPT",
                AI_PRICE_DAYS_FOR_PROMPT_DEFAULT,
            )
            if ai_settings
            else AI_PRICE_DAYS_FOR_PROMPT_DEFAULT
        )
        price_days_to_show = max(
            min(price_days_to_show, 250), 10
        )  # Clamp between 10-250 days

        logger.debug(
            f"[{symbol}] {func_name}: Price days to show (from config): {price_days_to_show}"
        )

        # Work on a copy to avoid modifying the original
        df_recent_copy = df_recent.copy()

        if "date" in df_recent_copy.columns:
            df_recent_copy.set_index("date", inplace=True)
        elif not isinstance(df_recent_copy.index, pd.DatetimeIndex):
            logger.warning(
                f"[{symbol}] {func_name}: DataFrame index is not DatetimeIndex and no 'date' column found."
            )
            return "{ Hibás idősor formátum az árfolyamadatokhoz }"

        logger.debug(
            f"[{symbol}] {func_name}: Extracting tail({price_days_to_show}) closing prices.."
        )
        closing_prices_series = df_recent_copy["close"].tail(price_days_to_show)

        if closing_prices_series.empty:
            logger.warning(
                f"[{symbol}] {func_name}: Tail({price_days_to_show}) closing prices series is empty."
            )
            return f"{{ Nincs árfolyamadat az utolsó {price_days_to_show} napból }}"

        closing_prices_dict = closing_prices_series.round(2).to_dict()
        closing_prices_str_dict = {}
        processed_count = 0
        skipped_nan = 0
        skipped_invalid_date_type = 0
        skipped_date_format_error = 0

        logger.debug(
            f"[{symbol}] {func_name}: Iterating through {len(closing_prices_dict)} price points.."
        )
        for dt, price in closing_prices_dict.items():
            processed_count += 1
            if pd.isna(price):
                skipped_nan += 1
                continue
            if not isinstance(dt, pd.Timestamp):
                logger.warning(
                    f"[{symbol}] {func_name}: Skipping non-timestamp index '{dt}' (type: {type(dt)})."
                )
                skipped_invalid_date_type += 1
                continue
            try:
                closing_prices_str_dict[dt.strftime("%Y-%m-%d")] = price
            except ValueError as e:
                logger.warning(
                    f"[{symbol}] {func_name}: Skipping invalid date format for timestamp '{dt}': {e}"
                )
                skipped_date_format_error += 1

        logger.debug(
            f"[{symbol}] {func_name}: Iteration summary - Processed: {processed_count}, Added: {len(closing_prices_str_dict)}, Skipped NaN: {skipped_nan}, Skipped Invalid Date Type: {skipped_invalid_date_type}, Skipped Date Format Error: {skipped_date_format_error}"
        )

        if not closing_prices_str_dict:
            logger.warning(
                f"[{symbol}] {func_name}: No valid price data points found after processing."
            )
            return "{ Nincs érvényes árfolyamadat a megadott időszakból }"

        price_data_json = json.dumps(
            closing_prices_str_dict, ensure_ascii=False, indent=2
        )
        logger.debug(
            f"[{symbol}] {func_name}: Successfully formatted {len(closing_prices_str_dict)} price points into JSON."
        )
        return price_data_json

    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Unexpected error: {e}", exc_info=True
        )
        return FALLBACK_PRICE_DATA

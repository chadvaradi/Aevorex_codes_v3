import pandas as pd
from typing import Any

from ....config import settings
from ....utils.logger_config import get_logger
from .constants import (
    FALLBACK_INDICATOR_DATA,
)


logger = get_logger(__name__)


def _safe_get_int_param(
    params_dict: dict[str, Any],
    key: str,
    default_value: int,
    symbol_for_log: str,
    func_name_for_log: str,
) -> int:
    """Safely gets and converts an integer parameter from a dictionary."""
    raw_val = params_dict.get(key, default_value)
    try:
        val_int = int(raw_val)
        if val_int <= 0:  # Periods should usually be positive
            logger.warning(
                f"[{symbol_for_log}] {func_name_for_log}: Non-positive value '{raw_val}' for '{key}' in indicator_params. Using default: {default_value}."
            )
            return default_value
        return val_int
    except (ValueError, TypeError):
        logger.warning(
            f"[{symbol_for_log}] {func_name_for_log}: Invalid value '{raw_val}' for '{key}' in indicator_params (expected int). Using default: {default_value}."
        )
        return default_value


def _format_rsi(latest_indicators: dict[str, Any], **kwargs) -> str | None:
    """Formats the RSI indicator summary."""
    rsi = latest_indicators.get("rsi")
    if rsi is None:
        return None
    rsi_f = float(rsi)
    rsi_desc = f"RSI (14): {rsi_f:.2f}"
    if rsi_f > 70:
        rsi_desc += " (Túlvett >70)"
    elif rsi_f < 30:
        rsi_desc += " (Túladott <30)"
    else:
        rsi_desc += " (Semleges)"
    return rsi_desc


def _format_macd(latest_indicators: dict[str, Any], **kwargs) -> str | None:
    """Formats the MACD Histogram summary."""
    macd_hist = latest_indicators.get("macd_hist")
    if macd_hist is None:
        return None
    macd_hist_f = float(macd_hist)
    macd_desc = f"MACD Hisztogram: {macd_hist_f:.3f}"
    if macd_hist_f > 0.001:
        macd_desc += " (Pozitív/Növekvő momentum)"
    elif macd_hist_f < -0.001:
        macd_desc += " (Negatív/Csökkenő momentum)"
    else:
        macd_desc += " (Semleges/Változás közel nulla)"
    return macd_desc


def _format_sma(latest_indicators: dict[str, Any], **kwargs) -> str | None:
    """Formats the SMA trend summary."""
    sma_short_period = latest_indicators.get("sma_short_period", "20")
    sma_long_period = latest_indicators.get("sma_long_period", "50")
    sma_short = latest_indicators.get("sma_short")
    sma_long = latest_indicators.get("sma_long")
    if sma_short is None or sma_long is None:
        return None
    sma_short_f = float(sma_short)
    sma_long_f = float(sma_long)
    trend_desc = f"Trend (SMA {sma_short_period} / SMA {sma_long_period}): "
    if sma_short_f > sma_long_f * 1.002:
        trend_desc += f"Emelkedő ({sma_short_f:.2f} > {sma_long_f:.2f})"
    elif sma_short_f < sma_long_f * 0.998:
        trend_desc += f"Csökkenő ({sma_short_f:.2f} < {sma_long_f:.2f})"
    else:
        trend_desc += f"Oldalazó/Bizonytalan ({sma_short_f:.2f} ≈ {sma_long_f:.2f})"
    return trend_desc


def _format_bb_middle(
    latest_indicators: dict[str, Any], last_close: float | None, **kwargs
) -> str | None:
    """Formats the Bollinger Band middle line comparison."""
    bb_period = latest_indicators.get("bb_period", 20)
    bb_mid = latest_indicators.get("bb_middle")
    if bb_mid is None or last_close is None:
        return None
    bb_mid_f = float(bb_mid)
    return f"Ár ({last_close:.2f}) vs BB Közép ({bb_period}, {bb_mid_f:.2f}): {'Fölötte' if last_close > bb_mid_f else 'Alatta'}"


def _format_bb_bands(
    latest_indicators: dict[str, Any], last_close: float | None, **kwargs
) -> str | None:
    """Formats the Bollinger Bands position summary."""
    bb_period = latest_indicators.get("bb_period", 20)
    bb_lower = latest_indicators.get("bb_lower")
    bb_upper = latest_indicators.get("bb_upper")
    if bb_lower is None or bb_upper is None or last_close is None:
        return None
    bb_lower_f = float(bb_lower)
    bb_upper_f = float(bb_upper)
    band_pos = "Közötte"
    if last_close > bb_upper_f:
        band_pos = "Fölötte (lehetséges trend-visszafordulás)"
    elif last_close < bb_lower_f:
        band_pos = "Alatta (lehetséges trend-visszafordulás)"
    return f"Ár ({last_close:.2f}) vs BB Szalagok ({bb_period}, {bb_lower_f:.2f}-{bb_upper_f:.2f}): {band_pos}"


FORMATTER_REGISTRY = {
    "rsi": _format_rsi,
    "macd_hist": _format_macd,
    "sma": _format_sma,
    "bb_middle": _format_bb_middle,
    "bb_bands": _format_bb_bands,
}


async def format_indicator_data_for_prompt(
    symbol: str,
    latest_indicators: dict[str, Any] | None,
    df_recent: pd.DataFrame | None,
) -> tuple[str, bool]:
    """
    Formats latest technical indicators into a structured, interpreted string for the AI prompt.
    Uses INDICATOR_PARAMS from settings.DATA_PROCESSING.
    Handles potential errors gracefully and ALWAYS returns a (string, bool) tuple.
    """
    func_name = "format_indicator_data_for_prompt"
    logger.debug(f"[{symbol}] Running {func_name}..")
    if not latest_indicators:
        logger.warning(
            f"[{symbol}] {func_name}: Skipping, no technical indicators dictionary provided."
        )
        return "Technikai indikátor adatok nem állnak rendelkezésre.", False

    summary_points = []
    indicator_data_found = False
    indicator_params: dict[str, Any] = {}

    try:
        try:
            indicator_params_setting = settings.DATA_PROCESSING.INDICATOR_PARAMS
            if not isinstance(indicator_params_setting, dict):
                raise TypeError(
                    f"INDICATOR_PARAMS is not a dict (type: {type(indicator_params_setting).__name__})"
                )
            indicator_params = indicator_params_setting
            logger.debug(
                f"[{symbol}] {func_name}: Using indicator parameters from settings.DATA_PROCESSING.INDICATOR_PARAMS: {indicator_params}"
            )
        except AttributeError as e:
            logger.error(
                f"[{symbol}] {func_name}: CONFIG ERROR - Could not access 'settings.DATA_PROCESSING.INDICATOR_PARAMS'. Details: {e}",
                exc_info=True,
            )
            return "Hiba az indikátor beállítások betöltésekor (elérési út).", False
        except TypeError as e:
            logger.error(
                f"[{symbol}] {func_name}: CONFIG ERROR - {e}. Using empty params, which will lead to defaults for periods."
            )
            indicator_params = {}  # Ensures it's a dict for _safe_get_int_param

        rsi_period = _safe_get_int_param(
            indicator_params, "RSI_PERIOD", 14, symbol, func_name
        )
        sma_short_period = _safe_get_int_param(
            indicator_params, "SMA_SHORT_PERIOD", 9, symbol, func_name
        )
        sma_long_period = _safe_get_int_param(
            indicator_params, "SMA_LONG_PERIOD", 20, symbol, func_name
        )
        bb_period = _safe_get_int_param(
            indicator_params, "BBANDS_PERIOD", 20, symbol, func_name
        )
        logger.debug(
            f"[{symbol}] {func_name}: Effective indicator periods - RSI({rsi_period}), SMA({sma_short_period}/{sma_long_period}), BB({bb_period})"
        )

        last_close: float | None = None
        if (
            df_recent is not None
            and not df_recent.empty
            and "close" in df_recent.columns
        ):
            try:
                last_close_val = df_recent["close"].iloc[-1]
                if pd.notna(last_close_val):
                    last_close = float(last_close_val)
                    logger.debug(
                        f"[{symbol}] {func_name}: Last close price: {last_close:.2f}"
                    )
                else:
                    logger.warning(f"[{symbol}] {func_name}: Last close price is NaN.")
            except (IndexError, ValueError, TypeError) as e:
                logger.warning(
                    f"[{symbol}] {func_name}: Could not retrieve/convert last close price: {e}"
                )
        else:
            logger.warning(
                f"[{symbol}] {func_name}: Cannot get last close price (df_recent missing, empty, or no 'close' column)."
            )

        for indicator_key, formatter_func in FORMATTER_REGISTRY.items():
            logger.debug(
                f"[{symbol}] {func_name}: Processing indicator '{indicator_key}'.."
            )
            try:
                summary = formatter_func(
                    latest_indicators=latest_indicators,
                    last_close=last_close,
                    params=indicator_params,  # Pass params for future use
                )
                if summary:
                    summary_points.append(summary)
                    indicator_data_found = True
            except (ValueError, TypeError) as e:
                logger.error(
                    f"[{symbol}] {func_name}: Error processing indicator '{indicator_key}': {e}",
                    exc_info=True,
                )
                summary_points.append(
                    f"Hiba a(z) '{indicator_key}' indikátor feldolgozása közben."
                )

        if not summary_points:
            logger.warning(
                f"[{symbol}] {func_name}: No indicator data points could be summarized."
            )
            return (
                "Nem sikerült a technikai indikátorokból összefoglalót készíteni.",
                False,
            )

        final_summary = "\n- ".join(summary_points)
        final_summary = "- " + final_summary
        logger.debug(
            f"[{symbol}] {func_name}: Successfully formatted {len(summary_points)} indicator points."
        )
        return final_summary, indicator_data_found

    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Unexpected error: {e}", exc_info=True
        )
        return FALLBACK_INDICATOR_DATA, False

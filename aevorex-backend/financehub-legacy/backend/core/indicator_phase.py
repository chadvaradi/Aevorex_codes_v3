# indicator_phase.py
# Standard library / third-party
from typing import Any
import pandas as pd

# Local imports
from backend.utils.logger_config import get_logger
from backend.core.indicator_service.service import calculate_and_format_indicators
from backend.models import IndicatorHistory

# Logger must be defined after imports
logger = get_logger(__name__)

__all__ = [
    "calculate_indicators",
    "extract_latest_indicators",
]


async def calculate_indicators(
    ohlcv_df: pd.DataFrame,
    symbol: str,
    request_id: str = "ind",
) -> IndicatorHistory | None:
    """Asynchronously calculate technical indicators for the given OHLCV DataFrame.

    The heavy-lifting is delegated to ``indicator_service.calculate_and_format_indicators``
    which returns a fully populated ``IndicatorHistory`` Pydantic object.
    """
    log_prefix = f"[{request_id}][Indicator:{symbol}]"
    try:
        if ohlcv_df is None or ohlcv_df.empty:
            logger.warning(
                f"{log_prefix} Empty OHLCV dataframe – skipping indicator calculation"
            )
            return None

        history: IndicatorHistory | None = calculate_and_format_indicators(
            ohlcv_df, symbol
        )
        if history is None:
            logger.warning(f"{log_prefix} Indicator calculation returned None")
        else:
            logger.info(f"{log_prefix} Indicator calculation finished successfully")
        return history
    except Exception as e:
        logger.error(
            f"{log_prefix} Unexpected error during indicator calculation: {e}",
            exc_info=True,
        )
        return None


def extract_latest_indicators(history: IndicatorHistory | None) -> dict[str, Any]:
    """Extract a flat ``dict`` of *latest* indicator values from an ``IndicatorHistory``.

    The function is defensive – if a specific indicator set is missing it simply won't
    add the key to the result dictionary. This guarantees that the orchestrator can
    pass the dict further without additional checks.
    """
    if history is None:
        return {}

    latest: dict[str, Any] = {}
    try:
        # --- RSI ---
        if history.rsi and history.rsi.RSI:
            latest_rsi = history.rsi.RSI[-1]
            if latest_rsi and latest_rsi.value is not None:
                latest["rsi"] = latest_rsi.value

        # --- MACD ---
        if history.macd and history.macd.MACD_LINE and history.macd.MACD_SIGNAL:
            latest_macd_line = history.macd.MACD_LINE[-1]
            latest_macd_signal = history.macd.MACD_SIGNAL[-1]
            if latest_macd_line and latest_macd_line.value is not None:
                latest["macd"] = latest_macd_line.value
            if latest_macd_signal and latest_macd_signal.value is not None:
                latest["macd_signal"] = latest_macd_signal.value
        if history.macd and history.macd.MACD_HIST:
            latest_hist = history.macd.MACD_HIST[-1]
            if latest_hist and latest_hist.value is not None:
                latest["macd_histogram"] = latest_hist.value

        # --- SMA ---
        if history.sma and history.sma.SMA_SHORT and history.sma.SMA_LONG:
            sma_short_last = history.sma.SMA_SHORT[-1]
            sma_long_last = history.sma.SMA_LONG[-1]
            if sma_short_last and sma_short_last.value is not None:
                latest["sma_short"] = sma_short_last.value
            if sma_long_last and sma_long_last.value is not None:
                latest["sma_long"] = sma_long_last.value

        # --- EMA ---
        if history.ema and history.ema.EMA_SHORT and history.ema.EMA_LONG:
            ema_short_last = history.ema.EMA_SHORT[-1]
            ema_long_last = history.ema.EMA_LONG[-1]
            if ema_short_last and ema_short_last.value is not None:
                latest["ema_short"] = ema_short_last.value
            if ema_long_last and ema_long_last.value is not None:
                latest["ema_long"] = ema_long_last.value

        # --- Bollinger Bands ---
        if (
            history.bbands
            and history.bbands.BBANDS_UPPER
            and history.bbands.BBANDS_MIDDLE
            and history.bbands.BBANDS_LOWER
        ):
            bb_upper_last = history.bbands.BBANDS_UPPER[-1]
            bb_middle_last = history.bbands.BBANDS_MIDDLE[-1]
            bb_lower_last = history.bbands.BBANDS_LOWER[-1]
            if bb_upper_last and bb_upper_last.value is not None:
                latest["bb_upper"] = bb_upper_last.value
            if bb_middle_last and bb_middle_last.value is not None:
                latest["bb_middle"] = bb_middle_last.value
            if bb_lower_last and bb_lower_last.value is not None:
                latest["bb_lower"] = bb_lower_last.value

        # --- Stochastic ---
        if history.stoch and history.stoch.STOCH:
            stoch_last = history.stoch.STOCH[-1]
            if stoch_last:
                if stoch_last.k is not None:
                    latest["stoch_k"] = stoch_last.k
                if stoch_last.d is not None:
                    latest["stoch_d"] = stoch_last.d

    except Exception as e:
        logger.error(
            f"extract_latest_indicators(): error while extracting values – {e}",
            exc_info=True,
        )

    return latest

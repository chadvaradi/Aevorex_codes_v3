# backend/core.indicator_service/service.py
import pandas as pd
import numpy as np
import time

from backend.config import settings
from backend.utils.logger_config import get_logger
from backend.models.stock import (
    IndicatorHistory,
    SMASet,
    BBandsSet,
    RSISeries,
    VolumeSeries,
    VolumeSMASeries,
    MACDSeries,
    STOCHSeries,
)
from .helpers import validate_ohlcv_dataframe
from .formatters import (
    format_simple_series,
    format_volume_series,
    format_macd_hist_series,
    format_stoch_series,
)
from .calculators import sma, bbands, rsi, macd, stoch, volume_sma

logger = get_logger(f"aevorex_finbot.{__name__}")


def calculate_and_format_indicators(
    ohlcv_df: pd.DataFrame, symbol: str
) -> IndicatorHistory | None:
    function_name = "calculate_and_format_indicators"
    symbol_upper = symbol.upper()
    logger.info(f"[{symbol_upper}] [{function_name}] Received request.")

    prep_start_time = time.monotonic()
    df_ta = validate_ohlcv_dataframe(ohlcv_df, function_name)
    if df_ta is None:
        return None  # Error logged in helper
    prep_duration = time.monotonic() - prep_start_time
    logger.info(
        f"[{symbol_upper}] [{function_name}] Prepared DataFrame shape {df_ta.shape} in {prep_duration:.4f}s."
    )

    try:
        params = settings.DATA_PROCESSING.INDICATOR_PARAMS
        sma_s_len = params.get("sma_short", 20)
        sma_l_len = params.get("sma_long", 50)
        bb_len = params.get("bbands_period", 20)
        bb_std = params.get("bbands_std_dev", 2.0)
        rsi_len = params.get("rsi_period", 14)
        vol_sma_len = params.get("volume_sma_period", 20)
        macd_f = params.get("macd_fast", 12)
        macd_s = params.get("macd_slow", 26)
        macd_sig = params.get("macd_signal", 9)
        stoch_k = params.get("stoch_k", 14)
        stoch_d = params.get("stoch_d", 3)
    except (AttributeError, ValueError, TypeError) as e_params:
        logger.error(
            f"[{symbol_upper}] [{function_name}] Invalid or missing indicator parameters in settings: {e_params}. Using hardcoded defaults.",
            exc_info=True,
        )
        sma_s_len, sma_l_len, bb_len, bb_std, rsi_len, vol_sma_len = (
            20,
            50,
            20,
            2.0,
            14,
            20,
        )
        macd_f, macd_s, macd_sig = 12, 26, 9
        stoch_k, stoch_d = 14, 3

    logger.info(f"[{symbol_upper}] [{function_name}] Starting TA-Lib calculations..")
    calc_start_time = time.monotonic()

    high = df_ta["high"].values.astype(np.float64)
    low = df_ta["low"].values.astype(np.float64)
    close = df_ta["close"].values.astype(np.float64)
    volume = df_ta["volume"].values.astype(np.float64)

    try:
        sma_short_vals, sma_long_vals = sma.calculate_sma(close, sma_s_len, sma_l_len)
        bb_upper_vals, bb_middle_vals, bb_lower_vals = bbands.calculate_bbands(
            close, bb_len, bb_std
        )
        rsi_vals = rsi.calculate_rsi(close, rsi_len)
        volume_sma_vals = volume_sma.calculate_volume_sma(volume, vol_sma_len)
        macd_line_vals, macd_signal_vals, macd_hist_vals = macd.calculate_macd(
            close, macd_f, macd_s, macd_sig
        )
        stoch_k_vals, stoch_d_vals = stoch.calculate_stoch(
            high, low, close, stoch_k, stoch_d
        )

        calc_duration = time.monotonic() - calc_start_time
        logger.info(
            f"[{symbol_upper}] [{function_name}] TA-Lib calculations finished in {calc_duration:.4f}s."
        )

        # Convert back to pandas Series for formatting
        def to_series(data):
            return pd.Series(data, index=df_ta.index)

        indicator_history = IndicatorHistory(
            sma=SMASet(
                SMA_SHORT=format_simple_series(to_series(sma_short_vals), "SMA_SHORT"),
                SMA_LONG=format_simple_series(to_series(sma_long_vals), "SMA_LONG"),
            ),
            bbands=BBandsSet(
                BBANDS_LOWER=format_simple_series(
                    to_series(bb_lower_vals), "BBANDS_LOWER"
                ),
                BBANDS_MIDDLE=format_simple_series(
                    to_series(bb_middle_vals), "BBANDS_MIDDLE"
                ),
                BBANDS_UPPER=format_simple_series(
                    to_series(bb_upper_vals), "BBANDS_UPPER"
                ),
            ),
            rsi=RSISeries(
                RSI=format_simple_series(to_series(rsi_vals), f"RSI_{rsi_len}")
            ),
            volume=VolumeSeries(
                VOLUME=format_volume_series(df_ta, "volume", "open", "close")
            ),
            volume_sma=VolumeSMASeries(
                VOLUME_SMA=format_simple_series(
                    to_series(volume_sma_vals), "VOLUME_SMA"
                )
            ),
            macd=MACDSeries(
                MACD_LINE=format_simple_series(to_series(macd_line_vals), "MACD_LINE"),
                MACD_SIGNAL=format_simple_series(
                    to_series(macd_signal_vals), "MACD_SIGNAL"
                ),
                MACD_HIST=format_macd_hist_series(
                    to_series(macd_hist_vals), "MACD_HIST"
                ),
            ),
            stoch=STOCHSeries(
                STOCH=format_stoch_series(
                    pd.DataFrame(
                        {"k": stoch_k_vals, "d": stoch_d_vals}, index=df_ta.index
                    ),
                    "k",
                    "d",
                )
            ),
        )

        return indicator_history

    except Exception as e:
        logger.error(
            f"[{symbol_upper}] [{function_name}] Error during TA-Lib calculations: {e}",
            exc_info=True,
        )
        return None

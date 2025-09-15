# backend/core.indicator_service/calculators/macd.py
import numpy as np
import pandas as pd

try:
    import talib

    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False


def calculate_macd(
    close_prices: np.ndarray, fast_period: int, slow_period: int, signal_period: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculates the Moving Average Convergence Divergence (MACD)."""
    if TA_AVAILABLE:
        macd_line, macd_signal, macd_hist = talib.MACD(
            close_prices,
            fastperiod=fast_period,
            slowperiod=slow_period,
            signalperiod=signal_period,
        )
        return macd_line, macd_signal, macd_hist
    else:
        # Fallback to pandas-ta
        try:
            import pandas_ta as ta

            df = pd.DataFrame({"close": close_prices})
            macd = ta.macd(
                df["close"], fast=fast_period, slow=slow_period, signal=signal_period
            )
            macd_line = macd[f"MACD_{fast_period}_{slow_period}_{signal_period}"].values
            macd_signal = macd[
                f"MACDs_{fast_period}_{slow_period}_{signal_period}"
            ].values
            macd_hist = macd[
                f"MACDh_{fast_period}_{slow_period}_{signal_period}"
            ].values
            return macd_line, macd_signal, macd_hist
        except ImportError:
            raise ImportError(
                "Neither TA-Lib nor pandas-ta is available for MACD calculation."
            )

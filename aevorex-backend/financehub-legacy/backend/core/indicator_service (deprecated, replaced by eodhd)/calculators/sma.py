# backend/core.indicator_service/calculators/sma.py
import numpy as np
import pandas as pd

try:
    import talib

    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False


def calculate_sma(
    close_prices: np.ndarray, short_period: int, long_period: int
) -> tuple[np.ndarray, np.ndarray]:
    """Calculates short and long Simple Moving Averages."""
    if TA_AVAILABLE:
        sma_short = talib.SMA(close_prices, timeperiod=short_period)
        sma_long = talib.SMA(close_prices, timeperiod=long_period)
        return sma_short, sma_long
    else:
        # Fallback to pandas-ta
        try:
            import pandas_ta as ta

            df = pd.DataFrame({"close": close_prices})
            sma_short = ta.sma(df["close"], length=short_period).values
            sma_long = ta.sma(df["close"], length=long_period).values
            return sma_short, sma_long
        except ImportError:
            raise ImportError(
                "Neither TA-Lib nor pandas-ta is available for SMA calculation."
            )

# backend/core.indicator_service/calculators/rsi.py
import numpy as np
import pandas as pd

try:
    import talib

    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False


def calculate_rsi(close_prices: np.ndarray, period: int) -> np.ndarray:
    """Calculates the Relative Strength Index (RSI)."""
    if TA_AVAILABLE:
        return talib.RSI(close_prices, timeperiod=period)
    else:
        # Fallback to pandas-ta
        try:
            import pandas_ta as ta

            df = pd.DataFrame({"close": close_prices})
            rsi = ta.rsi(df["close"], length=period).values
            return rsi
        except ImportError:
            raise ImportError(
                "Neither TA-Lib nor pandas-ta is available for RSI calculation."
            )

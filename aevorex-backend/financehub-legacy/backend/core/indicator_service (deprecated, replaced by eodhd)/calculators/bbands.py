# backend/core.indicator_service/calculators/bbands.py
import numpy as np
import pandas as pd

try:
    import talib

    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False


def calculate_bbands(
    close_prices: np.ndarray, period: int, std_dev: float
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calculates Bollinger Bands."""
    if TA_AVAILABLE:
        upper, middle, lower = talib.BBANDS(
            close_prices, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev
        )
        return upper, middle, lower
    else:
        # Fallback to pandas-ta
        try:
            import pandas_ta as ta

            df = pd.DataFrame({"close": close_prices})
            bbands = ta.bbands(df["close"], length=period, std=std_dev)
            upper = bbands[f"BBU_{period}_{std_dev}"].values
            middle = bbands[f"BBM_{period}_{std_dev}"].values
            lower = bbands[f"BBL_{period}_{std_dev}"].values
            return upper, middle, lower
        except ImportError:
            raise ImportError(
                "Neither TA-Lib nor pandas-ta is available for Bollinger Bands calculation."
            )

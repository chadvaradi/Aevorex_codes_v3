import numpy as np
import pandas as pd

try:
    import talib

    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False


def calculate_volume_sma(volume_data: np.ndarray, period: int) -> np.ndarray:
    """Calculates the Simple Moving Average of the volume."""
    if TA_AVAILABLE:
        return talib.SMA(volume_data, timeperiod=period)
    else:
        # Fallback to pandas-ta
        try:
            import pandas_ta as ta

            df = pd.DataFrame({"volume": volume_data})
            volume_sma = ta.sma(df["volume"], length=period).values
            return volume_sma
        except ImportError:
            raise ImportError(
                "Neither TA-Lib nor pandas-ta is available for Volume SMA calculation."
            )

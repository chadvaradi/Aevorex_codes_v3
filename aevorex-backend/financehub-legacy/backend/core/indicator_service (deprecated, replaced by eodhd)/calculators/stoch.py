# backend/core.indicator_service/calculators/stoch.py
import numpy as np
import pandas as pd

try:
    import talib

    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False


def calculate_stoch(
    high_prices: np.ndarray,
    low_prices: np.ndarray,
    close_prices: np.ndarray,
    k_period: int,
    d_period: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculates the Stochastic Oscillator."""
    if TA_AVAILABLE:
        stoch_k, stoch_d = talib.STOCH(
            high_prices,
            low_prices,
            close_prices,
            fastk_period=k_period,
            slowk_period=d_period,
            slowd_period=d_period,
        )
        return stoch_k, stoch_d
    else:
        # Fallback to pandas-ta
        try:
            import pandas_ta as ta

            df = pd.DataFrame(
                {"high": high_prices, "low": low_prices, "close": close_prices}
            )
            stoch = ta.stoch(df["high"], df["low"], df["close"], k=k_period, d=d_period)
            stoch_k = stoch[f"STOCHk_{k_period}_{d_period}"].values
            stoch_d = stoch[f"STOCHd_{k_period}_{d_period}"].values
            return stoch_k, stoch_d
        except ImportError:
            raise ImportError(
                "Neither TA-Lib nor pandas-ta is available for Stochastic Oscillator calculation."
            )

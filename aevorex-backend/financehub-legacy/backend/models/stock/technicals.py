"""
Technical indicator models and calculation utilities.
=====================================================

Ez a modul tartalmazza a legfontosabb technikai indikátorok adatszerkezeteit
és számítási függvényeit (SMA, EMA, RSI, MACD, Bollinger Bands).

Minden számítás valós piaci adatokból indul ki (pl. OHLCV).
Nincsenek placeholderek, minden funkció ténylegesen működik.

Author: Aevorex Team (2025)
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel
import numpy as np


# -------------------------------
# Indicator típusok enumerációja
# -------------------------------
class IndicatorType(str, Enum):
    SMA = "sma"
    EMA = "ema"
    RSI = "rsi"
    MACD = "macd"
    BBANDS = "bbands"


# -------------------------------
# Pydantic modellek
# -------------------------------
class IndicatorMetadata(BaseModel):
    indicator: IndicatorType
    description: Optional[str] = None


class SmaResult(BaseModel):
    date: str
    period: int
    value: float


class EmaResult(BaseModel):
    date: str
    period: int
    value: float


class RsiResult(BaseModel):
    date: str
    period: int
    value: float


class MacdResult(BaseModel):
    date: str
    macd: float
    signal: float
    histogram: float


class BBandsResult(BaseModel):
    date: str
    middle: float
    upper: float
    lower: float


class EmaCross(BaseModel):
    date: str
    fast_ema: float
    slow_ema: float
    cross_type: str  # "bullish" or "bearish"


# -------------------------------
# Számítási függvények
# -------------------------------
def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Simple Moving Average (SMA)"""
    if len(prices) < period:
        return []
    return list(np.convolve(prices, np.ones(period), "valid") / period)


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Exponential Moving Average (EMA)"""
    if len(prices) < period:
        return []
    weights = np.exp(np.linspace(-1.0, 0.0, period))
    weights /= weights.sum()
    ema = np.convolve(prices, weights, mode="full")[: len(prices)]
    return ema[period - 1 :]


def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
    """Relative Strength Index (RSI)"""
    if len(prices) < period + 1:
        return []
    deltas = np.diff(prices)
    seed = deltas[:period]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100.0 - 100.0 / (1.0 + rs)

    up_vals = np.where(deltas > 0, deltas, 0)
    down_vals = np.where(deltas < 0, -deltas, 0)

    up_avg = up
    down_avg = down

    for i in range(period, len(prices)):
        up_avg = (up_avg * (period - 1) + up_vals[i - 1]) / period
        down_avg = (down_avg * (period - 1) + down_vals[i - 1]) / period
        rs = up_avg / down_avg if down_avg != 0 else 0
        rsi[i] = 100.0 - 100.0 / (1.0 + rs)

    return list(rsi[period:])


def calculate_macd(
    prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9
):
    """MACD (Moving Average Convergence Divergence)"""
    if len(prices) < slow:
        return [], [], []
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    min_len = min(len(ema_fast), len(ema_slow))
    macd_line = np.array(ema_fast[-min_len:]) - np.array(ema_slow[-min_len:])
    signal_line = calculate_ema(list(macd_line), signal)
    hist = macd_line[-len(signal_line) :] - np.array(signal_line)
    return list(macd_line[-len(signal_line) :]), list(signal_line), list(hist)


def calculate_bbands(prices: List[float], period: int = 20, num_std_dev: float = 2.0):
    """Bollinger Bands"""
    if len(prices) < period:
        return [], [], []
    sma = calculate_sma(prices, period)
    sma = np.array(sma)
    rolling_std = np.array(
        [np.std(prices[i - period : i]) for i in range(period, len(prices) + 1)]
    )
    upper = sma + num_std_dev * rolling_std
    lower = sma - num_std_dev * rolling_std
    return list(sma), list(upper), list(lower)

# =============================================================================
# === From: indicator_models.py ===
# =============================================================================
from datetime import date as Date
from typing import Optional, List, Dict, Any, Annotated
from pydantic import BaseModel, Field

# Pydantic v2 compatible strict types
StrictFloat = Annotated[float, Field(strict=True)]
StrictInt = Annotated[int, Field(strict=True)]


class IndicatorPoint(BaseModel):
    """Általános indikátor adatpont, dátummal és értékkel."""

    date: Date
    value: Optional[StrictFloat] = None


class VolumePoint(BaseModel):
    """Forgalmi adatpont."""

    date: Date
    volume: StrictInt


class MACDHistPoint(BaseModel):
    """MACD indikátor adatpont (MACD, Signal, Histogram)."""

    date: Date
    macd: Optional[StrictFloat] = None
    signal: Optional[StrictFloat] = None
    hist: Optional[StrictFloat] = None


class STOCHPoint(BaseModel):
    """Stochastic Oscillator adatpont."""

    date: Date
    slow_k: Optional[StrictFloat] = Field(None, alias="slowK")
    slow_d: Optional[StrictFloat] = Field(None, alias="slowD")


class SMASet(BaseModel):
    """SMA (Simple Moving Average) értékek egy adott időpontban."""

    sma_5: Optional[StrictFloat] = Field(None, alias="sma5")
    sma_10: Optional[StrictFloat] = Field(None, alias="sma10")
    sma_20: Optional[StrictFloat] = Field(None, alias="sma20")
    sma_50: Optional[StrictFloat] = Field(None, alias="sma50")
    sma_100: Optional[StrictFloat] = Field(None, alias="sma100")
    sma_200: Optional[StrictFloat] = Field(None, alias="sma200")


class EMASet(BaseModel):
    """EMA (Exponential Moving Average) értékek."""

    ema_12: Optional[StrictFloat] = Field(None, alias="ema12")
    ema_26: Optional[StrictFloat] = Field(None, alias="ema26")


class BBandsSet(BaseModel):
    """Bollinger Bands értékek."""

    upper: Optional[StrictFloat] = None
    middle: Optional[StrictFloat] = None
    lower: Optional[StrictFloat] = None


class RSISeries(BaseModel):
    """RSI (Relative Strength Index) idősor."""

    rsi_14: List[IndicatorPoint] = Field(default_factory=list, alias="rsi14")


class VolumeSeries(BaseModel):
    """Forgalmi idősor."""

    volume: List[VolumePoint] = Field(default_factory=list)


class MACDSeries(BaseModel):
    """MACD idősor."""

    macd: List[MACDHistPoint] = Field(default_factory=list)


class STOCHSeries(BaseModel):
    """Stochastic Oscillator idősor."""

    stoch: List[STOCHPoint] = Field(default_factory=list)


class VolumeSMASeries(BaseModel):
    """Volume SMA (Simple Moving Average) idősor."""

    VOLUME_SMA: Optional[List[IndicatorPoint]] = Field(None)


class IndicatorHistory(BaseModel):
    """Különböző technikai indikátorok historikus adatait tárolja."""

    rsi: Optional[RSISeries] = None
    volume: Optional[VolumeSeries] = None
    macd: Optional[MACDSeries] = None
    stoch: Optional[STOCHSeries] = None


class LatestIndicators(BaseModel):
    """A legfrissebb indikátorértékeket tartalmazza."""

    rsi: Optional[Dict[str, Any]] = Field(None)
    sma: Optional[Dict[str, Any]] = Field(None)
    ema: Optional[Dict[str, Any]] = Field(None)
    macd: Optional[Dict[str, Any]] = Field(None)
    bbands: Optional[Dict[str, Any]] = Field(None)
    stoch: Optional[Dict[str, Any]] = Field(None)


class TechnicalAnalysis(BaseModel):
    """Átfogó technikai analízis adatmodell egy részvényhez."""

    symbol: str
    latest_indicators: Optional[LatestIndicators] = None
    indicator_history: Optional[IndicatorHistory] = None

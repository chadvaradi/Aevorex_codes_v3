from __future__ import annotations
from dataclasses import dataclass


@dataclass
class MarketData:
    """Real market data structure"""

    symbol: str
    current_price: float
    volume: int
    market_cap: int
    beta: float
    pe_ratio: float | None
    sector: str


@dataclass
class TechnicalIndicators:
    """Real technical indicators"""

    rsi: float
    macd_signal: str
    sma_20: float
    sma_50: float
    volume_trend: str
    support_levels: list[float]
    resistance_levels: list[float]

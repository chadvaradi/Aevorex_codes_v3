from __future__ import annotations

import statistics

from backend.core.ai_analyzers.models import TechnicalIndicators


class TechnicalAnalyzer:
    def analyze(self, chart_data: dict) -> TechnicalIndicators:
        """Analyze technical indicators from real chart data only"""
        if not chart_data or not chart_data.get("ohlcv_data"):
            raise ValueError("No real chart data available for technical analysis")

        ohlcv = chart_data["ohlcv_data"]
        if len(ohlcv) < 50:
            raise ValueError("Insufficient chart data for reliable technical analysis")

        prices = [float(bar.get("close", 0)) for bar in ohlcv[-50:]]
        volumes = [int(bar.get("volume", 0)) for bar in ohlcv[-20:]]

        if not all(prices) or not all(volumes):
            raise ValueError("Invalid price or volume data in chart")

        rsi = self._calculate_rsi(prices)
        sma_20 = statistics.mean(prices[-20:]) if len(prices) >= 20 else prices[-1]
        sma_50 = statistics.mean(prices[-50:]) if len(prices) >= 50 else prices[-1]
        macd_signal = "Bullish crossover" if sma_20 > sma_50 else "Bearish signal"
        volume_trend = (
            "Increasing" if volumes[-1] > statistics.mean(volumes) else "Decreasing"
        )
        support = self._calculate_support_levels(prices)
        resistance = self._calculate_resistance_levels(prices)

        return TechnicalIndicators(
            rsi=rsi,
            macd_signal=macd_signal,
            sma_20=sma_20,
            sma_50=sma_50,
            volume_trend=volume_trend,
            support_levels=support,
            resistance_levels=resistance,
        )

    def _calculate_rsi(self, prices: list[float], period: int = 14) -> float:
        """Calculate Relative Strength Index (RSI)."""
        if len(prices) < period:
            return 50.0

        gains = []
        losses = []
        for i in range(1, len(prices)):
            delta = prices[i] - prices[i - 1]
            if delta > 0:
                gains.append(delta)
            else:
                losses.append(abs(delta))

        avg_gain = statistics.mean(gains) if gains else 0
        avg_loss = statistics.mean(losses) if losses else 1

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(rsi, 2)

    def _calculate_support_levels(self, prices: list[float]) -> list[float]:
        """Calculate support levels based on recent lows."""
        if not prices:
            return []
        sorted_prices = sorted(prices[-20:])
        return [round(p, 2) for p in sorted_prices[:2]]

    def _calculate_resistance_levels(self, prices: list[float]) -> list[float]:
        """Calculate resistance levels based on recent highs."""
        if not prices:
            return []
        sorted_prices = sorted(prices[-20:], reverse=True)
        return [round(p, 2) for p in sorted_prices[:2]]

    def determine_trend(self, technical: TechnicalIndicators) -> str:
        """Determine the primary trend based on moving averages."""
        if technical.sma_20 > technical.sma_50:
            return "Uptrend"
        elif technical.sma_20 < technical.sma_50:
            return "Downtrend"
        return "Sideways"

    def analyze_moving_averages(self, technical: TechnicalIndicators) -> str:
        """Analyze the moving average signals."""
        if technical.sma_20 > technical.sma_50:
            return "20-day SMA is above 50-day SMA (Bullish)"
        else:
            return "20-day SMA is below 50-day SMA (Bearish)"

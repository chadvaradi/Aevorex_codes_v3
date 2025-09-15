from __future__ import annotations
import logging
from typing import Any

from backend.core.ai_analyzers.models import MarketData

logger = logging.getLogger(__name__)


class FundamentalAnalyzer:
    def analyze_risk(self, data: MarketData) -> str:
        """Analyzes risk based on fundamental data."""
        if data.beta > 1.5:
            return "Magas kockázat (magas béta)"
        if 1.0 < data.beta <= 1.5:
            return "Mérsékelt kockázat (átlagnál magasabb volatilitás)"
        if data.pe_ratio and data.pe_ratio > 40:
            return "Potenciálisan magas kockázat (magas P/E ráta)"
        return "Alacsony-mérsékelt kockázat"

    def analyze_growth(self, data: MarketData) -> str:
        """Analyzes growth potential."""
        if "Technology" in data.sector:
            return "Magas növekedési potenciál (technológiai szektor)"
        if data.pe_ratio and data.pe_ratio < 15:
            return "Értékalapú részvény, mérsékelt növekedéssel"
        return "Stabil, piacot követő növekedési potenciál"

    def analyze(self, market_data: dict[str, Any]) -> dict[str, str]:
        """Performs a full fundamental analysis."""
        if not market_data:
            raise ValueError("Nincsenek valós piaci adatok a fundamentális elemzéshez.")

        try:
            symbol = market_data.get("symbol")
            if symbol is None:
                raise ValueError("A 'symbol' kulcs hiányzik a piaci adatokból.")

            current_price = market_data.get("current_price")
            if current_price is None:
                raise ValueError("A 'current_price' kulcs hiányzik a piaci adatokból.")

            data = MarketData(
                symbol=symbol,
                current_price=current_price,
                volume=market_data.get("volume"),
                market_cap=market_data.get("market_cap"),
                beta=market_data.get("beta"),
                pe_ratio=market_data.get("pe_ratio"),
                sector=market_data.get("sector", "Unknown"),
            )
        except (TypeError, KeyError) as e:
            logger.error(f"Hiányzó kulcs a fundamentális adatokban: {e}")
            raise ValueError(
                f"Nem teljesek a bemeneti adatok a fundamentális elemzéshez: {e}"
            ) from e

        return {
            "risk_assessment": self.analyze_risk(data),
            "growth_potential": self.analyze_growth(data),
        }

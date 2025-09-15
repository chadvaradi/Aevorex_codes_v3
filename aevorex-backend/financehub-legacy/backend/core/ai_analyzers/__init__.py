from __future__ import annotations
import logging
from typing import Any

# Új, moduláris analizátorok importálása
from backend.core.ai_analyzers.technical_analyzer import TechnicalAnalyzer
from backend.core.ai_analyzers.fundamental_analyzer import FundamentalAnalyzer
from backend.core.ai_analyzers.sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)


class RealTimeAIAnalyzer:
    """
    Koordinátor osztály, amely a moduláris analizátorokat hívja meg
    és összefogja az eredményeket.
    """

    def __init__(self):
        self.technical = TechnicalAnalyzer()
        self.fundamental = FundamentalAnalyzer()
        self.sentiment = SentimentAnalyzer()
        logger.info("RealTimeAIAnalyzer inicializálva a moduláris analizátorokkal.")

    def run_full_analysis(
        self,
        chart_data: dict[str, Any],
        market_data: dict[str, Any],
        news_data: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Lefuttatja a teljes, valós idejű elemzési folyamatot.
        Minden al-analizátort meghív és az eredményeket egyetlen objektumban adja vissza.
        """
        analysis_results = {}
        try:
            # Párhuzamosításra alkalmas hely, de most szekvenciálisan futtatjuk
            if chart_data:
                analysis_results["technical"] = self.technical.analyze(chart_data)
            if market_data:
                analysis_results["fundamental"] = self.fundamental.analyze(market_data)
            if news_data:
                analysis_results["sentiment"] = self.sentiment.analyze(news_data)

            # Az összesített eredményekből generálunk egy szöveges összefoglalót
            if analysis_results:
                analysis_results["synthesis"] = (
                    "Synthesis feature is currently disabled."
                )

        except ValueError as e:
            logger.error(f"Hiba az elemzés közben: {e}", exc_info=True)
            # Dönthetünk úgy, hogy részleges eredményeket adunk vissza, vagy hibát dobunk.
            # Most egy hibaüzenetet adunk vissza a szintézisben.
            analysis_results["synthesis"] = f"Elemzési hiba: {e}"

        return analysis_results


__all__ = [
    "RealTimeAIAnalyzer",
    "TechnicalAnalyzer",
    "FundamentalAnalyzer",
    "SentimentAnalyzer",
]

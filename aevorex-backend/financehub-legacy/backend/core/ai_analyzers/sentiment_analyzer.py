# core/ai_analyzers/sentiment_analyzer.py

"""
Sentiment Analyzer (OpenRouter-backed)
======================================

This module replaces the previous dummy sentiment analyzer with a real
LLM-powered implementation, using the UnifiedAIService + OpenRouter.
"""

import logging
from typing import List, Dict

from backend.core.ai.unified_service import get_unified_ai_service

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Uses UnifiedAIService (OpenRouter LLM gateway) to classify sentiment
    of news items or free text as Positive / Negative / Neutral.
    """

    def __init__(self):
        self.ai_service = get_unified_ai_service()

    async def analyze(self, news_data: List[Dict[str, str]]) -> str:
        """
        Analyzes sentiment for a batch of news headlines.

        Args:
            news_data: list of dicts, each with at least {"title": str}

        Returns:
            "Positive", "Negative" or "Neutral"
        """
        if not news_data:
            return "Neutral (no news)"

        headlines = [item.get("title", "") for item in news_data if item.get("title")]
        if not headlines:
            return "Neutral (empty headlines)"

        user_prompt = (
            "Classify the overall sentiment of the following news headlines about a company.\n\n"
            + "\n".join(f"- {h}" for h in headlines[:5])  # cap at 5 to save tokens
            + "\n\nRespond with exactly one word: Positive, Negative, or Neutral."
        )

        try:
            # We don’t care about streaming here → collect final output
            result_text = ""
            async for chunk in self.ai_service.stream_chat(
                http_client=None,  # will be injected by gateway
                ticker="N/A",
                user_message=user_prompt,
                locale="en",
                plan="free",
                query_type="sentiment",
            ):
                result_text += chunk

            cleaned = result_text.strip().lower()
            if "positive" in cleaned:
                return "Positive"
            if "negative" in cleaned:
                return "Negative"
            return "Neutral"

        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return "Neutral (error)"

    async def analyze_text(self, text: str) -> str:
        """
        Analyzes sentiment for a single piece of text.
        """
        if not text:
            return "Neutral"

        user_prompt = f"Classify the sentiment of the following text as Positive, Negative, or Neutral:\n\n{text}"

        try:
            result_text = ""
            async for chunk in self.ai_service.stream_chat(
                http_client=None,
                ticker="N/A",
                user_message=user_prompt,
                locale="en",
                plan="free",
                query_type="sentiment",
            ):
                result_text += chunk

            cleaned = result_text.strip().lower()
            if "positive" in cleaned:
                return "Positive"
            if "negative" in cleaned:
                return "Negative"
            return "Neutral"

        except Exception as e:
            logger.error(f"Sentiment text analysis failed: {e}")
            return "Neutral (error)"

"""
Helper functions for the AI Summary service.
"""

import re
from typing import AsyncGenerator
import logging

from fastapi import BackgroundTasks
import httpx

from backend.core.ai.unified_service import get_unified_ai_service


logger = logging.getLogger(__name__)

# Pattern to remove common multi-sentence polite preambles from LLM responses
_LEADING_PREAMBLE_PATTERN = re.compile(
    r"^\s*(?:"
    r"(?:Okay|Sure|Certainly|Understood|I\s*(?:completely|totally)?\s*understand)"
    r"[\.\!\?]*\s*)+"
    r"(?:I\s+will\s+generate[^\.\n]{0,400}[\.\!\?]+\s*)?",
    flags=re.IGNORECASE | re.DOTALL,
)


def clean_ai_summary(text: str) -> str:
    """Return the meaningful part of the AI summary, stripping LLM fillers."""
    if not text:
        return ""
    working = text.lstrip()
    delim_match = re.search(r"^[ \t]*---[ \t]*(?:\n|$)", working, flags=re.MULTILINE)
    if delim_match:
        working = working[delim_match.end() :].lstrip("- \n")
    working = _LEADING_PREAMBLE_PATTERN.sub("", working).lstrip()
    heading_match = re.search(r"(?:^|\n)\s*(\*\*?\s*)?I\.\s", working)
    if heading_match and heading_match.start() <= 400:
        working = working[heading_match.start() :]
    return working.strip()


async def generate_prompt_from_template(
    symbol: str, company_overview, financials_data, latest_indicators, news_items
):
    """Generates a prompt for AI analysis based on a template."""
    # This is a placeholder for a more sophisticated template-based prompt generation
    # For now, it creates a simple concatenation of data.
    prompt = f"Provide a comprehensive financial analysis for {symbol}.\n\n"
    if company_overview:
        prompt += f"Company Overview: {company_overview}\n\n"
    if financials_data:
        prompt += f"Financials: {financials_data}\n\n"
    if latest_indicators:
        prompt += f"Latest Indicators: {latest_indicators}\n\n"
    if news_items:
        prompt += f"Recent News: {news_items}\n\n"
    return prompt


async def stream_openai_response(
    prompt: str,
    background_tasks: BackgroundTasks,
    request_id: str,
    ticker: str = "N/A",
    locale: str | None = None,
    plan: str = "pro",
) -> AsyncGenerator[str, None]:
    """
    Stream response from UnifiedAIService using OpenRouterGateway.
    """
    ai_service = get_unified_ai_service()
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        async for chunk in ai_service.stream_chat(
            http_client=http_client,
            ticker=ticker,
            user_message=prompt,
            locale=locale,
            plan=plan,
            context_messages=None,
            query_type="summary",
            data_block=None,
        ):
            yield chunk


async def generate_summary_for_stock_data(
    symbol: str, company_overview, financials_data, latest_indicators, news_items
) -> dict:
    """
    Generate a non-streaming AI summary for given stock data.
    """
    prompt = await generate_prompt_from_template(
        symbol, company_overview, financials_data, latest_indicators, news_items
    )

    ai_service = get_unified_ai_service()
    async with httpx.AsyncClient(timeout=60.0) as http_client:
        summary_text = await ai_service.generate_market_daily_summary(
            http_client=http_client,
            news_data=[{"title": f"AI-generated analysis context for {symbol}"}],
        )
        return {"summary": summary_text.get("summary", prompt)}

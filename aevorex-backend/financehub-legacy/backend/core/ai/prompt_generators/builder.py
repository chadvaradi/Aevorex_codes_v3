# ==============================================================================
# backend/core./prompt_generators/builder.py
# Aevorex FinBot Prompt Generation Service
# ==============================================================================

import time
import asyncio
from datetime import datetime, timezone
import logging

# Core imports with settings

# Formatters from the same package
from .price_formatter import format_price_data_for_prompt
from .indicator_formatter import format_indicator_data_for_prompt
from .news_formatter import format_news_data_for_prompt
from .fundamental_formatter import format_fundamental_data_for_prompt
from .financials_formatter import format_financials_data_for_prompt
from .earnings_formatter import format_earnings_data_for_prompt

# Constants from the same package
from .constants import (
    PROMPT_TEMPLATE_DIR,
    FALLBACK_PRICE_DATA,
    FALLBACK_INDICATOR_DATA,
    FALLBACK_NEWS_DATA,
    FALLBACK_FUNDAMENTAL_DATA,
    FALLBACK_FINANCIALS_DATA,
    FALLBACK_EARNINGS_DATA,
)


# Imports with proper error handling
from ....models.stock import FinBotStockResponse

# Configure logger
logger = logging.getLogger(__name__)


async def generate_ai_prompt_premium(
    symbol: str,
    stock_data: FinBotStockResponse,
    template_filename: str = "summary_v4.txt",
) -> str:
    """
    Generates a comprehensive AI prompt by aggregating various data points,
    formatting them, and injecting them into a text template.
    This version includes financials and earnings data.
    """
    func_name = "generate_ai_prompt_premium"
    logger.info(f"[{symbol}] Running {func_name} with template '{template_filename}'..")

    start_time = time.monotonic()

    # ------------------------------------------------------------------
    # 1. Gather raw values in a backward-compatible way
    #    The FinBotStockResponse model has evolved over time.  To keep the
    #    prompt generator resilient we look for both the *old* and *new*
    #    attribute names and gracefully fall back to ``None`` when absent.
    # ------------------------------------------------------------------

    # Price / OHLCV history – original attribute: ``df_recent`` (DataFrame)
    # → new unified attribute: ``history_ohlcv`` (list[dict])
    raw_price_source = getattr(stock_data, "df_recent", None) or getattr(
        stock_data, "history_ohlcv", None
    )

    # Latest indicator values – unchanged in newer schema, but keep safe-get
    raw_latest_indicators = getattr(stock_data, "latest_indicators", None) or {}

    # News items – moved under ``news.items`` container in the newer schema
    if hasattr(stock_data, "news") and getattr(stock_data.news, "items", None):
        raw_news_items = stock_data.news.items
    else:
        raw_news_items = getattr(stock_data, "news_items", None) or []

    # Fundamental overview – field name unchanged
    raw_company_overview = getattr(stock_data, "company_overview", None)

    # Financial & earnings – names consolidated in latest schema
    raw_financials = getattr(stock_data, "financials", None) or getattr(
        stock_data, "financials_data", None
    )
    raw_earnings = getattr(stock_data, "earnings", None) or getattr(
        stock_data, "earnings_data", None
    )

    # 2. Build async formatting tasks using the resolved raw values
    tasks = {
        "price_data": format_price_data_for_prompt(symbol, raw_price_source),
        "indicator_data": format_indicator_data_for_prompt(
            symbol, raw_latest_indicators, raw_price_source
        ),
        "news_data": format_news_data_for_prompt(symbol, raw_news_items),
        "fundamental_data": format_fundamental_data_for_prompt(
            symbol, raw_company_overview
        ),
        "financials_data": format_financials_data_for_prompt(symbol, raw_financials),
        "earnings_data": format_earnings_data_for_prompt(symbol, raw_earnings),
    }

    # 2. Execute all formatting tasks concurrently
    logger.debug(
        f"[{symbol}] {func_name}: Executing {len(tasks)} formatting tasks concurrently.."
    )
    results = await asyncio.gather(*tasks.values())
    logger.debug(f"[{symbol}] {func_name}: All formatting tasks completed.")

    # 3. Create a dictionary from the results
    formatted_data = dict(zip(tasks.keys(), results))

    # Handle Tuple returns from formatters
    indicator_text, _ = formatted_data.get(
        "indicator_data", (FALLBACK_INDICATOR_DATA, False)
    )
    news_text, _ = formatted_data.get("news_data", (FALLBACK_NEWS_DATA, False))
    fundamental_text, _ = formatted_data.get(
        "fundamental_data", (FALLBACK_FUNDAMENTAL_DATA, False)
    )

    # Assemble the context dictionary for the template
    current_utc_time = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    prompt_context = {
        "ticker": symbol,
        "current_date": current_utc_time,
        "price_data_json": formatted_data.get("price_data", FALLBACK_PRICE_DATA),
        "indicator_summary": indicator_text,
        "news_summary": news_text,
        "company_profile": fundamental_text,
        "financials_summary": formatted_data.get(
            "financials_data", FALLBACK_FINANCIALS_DATA
        ),
        "earnings_summary": formatted_data.get("earnings_data", FALLBACK_EARNINGS_DATA),
    }

    # 4. Load the prompt template from file
    try:
        template_path = PROMPT_TEMPLATE_DIR / template_filename
        logger.debug(
            f"[{symbol}] {func_name}: Loading prompt template from: {template_path}"
        )
        with open(template_path, encoding="utf-8") as f:
            template_str = f.read()
    except FileNotFoundError:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Prompt template file not found at '{template_path}'."
        )
        return f"CRITICAL_ERROR: PROMPT_TEMPLATE_NOT_FOUND: '{template_path}'"
    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Failed to read prompt template file: {e}",
            exc_info=True,
        )
        return f"CRITICAL_ERROR: FAILED_TO_READ_PROMPT_TEMPLATE: '{e}'"

    # 5. Substitute the context into the template
    try:
        final_prompt = template_str.format(**prompt_context)
        logger.info(f"[{symbol}] {func_name}: Successfully generated final prompt.")
    except KeyError as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Missing key in prompt template: {e}. Available keys: {list(prompt_context.keys())}"
        )
        return f"CRITICAL_ERROR: PROMPT_TEMPLATE_KEY_ERROR: Missing key '{e}'"
    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Failed to format prompt template: {e}",
            exc_info=True,
        )
        return f"CRITICAL_ERROR: FAILED_TO_FORMAT_PROMPT: '{e}'"

    end_time = time.monotonic()
    duration_ms = (end_time - start_time) * 1000
    logger.info(f"[{symbol}] {func_name}: Total execution time: {duration_ms:.2f} ms")

    return final_prompt

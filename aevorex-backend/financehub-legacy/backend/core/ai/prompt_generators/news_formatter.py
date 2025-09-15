from __future__ import annotations

from datetime import datetime, timezone

from ....config import settings
from .constants import (
    FALLBACK_NEWS_DATA,
    DEFAULT_TARGET_NEWS_COUNT,
    DEFAULT_RELEVANCE_THRESHOLD,
)
from ....models.stock import NewsItem
from ....utils.logger_config import get_logger


logger = get_logger(__name__)


async def format_news_data_for_prompt(
    symbol: str, news_items: list[NewsItem] | None
) -> tuple[str, bool]:
    """
    Formats a list of news items into a structured string for the AI prompt.
    Filters by relevance, sorts by date, and limits the count.
    Handles potential errors gracefully and ALWAYS returns a (string, bool) tuple.
    """
    func_name = "format_news_data_for_prompt"
    logger.debug(f"[{symbol}] Running {func_name}..")
    if not news_items:
        logger.warning(f"[{symbol}] {func_name}: Skipping, no news items provided.")
        return "Nincsenek elérhető hírek.", False

    try:
        # Get configuration, fallback to default if not available
        ai_settings = getattr(settings, "AI", None)
        relevance_threshold = (
            getattr(ai_settings, "RELEVANCE_THRESHOLD", DEFAULT_RELEVANCE_THRESHOLD)
            if ai_settings
            else DEFAULT_RELEVANCE_THRESHOLD
        )
        target_news_count = (
            getattr(ai_settings, "TARGET_NEWS_COUNT", DEFAULT_TARGET_NEWS_COUNT)
            if ai_settings
            else DEFAULT_TARGET_NEWS_COUNT
        )
        logger.debug(
            f"[{symbol}] {func_name}: Config values - Relevance Threshold: {relevance_threshold}, Target News Count: {target_news_count}"
        )

        # --- Filtering ---
        logger.debug(
            f"[{symbol}] {func_name}: Filtering {len(news_items)} news items by relevance_score. {relevance_threshold}.."
        )
        relevant_items = [
            item
            for item in news_items
            if item.relevance_score is not None
            and item.relevance_score >= relevance_threshold
        ]
        logger.debug(
            f"[{symbol}] {func_name}: Found {len(relevant_items)} relevant news items."
        )

        if not relevant_items:
            return "Nincsenek releváns hírek a megadott küszöbérték felett.", False

        # --- Sorting ---
        def get_sort_key(item: NewsItem) -> datetime:
            # Use NewsItem.published_at (AwareDatetime) for sorting
            # If for some reason it's naive, assume UTC.
            if item.published_at is None:
                return datetime.min.replace(
                    tzinfo=timezone.utc
                )  # Push items without date to the end
            if item.published_at.tzinfo is None:
                return item.published_at.replace(tzinfo=timezone.utc)
            return item.published_at

        logger.debug(
            f"[{symbol}] {func_name}: Sorting {len(relevant_items)} relevant items by 'published_at' descending.."
        )
        try:
            sorted_items = sorted(relevant_items, key=get_sort_key, reverse=True)
        except Exception as e:
            logger.error(
                f"[{symbol}] {func_name}: CRITICAL - Error during news sorting: {e}",
                exc_info=True,
            )
            # Fallback: try to use the list as is, maybe it's partially sorted
            sorted_items = relevant_items

        # --- Limiting and Formatting ---
        logger.debug(
            f"[{symbol}] {func_name}: Limiting to the top {target_news_count} items and formatting.."
        )
        limited_items = sorted_items[:target_news_count]

        formatted_news_list = []
        for i, item in enumerate(limited_items):
            # Format published_at, handling potential None
            date_str = (
                item.published_at.strftime("%Y-%m-%d")
                if item.published_at
                else "Ismeretlen dátum"
            )

            # Format title and source
            title = item.title.strip() if item.title else "Cím nélküli hír"
            source = item.source.strip() if item.source else "Ismeretlen forrás"

            # Add to list
            formatted_news_list.append(f"{i + 1}. [{date_str}, {source}] {title}")

        if not formatted_news_list:
            logger.warning(
                f"[{symbol}] {func_name}: No news items remained after formatting."
            )
            return "Nem sikerült a híreket formázni.", False

        final_summary = "\n".join(formatted_news_list)
        logger.debug(
            f"[{symbol}] {func_name}: Successfully formatted {len(limited_items)} news items."
        )
        return final_summary, True

    except Exception as e:
        logger.error(
            f"[{symbol}] {func_name}: CRITICAL - Unexpected error: {e}", exc_info=True
        )
        return FALLBACK_NEWS_DATA, False

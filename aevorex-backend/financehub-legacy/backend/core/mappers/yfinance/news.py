from typing import Any
from backend.core.mappers._mapper_base import (
    logger,
    StandardNewsDict,
    YFINANCE_NEWS_DEFAULT_SOURCE_NAME,
)
from backend.core.helpers import _clean_value, parse_timestamp_to_iso_utc, normalize_url


def map_yfinance_news_to_standard_dicts(
    raw_item: dict[str, Any], request_id: str | None = "N/A_REQ_ID"
) -> StandardNewsDict | None:
    """
    Maps a raw dictionary from yfinance Ticker.news to the StandardNewsDict format.
    Prioritizes data from the 'content' sub-dictionary, with fallbacks to root-level fields.
    Ensures 'published_on_raw_val' is defined before use to prevent UnboundLocalError.
    Args:
        raw_item: A dictionary representing a single news item from yfinance.
        request_id: An optional request identifier for logging purposes.
    Returns:
        A StandardNewsDict if mapping is successful, otherwise None.
    """
    func_name = "map_yfinance_news_to_standard_dicts"
    item_uuid = raw_item.get("uuid", "N/A_UUID")
    log_prefix = f"[{request_id}][{func_name}][UUID:{item_uuid}]"

    if not isinstance(raw_item, dict):
        logger.warning(
            f"{log_prefix} Input raw_item is not a dict (Type: {type(raw_item)}). Skipping."
        )
        return None

    content_dict_raw = raw_item.get("content")
    content_dict: dict[str, Any]

    if isinstance(content_dict_raw, dict):
        content_dict = content_dict_raw
    else:
        if content_dict_raw is not None:
            logger.warning(
                f"{log_prefix} 'content' field is present but not a dict (Type: {type(content_dict_raw)}). "
                f"Treating as empty for structured access. Raw 'content': {str(content_dict_raw)[:200]}"
            )
        content_dict = {}

    published_on_raw_val: Any = None
    source_field_date: str = "unknown"

    if "pubDate" in content_dict and content_dict.get("pubDate") is not None:
        published_on_raw_val = content_dict.get("pubDate")
        source_field_date = "content.pubDate"
    elif "displayTime" in content_dict and content_dict.get("displayTime") is not None:
        published_on_raw_val = content_dict.get("displayTime")
        source_field_date = "content.displayTime"

    if published_on_raw_val is None and raw_item.get("providerPublishTime") is not None:
        published_on_raw_val = raw_item.get("providerPublishTime")
        source_field_date = "root.providerPublishTime"
        logger.debug(
            f"{log_prefix} Date not in 'content', using fallback '{source_field_date}': {published_on_raw_val}"
        )

    published_utc_str: str | None = None
    if published_on_raw_val is not None:
        try:
            published_utc_str = parse_timestamp_to_iso_utc(
                published_on_raw_val,
                context=f"{log_prefix}:timestamp_from_{source_field_date}",
            )
            if published_utc_str:
                logger.debug(
                    f"{log_prefix} Parsed timestamp from '{source_field_date}': Raw='{published_on_raw_val}' -> ISO='{published_utc_str}'"
                )
            else:
                logger.warning(
                    f"{log_prefix} Timestamp from '{source_field_date}' (Raw='{published_on_raw_val}') parsed to None by helper. Timestamp will be None."
                )
        except ValueError as e_ts:
            logger.warning(
                f"{log_prefix} Failed to parse timestamp from '{source_field_date}': Raw='{published_on_raw_val}'. Error: {e_ts}. Timestamp will be None."
            )
    else:
        logger.debug(
            f"{log_prefix} No suitable timestamp field found or value was None ('content.pubDate', 'content.displayTime', or 'root.providerPublishTime'). Timestamp will be None."
        )

    raw_title_value: Any = None
    source_field_title: str = "unknown"

    if content_dict.get("title"):
        raw_title_value = content_dict.get("title")
        source_field_title = "content.title"
    elif content_dict.get("headline"):
        raw_title_value = content_dict.get("headline")
        source_field_title = "content.headline"

    if not raw_title_value:
        if raw_item.get("title"):
            raw_title_value = raw_item.get("title")
            source_field_title = "root.title"
        elif raw_item.get("headline"):
            raw_title_value = raw_item.get("headline")
            source_field_title = "root.headline"
        if raw_title_value:
            logger.debug(
                f"{log_prefix} Title not in 'content', using fallback '{source_field_title}'."
            )

    title = _clean_value(raw_title_value)

    if not title:
        logger.warning(
            f"{log_prefix} Skipping item: Missing or empty 'title' after cleaning. "
            f"Attempted source: '{source_field_title}', Raw value: '{str(raw_title_value)[:100]}'. "
            f"Item ID: {raw_item.get('id', 'N/A')}. Content keys: {list(content_dict.keys())}."
        )
        return None
    logger.debug(f"{log_prefix} Title extracted from '{source_field_title}': '{title}'")

    raw_url_str: str | None = None
    source_field_url: str = "unknown"

    def _get_url_from_complex_field(data_field: Any) -> str | None:
        if isinstance(data_field, dict):
            return data_field.get("url")
        if isinstance(data_field, str):
            return data_field
        return None

    if "canonicalUrl" in content_dict:
        raw_url_str = _get_url_from_complex_field(content_dict.get("canonicalUrl"))
        if raw_url_str:
            source_field_url = "content.canonicalUrl"

    if not raw_url_str and "clickThroughUrl" in content_dict:
        raw_url_str = _get_url_from_complex_field(content_dict.get("clickThroughUrl"))
        if raw_url_str:
            source_field_url = "content.clickThroughUrl"

    if not raw_url_str:
        link_val_at_root = raw_item.get("link")
        if isinstance(link_val_at_root, str):
            raw_url_str = link_val_at_root
            if raw_url_str:
                source_field_url = "root.link"
                logger.debug(
                    f"{log_prefix} URL not in 'content', using fallback '{source_field_url}'."
                )
        elif link_val_at_root is not None:
            logger.debug(
                f"{log_prefix} Root 'link' field was not a string (Type: {type(link_val_at_root)}): '{str(link_val_at_root)[:100]}'"
            )

    cleaned_raw_url = _clean_value(raw_url_str)
    url_normalized_str: str | None = normalize_url(cleaned_raw_url)

    if not url_normalized_str:
        logger.warning(
            f"{log_prefix} Skipping item: Invalid or missing URL after cleaning and normalization. "
            f"Attempted source: '{source_field_url}', Raw URL string: '{str(raw_url_str)[:200]}', Cleaned: '{cleaned_raw_url}'. Title: '{title}'"
        )
        return None
    logger.debug(
        f"{log_prefix} URL extracted from '{source_field_url}', Normalized: '{url_normalized_str}'"
    )

    raw_publisher_name: str | None = None
    source_field_publisher: str = "unknown"

    if content_dict.get("publisher"):
        raw_publisher_name = content_dict.get("publisher")
        source_field_publisher = "content.publisher"
    elif raw_item.get("publisher"):
        raw_publisher_name = raw_item.get("publisher")
        source_field_publisher = "root.publisher"
        if raw_publisher_name:
            logger.debug(
                f"{log_prefix} Publisher not in 'content', using fallback '{source_field_publisher}'."
            )

    publisher = _clean_value(raw_publisher_name)
    logger.debug(
        f"{log_prefix} Publisher extracted from '{source_field_publisher}': '{publisher}'"
    )

    summary_raw = content_dict.get("summary", "")
    summary_cleaned = _clean_value(summary_raw)

    final_publisher = publisher or YFINANCE_NEWS_DEFAULT_SOURCE_NAME

    return {
        "uuid": item_uuid,
        "title": title,
        "url": url_normalized_str,
        "publisher": final_publisher,
        "published_on": published_utc_str,
        "summary": summary_cleaned
        if summary_cleaned
        else f"Summary for '{title}' was not available.",
        "source": YFINANCE_NEWS_DEFAULT_SOURCE_NAME,
    }

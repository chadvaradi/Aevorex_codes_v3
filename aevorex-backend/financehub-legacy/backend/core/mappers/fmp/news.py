# Aevorex_codes/modules/financehub/backend/core/mappers/fmp/news.py
from typing import Any
from pydantic import HttpUrl

from backend.core.helpers import _clean_value, normalize_url, parse_timestamp_to_iso_utc
from backend.core.mappers._mapper_base import logger, StandardNewsDict, DEFAULT_NA_VALUE


def map_fmp_item_to_standard(
    raw_item: dict[str, Any], api_source: str
) -> StandardNewsDict | None:
    """
    Maps a raw dictionary item from an FMP news endpoint to the standardized StandardNewsDict format.
    """
    func_name = "map_fmp_item_to_standard"
    log_prefix = f"[{api_source}][{func_name}]"

    if not isinstance(raw_item, dict):
        logger.warning(
            f"{log_prefix} Input raw_item is not a dictionary. Type: {type(raw_item)}. Skipping."
        )
        return None

    try:
        title = _clean_value(raw_item.get("title"))
        raw_url = _clean_value(raw_item.get("url"))
        published_str = _clean_value(raw_item.get("publishedDate"))
        snippet = _clean_value(raw_item.get("text"))
        source_name = _clean_value(raw_item.get("site"))
        raw_image_url = _clean_value(raw_item.get("image"))
        ticker_symbol = _clean_value(raw_item.get("symbol"))

        if not title or not raw_url or not published_str:
            return None

        url: HttpUrl | None = normalize_url(raw_url)
        if not url:
            return None

        published_utc: str | None = parse_timestamp_to_iso_utc(
            timestamp_str=published_str,
            context=f"{log_prefix} Field: 'publishedDate', URL: {str(url)}",
        )
        if not published_utc:
            return None

        image_url: HttpUrl | None = None
        if raw_image_url and raw_image_url.strip():
            image_url = normalize_url(raw_image_url)

        tickers: list[str] = []
        if ticker_symbol and isinstance(ticker_symbol, str) and ticker_symbol.strip():
            tickers.append(ticker_symbol.strip().upper())

        standard_dict: StandardNewsDict = {
            "title": title,
            "url": str(url),
            "published_utc": published_utc,
            "source_name": source_name if source_name else "FMP",
            "snippet": snippet if snippet else title,
            "image_url": str(image_url) if image_url else None,
            "tickers": tickers,
            "api_source": api_source,
            "sentiment_score": None,
            "sentiment_label": None,
            "full_text": snippet,
            "authors": [],
            "tags_keywords": [],
            "source_feed_url": None,
            "meta_data": {
                "fmp_original_symbol": raw_item.get("symbol", DEFAULT_NA_VALUE)
            },
        }
        return standard_dict

    except Exception as e:
        logger.error(
            f"{log_prefix} Unexpected error mapping FMP news item (URL: {raw_item.get('url', 'N/A')}): {e}",
            exc_info=True,
        )
        return None

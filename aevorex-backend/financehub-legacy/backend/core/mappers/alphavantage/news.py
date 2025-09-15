from typing import Any
from pydantic import HttpUrl
from datetime import datetime, timezone

from backend.core.mappers._mapper_base import logger, StandardNewsDict
from backend.core.helpers import _clean_value, parse_optional_float, normalize_url


def map_alphavantage_item_to_standard(
    raw_item: dict[str, Any],
) -> StandardNewsDict | None:
    """
    Maps a single raw news item from Alpha Vantage to the StandardNewsDict format.
    Performs data cleaning, validation, and type conversion.
    """
    log_prefix = "[alphavantage_news_item_mapper]"

    if not isinstance(raw_item, dict):
        logger.warning(
            f"{log_prefix} Input raw_item is not a dict. Type: {type(raw_item)}. Skipping."
        )
        return None

    try:
        title = _clean_value(raw_item.get("title"))
        raw_url = _clean_value(raw_item.get("url"))
        published_str = _clean_value(raw_item.get("time_published"))

        url: HttpUrl | None = normalize_url(raw_url, log_prefix=log_prefix)

        if not title:
            logger.warning(
                f"{log_prefix} Skipping item: Missing or empty 'title'. Raw URL: {raw_url}"
            )
            return None
        if not url:
            logger.warning(
                f"{log_prefix} Skipping item: Invalid or missing 'url'. Original raw_url: {raw_url}"
            )
            return None
        if not published_str:
            logger.warning(
                f"{log_prefix} Skipping item: Missing 'time_published' field. URL: {url}"
            )
            return None

        published_utc: str | None = None
        try:
            dt_naive = datetime.strptime(published_str, "%Y%m%dT%H%M%S")
            dt_aware = dt_naive.replace(tzinfo=timezone.utc)
            published_utc = dt_aware.isoformat(timespec="seconds").replace(
                "+00:00", "Z"
            )
        except (ValueError, TypeError) as e_time:
            logger.warning(
                f"{log_prefix} Skipping item: Could not parse 'time_published' string '{published_str}'. Error: {e_time}. URL: {url}"
            )
            return None

        snippet = _clean_value(raw_item.get("summary"))
        source_name = _clean_value(raw_item.get("source"))
        source_domain = _clean_value(raw_item.get("source_domain"))
        raw_image_url = _clean_value(raw_item.get("banner_image"))
        image_url: HttpUrl | None = (
            normalize_url(raw_image_url, log_prefix=log_prefix)
            if raw_image_url
            else None
        )

        tickers: list[str] = []
        overall_sentiment_score: float | None = None
        overall_sentiment_label: str | None = None

        ticker_sentiment_list = raw_item.get("ticker_sentiment", [])
        if isinstance(ticker_sentiment_list, list):
            for ts_item in ticker_sentiment_list:
                if isinstance(ts_item, dict):
                    ticker = _clean_value(ts_item.get("ticker"))
                    if ticker and isinstance(ticker, str):
                        tickers.append(ticker.upper())

            overall_sentiment_score_raw = raw_item.get("overall_sentiment_score")
            overall_sentiment_score = parse_optional_float(
                overall_sentiment_score_raw,
                context=f"{log_prefix}:overall_sentiment_score for URL {url}",
            )
            overall_sentiment_label = _clean_value(
                raw_item.get("overall_sentiment_label")
            )

            if overall_sentiment_label and overall_sentiment_label.lower() == "neutral":
                overall_sentiment_label = "Neutral"

        standard_dict: StandardNewsDict = {
            "title": title,
            "url": str(url),
            "published_utc": published_utc,
            "source_name": source_name
            if source_name
            else source_domain
            if source_domain
            else "Alpha Vantage",
            "snippet": snippet if snippet else title,
            "image_url": str(image_url) if image_url else None,
            "tickers": tickers,
            "api_source": "alphavantage",
            "sentiment_score": overall_sentiment_score,
            "sentiment_label": overall_sentiment_label,
        }
        return standard_dict

    except Exception as e:
        logger.error(
            f"{log_prefix} Unexpected error mapping news item (URL: {raw_item.get('url', 'N/A')}): {e}",
            exc_info=True,
        )
        return None

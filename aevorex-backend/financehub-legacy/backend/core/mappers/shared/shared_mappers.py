# backend/core/mappers/_shared_mappers.py
# ==============================================================================
# Shared Components for the Data Mappers Package - V2 (Refactored Imports)
# ==============================================================================
# Contains the primary news mapping orchestrator functions. Imports base
# definitions/types from _mapper_base and relies on sibling modules for
# dynamic validation and source-specific internal mapping logic.
# ==============================================================================

import time
import uuid
from typing import Optional, Any, Final, cast
from collections.abc import Callable

# import pandas as pd # <<< JAVÍTVA: TÖRÖLVE (safe_get átkerült)
from pydantic import BaseModel, HttpUrl  # For orchestrator function signatures/usage

# --- 1. Import Base Components FIRST ---
from .._mapper_base import logger, DEFAULT_NA_VALUE, StandardNewsDict

# --- 2. Import Core Utilities ---
from ....core.helpers import _clean_value

# --- 3. Import Sibling Internal Mapper Components ---
from .._dynamic_validator import _dynamic_import_and_validate
from .. import yfinance, marketaux, fmp, newsapi, alphavantage

# --- Constants Specific to this Shared Logic ---
SERVICE_NAME: Final[str] = "MappersSharedLogic"
__version__: Final[str] = "1.1.1"  # Version bump

# ==============================================================================
# === Shared Helper Functions Defined Here ===
# ==============================================================================


# ==============================================================================
# === News Mapping Orchestration Logic ===
# ==============================================================================

# --- Type Aliases for Internal Mappers ---
# These use StandardNewsDict which is imported from _mapper_base
InternalMapperFunc = Callable[[dict[str, Any]], Optional[StandardNewsDict]]
InternalMapperFuncWithSource = Callable[
    [dict[str, Any], str], Optional[StandardNewsDict]
]

# --- Dispatch Dictionary for Internal Mappers ---
# Populated using the imported source-specific modules.
# Ensure functions exist in the respective files.
_INTERNAL_MAPPERS: dict[str, InternalMapperFunc | InternalMapperFuncWithSource] = {
    # FIGYELEM: A felhasználói utasítás szerint cserélve. Ez szemantikailag
    # helytelen lehet, mivel a news mapper-be egy overview mapper van bekötve.
    "yfinance": yfinance.map_yfinance_news_to_standard_dicts,
    "marketaux": marketaux._map_marketaux_item_to_standard,  # HELYES név a marketaux.py-ból
    "fmp_stock": lambda item: fmp.map_fmp_item_to_standard(item, "fmp_stock"),
    "fmp_press": lambda item: fmp.map_fmp_item_to_standard(item, "fmp_press"),
    "newsapi": newsapi._map_newsapi_item_to_standard,
    "alphavantage": alphavantage.map_alphavantage_item_to_standard,
}


# --- Stage 1: Raw API Dicts -> List[StandardNewsDict] ---
def map_raw_news_to_standard_dicts(
    raw_news_list: list[dict[str, Any]] | None, source_api_name: str
) -> list[StandardNewsDict]:
    func_name = "map_raw_news_to_standard_dicts"
    source_lower = source_api_name.lower()
    log_prefix = f"[{source_lower}][{func_name}]"

    if not raw_news_list:
        logger.debug(f"{log_prefix} Input is None or empty list.")
        return []

    mapper_func = _INTERNAL_MAPPERS.get(source_lower)
    if mapper_func is None:
        logger.error(f"{log_prefix} No internal mapper for '{source_lower}'.")
        return []

    logger.info(f"{log_prefix} Mapping {len(raw_news_list)} items...")
    t_start = time.monotonic()
    std_dicts = []
    skipped = 0
    processed = 0

    for i, item in enumerate(raw_news_list):
        try:
            std_dict = (
                cast(InternalMapperFunc, mapper_func)(item)
                if source_lower not in ["fmp_stock", "fmp_press"]
                else cast(InternalMapperFuncWithSource, mapper_func)(item, source_lower)
            )
            if std_dict:
                std_dicts.append(std_dict)
                processed += 1
            else:
                skipped += 1
        except Exception as e:
            logger.error(
                f"{log_prefix} Error mapping item #{i + 1}: {e}", exc_info=True
            )
            skipped += 1
            continue

    t_end = time.monotonic()
    logger.info(
        f"{log_prefix} Mapping done. Proc: {processed}, Skip: {skipped}. Took: {t_end - t_start:.4f}s"
    )
    return std_dicts


# --- Stage 2: List[StandardNewsDict] -> List[Validated NewsItem Models] ---
def map_standard_dicts_to_newsitems(
    standard_news_dicts: list[
        StandardNewsDict
    ],  # Takes list of the type defined in base
    target_symbol: str,
) -> list[BaseModel]:  # Returns List[NewsItem] as BaseModel
    """
    Maps standardized news dictionaries to validated NewsItem Pydantic models,
    including TickerSentiment generation and dynamic validation.
    """
    # This function now relies on:
    # - logger, DEFAULT_NA_VALUE, StandardNewsDict (from _mapper_base)
    # - _clean_value (from ...utils.helpers)
    # - _dynamic_import_and_validate (from ._dynamic_validator)
    # - BaseModel, HttpUrl (from pydantic)
    # - time, uuid, List, Optional, Dict, Any, cast (from typing)
    func_name = "map_standard_dicts_to_newsitems"
    target_symbol_upper = target_symbol.upper()
    log_prefix = f"[{target_symbol_upper}][{func_name}]"

    if not standard_news_dicts:
        logger.debug(
            f"{log_prefix} Input standard_news_dicts list is empty. Returning []."
        )
        return []

    logger.info(
        f"{log_prefix} Mapping {len(standard_news_dicts)} standard dicts to NewsItem models..."
    )
    map_start_time = time.monotonic()
    mapped_items: list[BaseModel] = []
    item_validation_errors = 0
    skipped_ticker_sentiments = 0

    for i, std_dict in enumerate(standard_news_dicts):
        item_log_prefix = f"{log_prefix}[StdItem #{i + 1}]"
        news_item_added = False
        generated_uuid = "N/A"  # For logging

        try:
            # --- 1. Get key fields from StandardNewsDict ---
            url_value_raw = std_dict.get("url")
            title_value = std_dict.get("title")
            std_dict.get("published_utc")  # Can be None

            # --- 2. Validate essential fields & Generate UUID ---
            if not title_value:
                logger.warning(f"{item_log_prefix} Skipping: Missing title.")
                item_validation_errors += 1
                continue
            if not url_value_raw or not isinstance(url_value_raw, (HttpUrl, str)):
                logger.warning(
                    f"{item_log_prefix} Skipping: Missing or invalid URL type ({type(url_value_raw)})."
                )
                item_validation_errors += 1
                continue
            try:
                url_str_for_uuid = str(url_value_raw)
                generated_uuid = uuid.uuid5(uuid.NAMESPACE_URL, url_str_for_uuid).hex
            except Exception as e_uuid:
                logger.error(
                    f"{item_log_prefix} Skipping: Failed UUID generation: {e_uuid}."
                )
                item_validation_errors += 1
                continue

            # --- 3. Prepare & Validate TickerSentiments ---
            ticker_sentiments_to_validate: list[dict[str, Any]] = []
            processed_tickers: set[str] = set()
            sentiment_score = std_dict.get("sentiment_score")
            sentiment_label = std_dict.get("sentiment_label")

            # Add target symbol sentiment
            ts_data_target = {
                "ticker": target_symbol_upper,
                "relevance_score": 1.0,
                "sentiment_score": sentiment_score,
                "sentiment_label": sentiment_label,
            }
            ticker_sentiments_to_validate.append(ts_data_target)
            processed_tickers.add(target_symbol_upper)

            # Add related tickers' sentiment
            related_tickers_raw = std_dict.get("tickers", [])
            if isinstance(related_tickers_raw, list):
                for ticker_raw in related_tickers_raw:
                    related_ticker_cleaned = _clean_value(
                        ticker_raw
                    )  # Uses imported helper
                    if related_ticker_cleaned and isinstance(
                        related_ticker_cleaned, str
                    ):
                        related_ticker_upper = related_ticker_cleaned.upper()
                        if (
                            related_ticker_upper
                            and related_ticker_upper != target_symbol_upper
                            and related_ticker_upper not in processed_tickers
                        ):
                            ts_data_related = {
                                "ticker": related_ticker_upper,
                                "relevance_score": 0.5,
                                "sentiment_score": sentiment_score,
                                "sentiment_label": sentiment_label,
                            }
                            ticker_sentiments_to_validate.append(ts_data_related)
                            processed_tickers.add(related_ticker_upper)

            # Validate TickerSentiment dicts
            ticker_sentiments_validated: list[BaseModel] = []
            for ts_data in ticker_sentiments_to_validate:
                ts_log_prefix = (
                    f"{item_log_prefix}[Ticker: {ts_data.get('ticker', '?')}]"
                )
                validated_ts = _dynamic_import_and_validate(
                    "TickerSentiment", ts_data, ts_log_prefix
                )  # Uses imported validator
                if validated_ts:
                    ticker_sentiments_validated.append(validated_ts)
                else:
                    skipped_ticker_sentiments += 1  # Error logged by validator

            # --- 4. Prepare NewsItem Data ---
            news_item_data = {
                # NewsItem mezőnév : StandardNewsDict kulcsnév (vagy feldolgozott érték)
                "uuid": generated_uuid,  # A NewsItem 'uuid' mezője (aliasa 'source_unique_id')
                "title": title_value,
                # A NewsItem 'link' mezője (aliasa 'article_url') HttpUrl típusú.
                # A std_dict.get("url") már HttpUrl vagy None lehet a forrás-specifikus mapperekből.
                # A Pydantic validátor a NewsItem-en majd kezeli.
                "link": std_dict.get("url"),
                # A NewsItem 'image_url' mezője HttpUrl típusú.
                # A std_dict.get("image_url") már HttpUrl vagy None lehet.
                "image_url": std_dict.get("image_url"),
                # A NewsItem 'publisher' mezője (aliasa 'source_name')
                "publisher": std_dict.get("source_name", DEFAULT_NA_VALUE),
                # A NewsItem modellben a mező neve 'published_at'.
                # A StandardNewsDict-ben 'published_utc' kulcs alatt van a string dátum.
                # A NewsItem '@field_validator('published_at', ...)' validátora fogja ezt AwareDatetime-ra alakítani.
                "published_at": std_dict.get(
                    "published_utc"
                ),  # <<< JAVÍTVA ERRE A KULCSNÉVRE
                "content": std_dict.get(
                    "content"
                ),  # Ha a NewsItem modellben van 'content' mező
                "summary": std_dict.get("snippet", title_value),
                # A NewsItem modellben 'source_api' a mező neve (aliasa 'raw_data_provider').
                # A StandardNewsDict-ből az 'api_source' kulcsot használjuk.
                "source_api": std_dict.get("api_source", DEFAULT_NA_VALUE),
                # A NewsItem modellben 'symbols' a mező neve (aliasa 'related_tickers').
                # A StandardNewsDict-ből a 'tickers' kulcsot használjuk.
                "symbols": std_dict.get("tickers", []),
                "overall_sentiment_score": sentiment_score,
                "overall_sentiment_label": sentiment_label,
                "relevance_score": 1.0
                if target_symbol_upper in processed_tickers
                else 0.5,
                "ticker_sentiment": ticker_sentiments_validated,
            }
            # --- 5. Validate Final NewsItem ---
            validated_news_item = _dynamic_import_and_validate(
                "NewsItem", news_item_data, item_log_prefix
            )  # Uses imported validator
            if validated_news_item:
                mapped_items.append(validated_news_item)
                news_item_added = True
            else:
                # Error logged by validator
                item_validation_errors += 1

        except KeyError as e_key:  # Should be rare if StandardNewsDict is consistent
            logger.warning(
                f"{item_log_prefix} Skipping: Missing key '{e_key}' in standard dict.",
                exc_info=False,
            )
            if not news_item_added:
                item_validation_errors += 1
        except Exception as e_map_item:
            logger.error(
                f"{item_log_prefix} Skipping: Unexpected error processing standard dict: {e_map_item}. UUID: {generated_uuid}",
                exc_info=True,
            )
            if not news_item_added:
                item_validation_errors += 1

    # --- Final Logging ---
    map_duration = time.monotonic() - map_start_time
    logger.info(
        f"{log_prefix} NewsItem mapping finished. "
        f"Input: {len(standard_news_dicts)}, Validated: {len(mapped_items)}, "
        f"Item Errors: {item_validation_errors}, "
        f"Skipped TickerSentiments: {skipped_ticker_sentiments}. "
        f"Duration: {map_duration:.4f}s"
    )
    return mapped_items


# ==============================================================================
# Module Loaded Confirmation
# ==============================================================================
# Use the logger imported from base
logger.info(f"--- {SERVICE_NAME} (v{__version__}) loaded successfully. ---")

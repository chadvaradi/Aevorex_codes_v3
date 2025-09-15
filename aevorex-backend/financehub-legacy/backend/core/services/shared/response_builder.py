"""StockService – Response Builder

Contains a robust implementation of `build_stock_response_from_parallel_data` that never
returns `None`.  Missing data components are substituted with safe defaults so that the
API layer can always return HTTP 200 with a valid (though possibly sparse) payload.

This file intentionally has **zero** external side-effects and may therefore be imported
very early during application start-up without impacting legacy code paths.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd

from backend.models.stock import (
    FinBotStockResponse,
    NewsItem,
    CompanyOverview,
    FinancialsData,
    LatestOHLCV,
    IndicatorHistory,
)
from backend.core.services.stock.fundamentals_processors import FundamentalsProcessor
from backend.core.services.shared.response_helpers import (
    process_ohlcv_dataframe,
    process_technical_indicators,
)
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

__all__ = [
    "build_stock_response_from_parallel_data",
]


async def build_stock_response_from_parallel_data(
    symbol: str,
    fundamentals_raw: dict[str, Any] | None,
    technical_indicators: dict[str, Any] | None,
    news_items: list[Any] | None,
    ohlcv_df: pd.DataFrame | None,
) -> FinBotStockResponse:
    """Create a **minimal but valid** :class:`FinBotStockResponse`.

    Unlike the legacy implementation, this version **never** returns ``None``.  If a
    sub-component cannot be parsed it will simply be set to ``None`` (or an empty list in
    case of collections) while still constructing a fully validated response model.
    """

    log_prefix = f"[build_stock_resp_v2:{symbol}]"
    logger.debug("%s invoked", log_prefix)

    # ---------------------------------------------------------------------
    # Fundamentals → company_overview, financials_data, earnings_data
    # ---------------------------------------------------------------------
    company_overview = None
    financials_data = None
    earnings_data = None
    try:
        if isinstance(fundamentals_raw, dict) and fundamentals_raw:
            fundamentals_processor = FundamentalsProcessor()
            company_overview = fundamentals_processor.process_company_info(
                fundamentals_raw, symbol
            )
            financials_data = fundamentals_processor.process_financials_data(
                fundamentals_raw
            )
            earnings_data = fundamentals_processor.extract_market_metrics(
                fundamentals_raw
            )
        else:
            logger.debug(
                "%s fundamentals_raw missing or invalid – treated as empty", log_prefix
            )
    except Exception as exc:
        logger.warning(
            "%s fundamentals processing failed: %s", log_prefix, exc, exc_info=True
        )

    # ---------------------------------------------------------------------
    # News – ensure we always return a NewsData object
    # ---------------------------------------------------------------------
    from backend.models.stock.response_models import (
        NewsData,
    )  # local import to avoid circular deps

    processed_news_items: list[Any] = []
    try:
        if isinstance(news_items, list) and news_items:
            processed_news_items = [NewsItem(**item) for item in news_items]
        else:
            logger.debug("%s news_items missing/invalid – using empty list", log_prefix)
    except Exception as exc:
        logger.warning("%s news processing failed: %s", log_prefix, exc, exc_info=True)

    news_data_obj = (
        NewsData(items=processed_news_items) if processed_news_items else None
    )

    # ---------------------------------------------------------------------
    # OHLCV & history_ohlcv – convert DataFrame to list[CompanyPriceHistoryEntry]
    # ---------------------------------------------------------------------
    history_entries, latest_ohlcv = process_ohlcv_dataframe(ohlcv_df, log_prefix)

    # ---------------------------------------------------------------------
    # Latest technical indicators – ensure None/empty dict acceptable
    # ---------------------------------------------------------------------
    latest_indicators_obj = process_technical_indicators(
        technical_indicators, log_prefix
    )

    # ---------------------------------------------------------------------
    # Assemble FinBotStockResponse with safe defaults
    # ---------------------------------------------------------------------
    response = FinBotStockResponse(
        symbol=symbol.upper(),
        request_timestamp_utc=datetime.now(timezone.utc),
        data_source_info="mixed-sources-parallel",
        is_data_stale=False,
        history_ohlcv=history_entries,
        latest_ohlcv=latest_ohlcv,
        latest_indicators=latest_indicators_obj,
        company_overview=company_overview,
        financials=financials_data,
        earnings=earnings_data,
        news=news_data_obj,
    )

    logger.info(
        "%s FinBotStockResponse built. history_len=%d, news=%d",
        log_prefix,
        len(history_entries),
        len(processed_news_items),
    )
    return response


# --------------------------------------------------
# Helper utilities (internal)
# --------------------------------------------------


def _safe_float(val: Any) -> float | None:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        parsed = float(val)
        return parsed if pd.notna(parsed) else None
    except Exception:
        return None


def _safe_int(val: Any) -> int | None:
    try:
        if val is None or (isinstance(val, float) and pd.isna(val)):
            return None
        parsed = int(val)
        return parsed
    except Exception:
        return None


def build_finbot_stock_response(
    symbol: str,
    fundamentals_data: dict[str, Any] | None,
    technical_indicators: dict[str, Any] | None,
    news_items: list[dict[str, Any]] | None,
    ohlcv_df: pd.DataFrame | None,
) -> FinBotStockResponse:
    """
    Constructs the final FinBotStockResponse model from various data sources.
    """
    log_prefix = f"[ResponseBuilder:{symbol}]"
    logger.info(f"{log_prefix} Building final response model.")

    # Process Fundamentals
    company_overview = (
        CompanyOverview(**fundamentals_data.get("company_overview", {}))
        if fundamentals_data
        else CompanyOverview()
    )
    financials_data = (
        FinancialsData(**fundamentals_data.get("financials", {}))
        if fundamentals_data
        else FinancialsData()
    )

    # Process News
    from backend.models.stock.response_models import NewsData

    processed_news_items = (
        [NewsItem(**item) for item in news_items] if news_items else []
    )
    news_data_obj = (
        NewsData(items=processed_news_items) if processed_news_items else None
    )

    # Process Chart Data (OHLCV)
    latest_ohlcv_point = None
    if ohlcv_df is not None and not ohlcv_df.empty:
        ohlcv_df_sorted = ohlcv_df.sort_index()
        last_row = ohlcv_df_sorted.iloc[-1]
        latest_ohlcv_point = LatestOHLCV(
            t=int(last_row.name.timestamp()),
            o=last_row.get("open", 0),
            h=last_row.get("high", 0),
            l=last_row.get("low", 0),
            c=last_row.get("close", 0),
            v=last_row.get("volume", 0),
        )

    # Process Technical Indicators
    indicator_history = (
        IndicatorHistory(**technical_indicators)
        if technical_indicators
        else IndicatorHistory()
    )

    return FinBotStockResponse(
        symbol=symbol,
        company_overview=company_overview,
        financials=financials_data,
        news=news_data_obj,
        latest_ohlcv=latest_ohlcv_point,
        indicator_history=indicator_history,
    )

"""
Response Builder Module - Stock Response Assembly

This module handles the final assembly of stock response objects
that were previously part of the monolithic stock_data_service.py.
"""

from datetime import datetime, timezone
from typing import Any
import pandas as pd

from backend.models import (
    FinBotStockResponse,
    IndicatorHistory,
    CompanyOverview,
    NewsItem,
    CompanyPriceHistoryEntry,
    LatestOHLCV,
    FinancialsData,
    EarningsData,
)
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.ResponseBuilder")

__all__ = ["build_stock_response", "format_ohlcv_history", "build_latest_ohlcv"]


def build_stock_response(
    symbol: str,
    company_overview: CompanyOverview | None = None,
    financials_data: FinancialsData | None = None,
    earnings_data: EarningsData | None = None,
    news_items: list[NewsItem] | None = None,
    ohlcv_df: pd.DataFrame | None = None,
    indicator_history: IndicatorHistory | None = None,
    latest_indicators: dict[str, Any] | None = None,
    ai_summary: str | None = None,
    request_id: str = "response",
) -> FinBotStockResponse:
    """Build a complete FinBotStockResponse object from component data."""
    log_prefix = f"[{request_id}][Response:{symbol}]"

    try:
        logger.info(f"{log_prefix} Building stock response")

        # Format OHLCV history
        history_ohlcv = (
            format_ohlcv_history(ohlcv_df, symbol) if ohlcv_df is not None else []
        )

        # Build latest OHLCV
        latest_ohlcv = (
            build_latest_ohlcv(ohlcv_df, symbol) if ohlcv_df is not None else None
        )

        # Ensure news items is a list
        news_list = news_items if news_items is not None else []

        # Build the response object
        response = FinBotStockResponse(
            symbol=symbol.upper(),
            request_timestamp_utc=datetime.now(timezone.utc),
            data_source_info="Multi-source aggregated",
            is_data_stale=False,
            latest_ohlcv=latest_ohlcv,
            history_ohlcv=history_ohlcv,
            indicator_history=indicator_history,
            latest_indicators=latest_indicators or {},
            company_overview=company_overview,
            financials=financials_data,
            earnings=earnings_data,
            news=news_list,
            ai_summary_hu=ai_summary,
            ratings_history=[],  # Empty for now
            technical_analysis={},  # Empty for now
            metadata={},
        )

        logger.info(f"{log_prefix} Stock response built successfully")
        return response

    except Exception as e:
        logger.error(f"{log_prefix} Error building stock response: {e}", exc_info=True)
        raise


def format_ohlcv_history(
    ohlcv_df: pd.DataFrame, symbol: str
) -> list[CompanyPriceHistoryEntry]:
    """Convert OHLCV DataFrame to list of CompanyPriceHistoryEntry objects."""
    if ohlcv_df is None or ohlcv_df.empty:
        return []

    history_entries = []

    try:
        for index, row in ohlcv_df.iterrows():
            entry = CompanyPriceHistoryEntry(
                symbol=symbol,
                date=index.isoformat() if hasattr(index, "isoformat") else str(index),
                open=float(row.get("open", 0)),
                high=float(row.get("high", 0)),
                low=float(row.get("low", 0)),
                close=float(row.get("close", 0)),
                volume=int(row.get("volume", 0)),
                adj_close=float(row.get("adj_close", row.get("close", 0))),
            )
            history_entries.append(entry)

    except Exception as e:
        logger.error(f"Error formatting OHLCV history for {symbol}: {e}", exc_info=True)

    return history_entries


def build_latest_ohlcv(ohlcv_df: pd.DataFrame, symbol: str) -> LatestOHLCV | None:
    """Build LatestOHLCV object from the most recent row of OHLCV DataFrame."""
    if ohlcv_df is None or ohlcv_df.empty:
        return None

    try:
        latest_row = ohlcv_df.iloc[-1]

        return LatestOHLCV(
            symbol=symbol,
            date=latest_row.name.isoformat()
            if hasattr(latest_row.name, "isoformat")
            else str(latest_row.name),
            open=float(latest_row.get("open", 0)),
            high=float(latest_row.get("high", 0)),
            low=float(latest_row.get("low", 0)),
            close=float(latest_row.get("close", 0)),
            volume=int(latest_row.get("volume", 0)),
            adj_close=float(latest_row.get("adj_close", latest_row.get("close", 0))),
        )

    except Exception as e:
        logger.error(f"Error building latest OHLCV for {symbol}: {e}", exc_info=True)
        return None

"""
Stock Response Builder

Extracted from stock_data_service.py (3662 LOC) to follow 160 LOC rule.
Handles building and formatting of API responses for stock data.

Responsibilities:
- Building structured API responses
- Data serialization and formatting
- Response validation
- Default value handling
- Response caching preparation
"""

import pandas as pd
from typing import Any
from datetime import datetime
import uuid

from backend.models.stock import CompanyOverview, NewsItem, LatestOHLCV
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.StockResponseBuilder")


class StockResponseBuilder:
    """Service for building and formatting stock data responses."""

    def __init__(self):
        self.default_response_fields = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "data_source": "aevorex_finbot",
        }

    def build_chart_response(
        self,
        symbol: str,
        ohlcv_df: pd.DataFrame,
        latest_ohlcv: LatestOHLCV | None,
        request_id: str = None,
    ) -> dict[str, Any]:
        """Build chart data response from OHLCV DataFrame."""
        if not request_id:
            request_id = f"chart-resp-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            chart_data: list[dict] = []
            if not ohlcv_df.empty:
                prev_close: float | None = None
                for idx, row in ohlcv_df.iterrows():
                    close_val = float(row.get("close", 0))
                    # Compute daily change & percent if previous close present
                    d_val = None
                    dp_val = None
                    if prev_close is not None and prev_close != 0:
                        d_val = round(close_val - prev_close, 4)
                        dp_val = round((d_val / prev_close) * 100, 4)
                    chart_row = {
                        "timestamp": int(idx.timestamp())
                        if hasattr(idx, "timestamp")
                        else str(idx),
                        "open": float(row.get("open", 0)),
                        "high": float(row.get("high", 0)),
                        "low": float(row.get("low", 0)),
                        "close": close_val,
                        "volume": int(row.get("volume", 0)),
                    }
                    # Add change metrics only for the most recent row (to reduce payload)
                    if dp_val is not None:
                        chart_row["d"] = d_val
                        chart_row["dp"] = dp_val
                    chart_data.append(chart_row)
                    prev_close = close_val

            response = {
                "symbol": symbol,
                "chart_data": chart_data,
                "latest_ohlcv": latest_ohlcv.dict() if latest_ohlcv else None,
                "data_points": len(chart_data),
                **self.default_response_fields,
                "request_id": request_id,
            }
            logger.debug(
                f"[{request_id}] Chart response built for {symbol} with {len(chart_data)} points"
            )
            return response
        except Exception as e:
            logger.error(
                f"[{request_id}] Error building chart response for {symbol}: {e}"
            )
            return self._build_error_response(symbol, "chart_data_error", request_id)

    def build_fundamentals_response(
        self,
        symbol: str,
        company_overview: CompanyOverview | None,
        price_metrics: dict[str, Any],
        raw_ticker_info: dict[str, Any],
        request_id: str = None,
    ) -> dict[str, Any]:
        """Build fundamentals data response."""
        if not request_id:
            request_id = f"fund-resp-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            import math
            import pandas as pd

            def _clean(value):
                # Replace pandas NaN / math nan with None for JSON serialisation
                if value is None:
                    return None
                if isinstance(value, (float, int)) and (
                    math.isnan(value) if isinstance(value, float) else False
                ):
                    return None
                if pd.isna(value):
                    return None
                return value

            financial_metrics = {
                "pe_ratio": _clean(raw_ticker_info.get("trailingPE")),
                "forward_pe": _clean(raw_ticker_info.get("forwardPE")),
                "peg_ratio": _clean(raw_ticker_info.get("pegRatio")),
                "price_to_book": _clean(raw_ticker_info.get("priceToBook")),
                "price_to_sales": _clean(
                    raw_ticker_info.get("priceToSalesTrailing12Months")
                ),
                "dividend_yield": _clean(raw_ticker_info.get("dividendYield")),
                "beta": _clean(raw_ticker_info.get("beta")),
                "eps": _clean(raw_ticker_info.get("trailingEps")),
                "revenue": _clean(raw_ticker_info.get("totalRevenue")),
                "profit_margin": _clean(raw_ticker_info.get("profitMargins")),
                "operating_margin": _clean(raw_ticker_info.get("operatingMargins")),
                "return_on_equity": _clean(raw_ticker_info.get("returnOnEquity")),
                "return_on_assets": _clean(raw_ticker_info.get("returnOnAssets")),
                "debt_to_equity": _clean(raw_ticker_info.get("debtToEquity")),
                "current_ratio": _clean(raw_ticker_info.get("currentRatio")),
                "quick_ratio": _clean(raw_ticker_info.get("quickRatio")),
            }

            response = {
                "symbol": symbol,
                "company_overview": company_overview.dict() if company_overview else {},
                "price_metrics": price_metrics,
                "financial_metrics": financial_metrics,
                "valuation_metrics": {
                    "market_cap": raw_ticker_info.get("marketCap"),
                    "enterprise_value": raw_ticker_info.get("enterpriseValue"),
                    "shares_outstanding": raw_ticker_info.get("sharesOutstanding"),
                    "float_shares": raw_ticker_info.get("floatShares"),
                    "book_value": raw_ticker_info.get("bookValue"),
                },
                **self.default_response_fields,
                "request_id": request_id,
            }

            logger.debug(f"[{request_id}] Fundamentals response built for {symbol}")
            return response

        except Exception as e:
            logger.error(
                f"[{request_id}] Error building fundamentals response for {symbol}: {e}"
            )
            return self._build_error_response(
                symbol, "fundamentals_data_error", request_id
            )

    def build_news_response(
        self,
        symbol: str,
        news_items: list[NewsItem],
        sentiment_summary: dict[str, Any] = None,
        request_id: str = None,
    ) -> dict[str, Any]:
        """Build news data response."""
        if not request_id:
            request_id = f"news-resp-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            # Convert NewsItem objects to dicts
            news_data = []
            for item in news_items:
                news_data.append(
                    {
                        "title": item.title,
                        "summary": item.summary,
                        "url": str(item.link) if item.link else None,
                        "published_date": item.published_at.isoformat()
                        if item.published_at
                        else None,
                        "source": item.publisher,
                        "sentiment": getattr(
                            item, "overall_sentiment_label", "neutral"
                        ),
                    }
                )

            # Calculate sentiment if not provided
            if not sentiment_summary:
                pos = sum(
                    1
                    for item in news_items
                    if getattr(item, "overall_sentiment_label", "") == "positive"
                )
                neg = sum(
                    1
                    for item in news_items
                    if getattr(item, "overall_sentiment_label", "") == "negative"
                )
                neu = len(news_items) - pos - neg

                overall = (
                    "positive"
                    if pos > max(neg, neu)
                    else "negative"
                    if neg > max(pos, neu)
                    else "neutral"
                )
                sentiment_summary = {
                    "overall": overall,
                    "positive": pos,
                    "negative": neg,
                    "neutral": neu,
                    "total_articles": len(news_items),
                }

            response = {
                "symbol": symbol,
                "news": news_data,
                "sentiment_summary": sentiment_summary,
                "news_count": len(news_items),
                **self.default_response_fields,
                "request_id": request_id,
            }

            logger.debug(
                f"[{request_id}] News response built for {symbol} with {len(news_items)} items"
            )
            return response

        except Exception as e:
            logger.error(
                f"[{request_id}] Error building news response for {symbol}: {e}"
            )
            return self._build_error_response(symbol, "news_data_error", request_id)

    def _build_error_response(
        self, symbol: str, error_type: str, request_id: str = None
    ) -> dict[str, Any]:
        """Build standardized error response."""
        return {
            "symbol": symbol,
            "status": "error",
            "error_type": error_type,
            "message": f"Error processing {error_type} for {symbol}",
            "timestamp": datetime.utcnow().isoformat(),
            "request_id": request_id or f"error-{uuid.uuid4().hex[:6]}",
        }

"""
Stock Data Processor

Extracted from stock_data_service.py (3662 LOC) to follow 160 LOC rule.
Handles data processing, transformation, and validation for stock data.

Responsibilities:
- Raw data validation and cleaning
- Data format standardization
- Price calculations and metrics
- Technical indicator processing
- Data quality checks
"""

import pandas as pd
from typing import Any
from datetime import datetime
import uuid

from backend.models.stock import CompanyOverview, NewsItem, LatestOHLCV
from backend.utils.logger_config import get_logger
from backend.core.helpers import parse_optional_int

logger = get_logger("aevorex_finbot.StockDataProcessor")


class StockDataProcessor:
    """Service for processing and transforming stock data."""

    def __init__(self):
        self.default_na_value = "N/A"

    def process_company_info(
        self, ticker_info: dict[str, Any], symbol: str, request_id: str = None
    ) -> CompanyOverview | None:
        """Process raw company information into CompanyOverview model."""
        if not request_id:
            request_id = f"process-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            company_overview = CompanyOverview(
                symbol=symbol,
                company_name=ticker_info.get("longName")
                or ticker_info.get("shortName", symbol),
                sector=ticker_info.get("sector", self.default_na_value),
                industry=ticker_info.get("industry", self.default_na_value),
                market_cap=parse_optional_int(ticker_info.get("marketCap")),
                employees=parse_optional_int(ticker_info.get("fullTimeEmployees")),
                description=ticker_info.get("longBusinessSummary", ""),
                website=ticker_info.get("website", ""),
                headquarters=f"{ticker_info.get('city', '')}, {ticker_info.get('country', '')}".strip(
                    ", "
                ),
                founded_year=ticker_info.get("foundedYear"),
                exchange=ticker_info.get("exchange", ""),
                currency=ticker_info.get("currency", "USD"),
                country=ticker_info.get("country", ""),
                ceo=ticker_info.get("companyOfficers", [{}])[0].get("name", "")
                if ticker_info.get("companyOfficers")
                else "",
            )
            logger.debug(f"[{request_id}] Company info processed for {symbol}")
            return company_overview
        except Exception as e:
            logger.error(
                f"[{request_id}] Error processing company info for {symbol}: {e}"
            )
            return None

    def calculate_price_metrics(
        self, ticker_info: dict[str, Any], request_id: str = None
    ) -> dict[str, Any]:
        """Calculate price-related metrics from ticker information."""
        try:
            current_price = ticker_info.get("currentPrice") or ticker_info.get(
                "regularMarketPrice"
            )
            previous_close = ticker_info.get("previousClose") or ticker_info.get(
                "regularMarketPreviousClose"
            )

            change = None
            change_percent = None
            if current_price and previous_close:
                change = current_price - previous_close
                change_percent = (change / previous_close) * 100

            return {
                "current_price": current_price,
                "previous_close": previous_close,
                "change": change,
                "change_percent": change_percent,
                "day_high": ticker_info.get("dayHigh")
                or ticker_info.get("regularMarketDayHigh"),
                "day_low": ticker_info.get("dayLow")
                or ticker_info.get("regularMarketDayLow"),
                "volume": ticker_info.get("volume")
                or ticker_info.get("regularMarketVolume"),
            }

        except Exception as e:
            logger.error(f"[{request_id}] Error calculating price metrics: {e}")
            return {}

    def process_ohlcv_dataframe(
        self, ohlcv_df: pd.DataFrame, symbol: str, request_id: str = None
    ) -> LatestOHLCV | None:
        """Process OHLCV DataFrame and extract latest point."""
        if not request_id:
            request_id = f"ohlcv-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            if ohlcv_df is None or ohlcv_df.empty:
                return None

            # Ensure DataFrame is sorted by index (should be datetime)
            ohlcv_df_sorted = ohlcv_df.sort_index()
            last_row = ohlcv_df_sorted.iloc[-1]

            latest_ohlcv = LatestOHLCV(
                t=int(last_row.name.timestamp())
                if hasattr(last_row.name, "timestamp")
                else int(datetime.now().timestamp()),
                o=float(last_row.get("open", 0)),
                h=float(last_row.get("high", 0)),
                l=float(last_row.get("low", 0)),
                c=float(last_row.get("close", 0)),
                v=int(last_row.get("volume", 0)),
            )

            logger.debug(f"[{request_id}] OHLCV processed for {symbol}")
            return latest_ohlcv

        except Exception as e:
            logger.error(f"[{request_id}] Error processing OHLCV for {symbol}: {e}")
            return None

    def process_news_items(
        self,
        news_items: list[Any],
        symbol: str,
        limit: int = 10,
        request_id: str = None,
    ) -> list[NewsItem]:
        """Process raw news items into NewsItem models."""
        if not request_id:
            request_id = f"news-{symbol}-{uuid.uuid4().hex[:6]}"

        processed_news = []

        try:
            for item in news_items[:limit]:
                if hasattr(item, "title"):  # Already a NewsItem
                    processed_news.append(item)
                else:  # Raw dict that needs processing
                    news_item = NewsItem(
                        title=item.get("title", ""),
                        summary=item.get("summary") or item.get("content", ""),
                        link=item.get("url") or item.get("link"),
                        published_at=item.get("published_date"),
                        publisher=item.get("source", ""),
                        overall_sentiment_label=item.get("sentiment", "neutral"),
                    )
                    processed_news.append(news_item)

            logger.debug(
                f"[{request_id}] Processed {len(processed_news)} news items for {symbol}"
            )
            return processed_news

        except Exception as e:
            logger.error(f"[{request_id}] Error processing news for {symbol}: {e}")
            return []

    def validate_and_clean_data(
        self,
        data: dict[str, Any],
        required_fields: list[str] = None,
        request_id: str = None,
    ) -> dict[str, Any]:
        """Validate and clean processed data."""
        if required_fields is None:
            required_fields = []

        try:
            cleaned_data = {}

            for key, value in data.items():
                # Clean None values and replace with appropriate defaults
                if value is None:
                    if key in [
                        "current_price",
                        "previous_close",
                        "change",
                        "change_percent",
                    ]:
                        cleaned_data[key] = 0.0
                    elif key in ["volume", "market_cap"]:
                        cleaned_data[key] = 0
                    else:
                        cleaned_data[key] = self.default_na_value
                else:
                    cleaned_data[key] = value

            # Check required fields
            missing_fields = [
                field for field in required_fields if field not in cleaned_data
            ]
            if missing_fields:
                logger.warning(
                    f"[{request_id}] Missing required fields: {missing_fields}"
                )

            return cleaned_data

        except Exception as e:
            logger.error(f"[{request_id}] Error validating data: {e}")
            return data

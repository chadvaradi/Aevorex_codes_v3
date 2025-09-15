"""
Data Processor Service - Raw Data Processing

Extracted from stock_service.py (3,774 LOC) to follow 160 LOC rule.
Handles processing and transformation of raw fetched data.

Responsibilities:
- Raw data validation and cleaning
- Data format standardization
- Type conversion and validation
- Data quality checks
"""

import pandas as pd
from typing import Any
from datetime import datetime

from backend.models.stock import CompanyOverview, NewsItem, LatestOHLCV
from backend.utils.logger_config import get_logger
from backend.core.helpers import parse_optional_float, parse_optional_int

logger = get_logger("aevorex_finbot.DataProcessor")


class DataProcessor:
    """Service for processing and transforming raw fetched data."""

    def __init__(self):
        self.default_na_value = "N/A"

    def process_company_info(
        self, raw_data: dict[str, Any] | None, symbol: str, request_id: str
    ) -> CompanyOverview | None:
        """Process raw company information into CompanyOverview model."""
        if not raw_data:
            logger.debug(f"[{request_id}] No company info to process for {symbol}")
            return None

        try:
            # Extract and clean company info fields
            processed_data = {
                "symbol": symbol,
                "company_name": raw_data.get("longName")
                or raw_data.get("shortName")
                or symbol,
                "sector": raw_data.get("sector", self.default_na_value),
                "industry": raw_data.get("industry", self.default_na_value),
                "description": raw_data.get(
                    "longBusinessSummary", self.default_na_value
                ),
                "employees": parse_optional_int(raw_data.get("fullTimeEmployees")),
                "market_cap": parse_optional_float(raw_data.get("marketCap")),
                "website": raw_data.get("website"),
                "country": raw_data.get("country", self.default_na_value),
                "currency": raw_data.get("currency", "USD"),
                "exchange": raw_data.get("exchange", self.default_na_value),
            }

            # Validate required fields
            if not processed_data["company_name"]:
                processed_data["company_name"] = symbol

            return CompanyOverview(**processed_data)

        except Exception as e:
            logger.error(
                f"[{request_id}] Failed to process company info for {symbol}: {e}"
            )
            return None

    def process_ohlcv_data(
        self, raw_data: list[dict[str, Any]] | None, symbol: str, request_id: str
    ) -> pd.DataFrame | None:
        """Process raw OHLCV data into standardized DataFrame."""
        if not raw_data:
            logger.debug(f"[{request_id}] No OHLCV data to process for {symbol}")
            return None

        try:
            # Convert to DataFrame
            df = pd.DataFrame(raw_data)

            # Validate required columns
            required_cols = ["date", "open", "high", "low", "close", "volume"]
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                logger.error(
                    f"[{request_id}] Missing OHLCV columns for {symbol}: {missing_cols}"
                )
                return None

            # Clean and convert data types
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

            # Convert numeric columns
            numeric_cols = ["open", "high", "low", "close", "volume"]
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # Remove rows with invalid data
            df = df.dropna()

            if df.empty:
                logger.warning(
                    f"[{request_id}] No valid OHLCV data after cleaning for {symbol}"
                )
                return None

            # Sort by date
            df = df.sort_index()

            logger.debug(
                f"[{request_id}] Processed {len(df)} OHLCV records for {symbol}"
            )
            return df

        except Exception as e:
            logger.error(
                f"[{request_id}] Failed to process OHLCV data for {symbol}: {e}"
            )
            return None

    def process_news_data(
        self, raw_data: list[dict[str, Any]] | None, symbol: str, request_id: str
    ) -> list[NewsItem]:
        """Process raw news data into NewsItem models."""
        if not raw_data:
            logger.debug(f"[{request_id}] No news data to process for {symbol}")
            return []

        processed_news = []

        for item in raw_data:
            try:
                # Extract and clean news item fields
                processed_item = {
                    "title": item.get("title", "").strip(),
                    "summary": item.get("summary")
                    or item.get("description", "").strip(),
                    "link": item.get("link") or item.get("url"),
                    "published_at": self._parse_news_date(item.get("published_at")),
                    "publisher": item.get("publisher") or item.get("source", "Unknown"),
                    "image_url": item.get("image_url"),
                    "overall_sentiment_label": item.get("sentiment", "neutral"),
                }

                # Validate required fields
                if not processed_item["title"]:
                    continue

                # Create NewsItem model
                news_item = NewsItem(**processed_item)
                processed_news.append(news_item)

            except Exception as e:
                logger.debug(
                    f"[{request_id}] Failed to process news item for {symbol}: {e}"
                )
                continue

        logger.debug(
            f"[{request_id}] Processed {len(processed_news)} news items for {symbol}"
        )
        return processed_news

    def extract_latest_ohlcv(
        self, ohlcv_df: pd.DataFrame | None, symbol: str, request_id: str
    ) -> LatestOHLCV | None:
        """Extract latest OHLCV data from DataFrame."""
        if ohlcv_df is None or ohlcv_df.empty:
            logger.debug(f"[{request_id}] No OHLCV data to extract latest for {symbol}")
            return None

        try:
            latest_row = ohlcv_df.iloc[-1]

            return LatestOHLCV(
                symbol=symbol,
                date=latest_row.name.isoformat()
                if hasattr(latest_row.name, "isoformat")
                else str(latest_row.name),
                open=float(latest_row["open"]),
                high=float(latest_row["high"]),
                low=float(latest_row["low"]),
                close=float(latest_row["close"]),
                volume=int(latest_row["volume"]),
            )

        except Exception as e:
            logger.error(
                f"[{request_id}] Failed to extract latest OHLCV for {symbol}: {e}"
            )
            return None

    def _parse_news_date(self, date_str: str | None) -> datetime | None:
        """Parse news publication date from various formats."""
        if not date_str:
            return None

        try:
            # Try ISO format first
            if "T" in date_str:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))

            # Try other common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d/%m/%Y",
                "%m/%d/%Y",
            ]

            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue

            logger.debug(f"Could not parse date: {date_str}")
            return None

        except Exception:
            return None

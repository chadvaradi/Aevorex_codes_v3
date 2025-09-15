"""
Fundamentals Service - Company and Financial Data Processing

Extracted from stock_service.py (3,774 LOC) to follow 160 LOC rule.
Handles company fundamentals and financial data processing.

Responsibilities:
- Company information processing
- Financial metrics extraction
- Basic stock data retrieval
- Data validation and mapping
"""

import uuid
from typing import Any
from datetime import datetime
import httpx

from backend.utils.cache_service import CacheService
from backend.core.fetchers.yfinance.yfinance_fetcher import YFinanceFetcher
from backend.utils.logger_config import get_logger
from backend.core.services.stock.fundamentals_processors import FundamentalsProcessor

logger = get_logger("aevorex_finbot.FundamentalsService")


class FundamentalsService:
    """Service for handling company fundamentals and financial data."""

    def __init__(self):
        self.processor = FundamentalsProcessor()

    async def get_fundamentals_data(
        self, symbol: str, client: httpx.AsyncClient, cache: CacheService
    ) -> dict[str, Any] | None:
        """Get comprehensive fundamentals data for a stock symbol."""
        request_id = f"fundamentals-{symbol}-{uuid.uuid4().hex[:6]}"
        logger.info(f"[{request_id}] Fetching fundamentals for {symbol}")

        try:
            # Fetch company information from YFinance
            fetcher = YFinanceFetcher(cache)
            ticker_info = await fetcher.fetch_fundamentals(symbol)

            if not ticker_info:
                logger.warning(f"[{request_id}] No ticker info available for {symbol}")
                return None

            # Process using the processor
            company_overview = self.processor.process_company_info(ticker_info, symbol)
            financials_data = self.processor.process_financials_data(ticker_info)
            metrics = self.processor.extract_market_metrics(ticker_info)

            fundamentals_response = {
                "symbol": symbol,
                "company_overview": company_overview,
                "financials": financials_data,
                "metrics": metrics,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
            }

            logger.info(f"[{request_id}] Fundamentals data retrieved successfully")
            return fundamentals_response

        except Exception as e:
            logger.error(f"[{request_id}] Error getting fundamentals: {e}")
            return None

    async def get_basic_stock_data(
        self, symbol: str, client: httpx.AsyncClient, cache: CacheService
    ) -> dict[str, Any] | None:
        """Get basic stock data for ticker-tape and simple displays."""
        request_id = f"basic-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            # Fetch basic company info
            fetcher = YFinanceFetcher(cache)
            ticker_info = await fetcher.fetch_fundamentals(symbol)

            if not ticker_info:
                return None

            # Process using the processor
            price_metrics = self.processor.calculate_price_metrics(ticker_info)
            basic_summary = self.processor.format_basic_summary(ticker_info, symbol)

            basic_data = {
                **basic_summary,
                **price_metrics,
                "exchange": ticker_info.get("exchange"),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
            }

            return basic_data

        except Exception as e:
            logger.error(f"[{request_id}] Error getting basic stock data: {e}")
            return None

    async def get_company_overview(
        self, symbol: str, client: httpx.AsyncClient, cache: CacheService
    ) -> dict[str, Any] | None:
        """Get company overview data only."""
        request_id = f"overview-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            fetcher = YFinanceFetcher(cache)
            ticker_info = await fetcher.fetch_fundamentals(symbol)
            if not ticker_info:
                return None

            return self.processor.process_company_info(ticker_info, symbol)

        except Exception as e:
            logger.error(f"[{request_id}] Error getting company overview: {e}")
            return None

    async def get_financial_metrics(
        self, symbol: str, client: httpx.AsyncClient, cache: CacheService
    ) -> dict[str, Any] | None:
        """Get financial metrics only."""
        request_id = f"metrics-{symbol}-{uuid.uuid4().hex[:6]}"

        try:
            fetcher = YFinanceFetcher(cache)
            ticker_info = await fetcher.fetch_fundamentals(symbol)
            if not ticker_info:
                return None

            financials = self.processor.process_financials_data(ticker_info)
            market_metrics = self.processor.extract_market_metrics(ticker_info)

            return {
                "financials": financials,
                "market_metrics": market_metrics,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"[{request_id}] Error getting financial metrics: {e}")
            return None

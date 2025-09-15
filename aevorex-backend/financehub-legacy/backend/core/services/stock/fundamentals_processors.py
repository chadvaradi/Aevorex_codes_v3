"""
Fundamentals Processors - Data processing utilities for financial data.
Split from fundamentals_service.py to maintain 160 LOC limit.
"""

from typing import Any
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.FundamentalsProcessors")


class FundamentalsProcessor:
    """Handles processing of financial and company data."""

    def process_company_info(
        self, ticker_info: dict[str, Any], symbol: str
    ) -> dict[str, Any]:
        """Process raw ticker info into structured company overview."""
        return {
            "symbol": symbol,
            "name": ticker_info.get("longName")
            or ticker_info.get("shortName")
            or symbol,
            "exchange": ticker_info.get("exchange")
            or ticker_info.get("fullExchangeName"),
            "sector": ticker_info.get("sector"),
            "industry": ticker_info.get("industry"),
            "country": ticker_info.get("country"),
            "currency": ticker_info.get("currency"),
            "market_cap": ticker_info.get("marketCap"),
            "description": ticker_info.get("longBusinessSummary"),
            "website": ticker_info.get("website"),
            "employees": ticker_info.get("fullTimeEmployees"),
            "headquarters": ticker_info.get("city") or ticker_info.get("address1"),
        }

    def process_financials_data(self, ticker_info: dict[str, Any]) -> dict[str, Any]:
        """Process financial metrics from ticker info."""
        return {
            "market_cap": ticker_info.get("marketCap"),
            "revenue": ticker_info.get("totalRevenue"),
            "profit_margin": ticker_info.get("profitMargins"),
            "operating_margin": ticker_info.get("operatingMargins"),
            "return_on_equity": ticker_info.get("returnOnEquity"),
            "return_on_assets": ticker_info.get("returnOnAssets"),
            "debt_to_equity": ticker_info.get("debtToEquity"),
            "current_ratio": ticker_info.get("currentRatio"),
            "quick_ratio": ticker_info.get("quickRatio"),
            "gross_margin": ticker_info.get("grossMargins"),
        }

    def extract_market_metrics(self, ticker_info: dict[str, Any]) -> dict[str, Any]:
        """Extract market valuation metrics."""
        return {
            "pe_ratio": ticker_info.get("trailingPE"),
            "forward_pe": ticker_info.get("forwardPE"),
            "pb_ratio": ticker_info.get("priceToBook"),
            "ps_ratio": ticker_info.get("priceToSalesTrailing12Months"),
            "peg_ratio": ticker_info.get("pegRatio"),
            "beta": ticker_info.get("beta"),
            "dividend_yield": ticker_info.get("dividendYield"),
            "payout_ratio": ticker_info.get("payoutRatio"),
        }

    def calculate_price_metrics(self, ticker_info: dict[str, Any]) -> dict[str, Any]:
        """Calculate derived price metrics."""
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
            "currency": ticker_info.get("currency", "USD"),
            "volume": ticker_info.get("volume")
            or ticker_info.get("regularMarketVolume"),
        }

    def validate_fundamentals_data(self, data: dict[str, Any]) -> bool:
        """Validate fundamentals data structure."""
        required_fields = ["symbol", "company_overview", "financials", "metrics"]
        return all(field in data for field in required_fields)

    def format_basic_summary(
        self, ticker_info: dict[str, Any], symbol: str
    ) -> dict[str, Any]:
        """Format basic company summary for display."""
        return {
            "symbol": symbol,
            "name": ticker_info.get("longName") or ticker_info.get("shortName"),
            "sector": ticker_info.get("sector"),
            "industry": ticker_info.get("industry"),
            "market_cap": ticker_info.get("marketCap"),
            "pe_ratio": ticker_info.get("trailingPE"),
            "dividend_yield": ticker_info.get("dividendYield"),
        }

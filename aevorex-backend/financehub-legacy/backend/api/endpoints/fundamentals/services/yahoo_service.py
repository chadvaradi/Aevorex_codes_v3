"""
Yahoo Finance Service

Provides data fetching capabilities from Yahoo Finance for fundamental analysis.
Handles company overview, financial statements, ratios, and earnings data.
"""

from typing import Dict, Any, Optional
import asyncio
import time
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class YahooService:
    """Service for fetching fundamental data from Yahoo Finance using yfinance."""
    
    def __init__(self):
        self.provider = "yahoo_finance"
    
    async def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch company overview data from Yahoo Finance."""
        start_time = time.time()
        logger.info(f"Fetching company overview for {symbol}")
        
        try:
            import yfinance as yf
            
            # Run yfinance in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, getattr, ticker, 'info')
            
            if not info or 'symbol' not in info:
                logger.warning(f"No overview data found for {symbol}")
                return None
            
            overview_data = {
                "longName": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "country": info.get("country"),
                "exchange": info.get("exchange"),
                "marketCap": info.get("marketCap"),
                "fullTimeEmployees": info.get("fullTimeEmployees"),
                "website": info.get("website"),
                "businessSummary": info.get("longBusinessSummary"),
                "city": info.get("city"),
                "state": info.get("state"),
                "zip": info.get("zip"),
                "phone": info.get("phone"),
            }
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Successfully fetched overview for {symbol} in {processing_time:.2f}ms")
            
            return {
                "metadata": {
                    "symbol": symbol,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "provider": self.provider,
                    "processing_time_ms": round(processing_time, 2)
                },
                "data": overview_data
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch overview for {symbol}: {e}")
            return None
    
    async def get_financial_statements(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch financial statements from Yahoo Finance."""
        start_time = time.time()
        logger.info(f"Fetching financial statements for {symbol}")
        
        try:
            import yfinance as yf
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            
            # Get financial statements
            financials = await loop.run_in_executor(None, getattr, ticker, 'financials')
            balance_sheet = await loop.run_in_executor(None, getattr, ticker, 'balance_sheet')
            cashflow = await loop.run_in_executor(None, getattr, ticker, 'cashflow')
            
            # Get latest annual data (most recent year)
            latest_financials = financials.iloc[0].to_dict() if not financials.empty else {}
            latest_balance = balance_sheet.iloc[0].to_dict() if not balance_sheet.empty else {}
            latest_cashflow = cashflow.iloc[0].to_dict() if not cashflow.empty else {}
            
            financial_data = {
                # Income Statement
                "revenue": latest_financials.get("Total Revenue"),
                "gross_profit": latest_financials.get("Gross Profit"),
                "operating_income": latest_financials.get("Operating Income"),
                "net_income": latest_financials.get("Net Income"),
                
                # Balance Sheet
                "total_assets": latest_balance.get("Total Assets"),
                "total_liabilities": latest_balance.get("Total Liab"),
                "shareholder_equity": latest_balance.get("Stockholders Equity"),
                "cash_and_equivalents": latest_balance.get("Cash And Cash Equivalents"),
                "total_debt": latest_balance.get("Total Debt"),
                
                # Cash Flow
                "operating_cash_flow": latest_cashflow.get("Total Cash From Operating Activities"),
                "capital_expenditure": latest_cashflow.get("Capital Expenditures"),
                "free_cash_flow": latest_cashflow.get("Free Cash Flow"),
                "dividends_paid": latest_cashflow.get("Dividends Paid"),
            }
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Successfully fetched financials for {symbol} in {processing_time:.2f}ms")
            
            return {
                "metadata": {
                    "symbol": symbol,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "provider": self.provider,
                    "processing_time_ms": round(processing_time, 2)
                },
                "data": financial_data
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch financials for {symbol}: {e}")
            return None
    
    async def get_financial_ratios(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch financial ratios from Yahoo Finance."""
        start_time = time.time()
        logger.info(f"Fetching financial ratios for {symbol}")
        
        try:
            import yfinance as yf
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, getattr, ticker, 'info')
            
            if not info:
                logger.warning(f"No ratio data found for {symbol}")
                return None
            
            ratios_data = {
                # Valuation Ratios
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "enterprise_to_revenue": info.get("enterpriseToRevenue"),
                "enterprise_to_ebitda": info.get("enterpriseToEbitda"),
                
                # Profitability Ratios
                "profit_margins": info.get("profitMargins"),
                "operating_margins": info.get("operatingMargins"),
                "gross_margins": info.get("grossMargins"),
                "return_on_assets": info.get("returnOnAssets"),
                "return_on_equity": info.get("returnOnEquity"),
                
                # Debt Ratios
                "debt_to_equity": info.get("debtToEquity"),
                "total_cash_per_share": info.get("totalCashPerShare"),
                "total_debt": info.get("totalDebt"),
                
                # Liquidity Ratios
                "current_ratio": info.get("currentRatio"),
                "quick_ratio": info.get("quickRatio"),
                
                # Other Metrics
                "beta": info.get("beta"),
                "dividend_yield": info.get("dividendYield"),
                "payout_ratio": info.get("payoutRatio"),
                "earnings_growth": info.get("earningsGrowth"),
                "revenue_growth": info.get("revenueGrowth"),
            }
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Successfully fetched ratios for {symbol} in {processing_time:.2f}ms")
            
            return {
                "metadata": {
                    "symbol": symbol,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "provider": self.provider,
                    "processing_time_ms": round(processing_time, 2)
                },
                "data": ratios_data
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch ratios for {symbol}: {e}")
            return None
    
    async def get_earnings_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Fetch earnings data from Yahoo Finance."""
        start_time = time.time()
        logger.info(f"Fetching earnings data for {symbol}")
        
        try:
            import yfinance as yf
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, getattr, ticker, 'info')
            
            if not info:
                logger.warning(f"No earnings data found for {symbol}")
                return None
            
            earnings_data = {
                "trailing_eps": info.get("trailingEps"),
                "forward_eps": info.get("forwardEps"),
                "earnings_quarterly_growth": info.get("earningsQuarterlyGrowth"),
                "earnings_growth": info.get("earningsGrowth"),
                "revenue_growth": info.get("revenueGrowth"),
                "target_high_price": info.get("targetHighPrice"),
                "target_low_price": info.get("targetLowPrice"),
                "target_mean_price": info.get("targetMeanPrice"),
                "recommendation_mean": info.get("recommendationMean"),
                "number_of_analyst_opinions": info.get("numberOfAnalystOpinions"),
            }
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Successfully fetched earnings for {symbol} in {processing_time:.2f}ms")
            
            return {
                "metadata": {
                    "symbol": symbol,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "provider": self.provider,
                    "processing_time_ms": round(processing_time, 2)
                },
                "data": earnings_data
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch earnings for {symbol}: {e}")
            return None
    
    async def get_baseline_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get minimum baseline data for quick equity search view."""
        start_time = time.time()
        logger.info(f"Fetching baseline data for {symbol}")
        
        try:
            import yfinance as yf
            
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, getattr, ticker, 'info')
            
            if not info:
                logger.warning(f"No baseline data found for {symbol}")
                return None
            
            baseline_data = {
                "long_name": info.get("longName"),
                "sector": info.get("sector"),
                "exchange": info.get("exchange"),
                "market_cap": info.get("marketCap"),
                "trailing_pe": info.get("trailingPE"),
                "forward_pe": info.get("forwardPE"),
                "peg_ratio": info.get("pegRatio"),
                "price_to_book": info.get("priceToBook"),
                "return_on_equity": info.get("returnOnEquity"),
                "return_on_assets": info.get("returnOnAssets"),
                "debt_to_equity": info.get("debtToEquity"),
                "current_ratio": info.get("currentRatio"),
                "net_income": info.get("netIncomeToCommon"),
                "free_cash_flow": info.get("freeCashflow"),
            }
            
            processing_time = (time.time() - start_time) * 1000
            logger.info(f"Successfully fetched baseline for {symbol} in {processing_time:.2f}ms")
            
            return {
                "metadata": {
                    "symbol": symbol,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "provider": self.provider,
                    "processing_time_ms": round(processing_time, 2)
                },
                "data": baseline_data
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch baseline for {symbol}: {e}")
            return None


__all__ = ["YahooService"]

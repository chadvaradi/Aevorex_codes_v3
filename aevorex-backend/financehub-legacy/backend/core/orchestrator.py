"""
Aevorex FinBot - Stock Data Orchestrator v1

Centralized orchestration layer for stock data fetching, processing, and AI analysis.
Replaces the monolithic stock_data_service.py with a clean, step-based pipeline.
"""

import asyncio
import time
import uuid
from typing import Any
from datetime import datetime

import httpx

from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.core.fetchers import get_fetcher
from backend.core.ai.unified_service import UnifiedAIService
from backend.core.services.stock.fetcher import StockDataFetcher
from backend.core.services.stock.processor import StockDataProcessor
from backend.core.services.shared.response_builder import (
    build_stock_response_from_parallel_data,
)
from backend.models.stock import FinBotStockResponse
from backend.core.services.stock.response import StockResponseBuilder

logger = get_logger("aevorex_finbot.core.orchestrator")


class StockOrchestrator:
    """
    Orchestrates the complete stock data pipeline:
    1. Cache check
    2. Parallel data fetching (fundamentals, OHLCV, news)
    3. Data mapping and validation
    4. AI analysis (if requested)
    5. Response building
    """

    def __init__(self, cache: CacheService, ai_service: UnifiedAIService = None):
        self.cache = cache
        self.ai_service = ai_service
        self._http_client: httpx.AsyncClient | None = None

        # Legacy compatibility - initialize services if not provided
        if ai_service is None:
            self.ai_service = UnifiedAIService()

        # Initialize legacy services for compatibility
        self.fetcher = StockDataFetcher(cache=cache)
        self.processor = StockDataProcessor()
        self.response_builder = StockResponseBuilder()

    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client for API calls."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client

    async def run(
        self,
        ticker: str,
        *,
        force_refresh: bool = False,
        include_ai: bool = True,
        request_id: str = None,
    ) -> dict[str, Any]:
        """
        Main orchestration method.

        Args:
            ticker: Stock symbol to fetch data for
            force_refresh: Skip cache and force fresh data fetch
            include_ai: Whether to include AI analysis
            request_id: Unique request identifier for logging

        Returns:
            Complete stock data response
        """
        if not request_id:
            request_id = (
                f"orchestrator_{ticker}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

        logger.info(f"[{request_id}] Starting orchestration for {ticker}")

        try:
            # Step 1: Cache check
            if not force_refresh:
                cached_data = await self._check_cache(ticker, request_id)
                if cached_data:
                    logger.info(f"[{request_id}] Returning cached data for {ticker}")
                    return cached_data

            # Step 2: Parallel data fetching
            client = await self._get_http_client()

            logger.info(f"[{request_id}] Starting parallel data fetch for {ticker}")

            # Run fetchers in parallel
            tasks = [
                self._fetch_fundamentals(ticker, client, request_id),
                self._fetch_ohlcv(ticker, client, request_id),
                self._fetch_news(ticker, client, request_id) if include_ai else None,
            ]

            # Filter out None tasks
            tasks = [task for task in tasks if task is not None]

            results = await asyncio.gather(*tasks, return_exceptions=True)

            fundamentals_data = results[0] if len(results) > 0 else None
            ohlcv_data = results[1] if len(results) > 1 else None
            news_data = results[2] if len(results) > 2 else None

            # Step 3: Data validation and building
            response_data = await self._build_response(
                ticker=ticker,
                fundamentals=fundamentals_data,
                ohlcv=ohlcv_data,
                news=news_data,
                request_id=request_id,
            )

            # Step 4: AI analysis (if requested)
            if include_ai and response_data:
                try:
                    ai_summary = await self._generate_ai_summary(
                        response_data, request_id
                    )
                    if ai_summary:
                        response_data["ai_summary"] = ai_summary
                except Exception as ai_error:
                    logger.error(f"[{request_id}] AI analysis failed: {ai_error}")
                    # Continue without AI - don't fail the entire request

            # Step 5: Cache successful response
            if response_data:
                await self._cache_response(ticker, response_data, request_id)

            logger.info(f"[{request_id}] Orchestration completed for {ticker}")
            return response_data or {}

        except Exception as error:
            logger.error(
                f"[{request_id}] Orchestration failed for {ticker}: {error}",
                exc_info=True,
            )
            return {"error": str(error), "ticker": ticker}

        finally:
            # Cleanup
            if self._http_client:
                await self._http_client.aclose()
                self._http_client = None

    async def _check_cache(self, ticker: str, request_id: str) -> dict[str, Any] | None:
        """Check cache for existing data."""
        cache_key = f"stock_data:{ticker}"
        try:
            cached = await self.cache.get(cache_key)
            if cached:
                logger.debug(f"[{request_id}] Cache hit for {ticker}")
                return cached
        except Exception as cache_error:
            logger.warning(f"[{request_id}] Cache check failed: {cache_error}")
        return None

    async def _fetch_fundamentals(
        self, ticker: str, client: httpx.AsyncClient, request_id: str
    ) -> dict[str, Any] | None:
        """Fetch fundamental data."""
        try:
            fetcher = await get_fetcher("yfinance", client, self.cache)
            return await fetcher.fetch_fundamentals(ticker)
        except Exception as error:
            logger.error(f"[{request_id}] Fundamentals fetch failed: {error}")
            return None

    async def _fetch_ohlcv(
        self, ticker: str, client: httpx.AsyncClient, request_id: str
    ) -> dict[str, Any] | None:
        """Fetch OHLCV data."""
        try:
            fetcher = await get_fetcher("yfinance", client, self.cache)
            df = await fetcher.fetch_ohlcv(ticker, period="1y", interval="1d")
            if df is not None and not df.empty:
                return df.to_dict("records")
        except Exception as error:
            logger.error(f"[{request_id}] OHLCV fetch failed: {error}")
        return None

    async def _fetch_news(
        self, ticker: str, client: httpx.AsyncClient, request_id: str
    ) -> dict[str, Any] | None:
        """Fetch news data."""
        try:
            fetcher = await get_fetcher("yfinance", client, self.cache)
            return await fetcher.fetch_news(ticker)
        except Exception as error:
            logger.error(f"[{request_id}] News fetch failed: {error}")
        return None

    async def _build_response(
        self,
        ticker: str,
        fundamentals: dict[str, Any] | None,
        ohlcv: dict[str, Any] | None,
        news: dict[str, Any] | None,
        request_id: str,
    ) -> dict[str, Any]:
        """Build the final response structure."""
        response = {
            "ticker": ticker,
            "timestamp": datetime.now().isoformat(),
            "fundamentals": fundamentals,
            "ohlcv": ohlcv,
            "news": news,
        }

        logger.debug(f"[{request_id}] Built response for {ticker}")
        return response

    async def _generate_ai_summary(
        self, data: dict[str, Any], request_id: str
    ) -> str | None:
        """Generate AI summary of the stock data using UnifiedAIService."""
        try:
            if not self.ai_service:
                logger.warning(
                    f"[{request_id}] AI service not available, skipping summary generation"
                )
                return None

            # Extract key data for AI analysis
            ticker = data.get("ticker", "UNKNOWN")
            fundamentals = data.get("fundamentals", {})
            ohlcv = data.get("ohlcv", {})
            news = data.get("news", {})

            # Build comprehensive prompt for AI analysis
            analysis_prompt = self._build_analysis_prompt(
                ticker, fundamentals, ohlcv, news
            )

            # Call UnifiedAIService for analysis
            try:
                # Try the dedicated stock analysis method first
                if hasattr(self.ai_service, "generate_stock_analysis"):
                    ai_response = await self.ai_service.generate_stock_analysis(
                        symbol=ticker,
                        basic_data=fundamentals,
                        chart_data=ohlcv,
                        fundamentals=fundamentals,  # Keep for backward compatibility
                    )
                    if ai_response and isinstance(ai_response, dict):
                        return ai_response.get("summary", str(ai_response))

                # Fallback to stream_chat if generate_stock_analysis is not available
                logger.info(
                    f"[{request_id}] Using stream_chat fallback for AI analysis"
                )
                ai_summary = ""

                # Get HTTP client for AI service
                http_client = self._get_http_client()
                if not http_client:
                    logger.error(
                        f"[{request_id}] No HTTP client available for AI service"
                    )
                    return None

                async for chunk in self.ai_service.stream_chat(
                    http_client=http_client,
                    ticker=ticker,
                    user_message=analysis_prompt,
                    locale="en",
                    plan="free",
                    query_type="summary",
                ):
                    ai_summary += chunk

                return ai_summary.strip() if ai_summary else None

            except Exception as ai_error:
                logger.error(f"[{request_id}] AI service call failed: {ai_error}")
                # Return error message for debug purposes in development
                return (
                    f"[AI Error] {str(ai_error)}" if logger.level <= 10 else None
                )  # DEBUG level

        except Exception as error:
            logger.error(f"[{request_id}] AI summary generation failed: {error}")
            # Return error message for debug purposes in development
            return (
                f"[AI Error] {str(error)}" if logger.level <= 10 else None
            )  # DEBUG level

    def _build_analysis_prompt(
        self, ticker: str, fundamentals: dict, ohlcv: dict, news: dict
    ) -> str:
        """Build a comprehensive prompt for AI stock analysis."""
        prompt_parts = [
            f"Analyze the following stock data for {ticker}:",
            "",
            "FUNDAMENTALS:",
            f"- Company: {fundamentals.get('company_name', 'N/A')}",
            f"- Sector: {fundamentals.get('sector', 'N/A')}",
            f"- Market Cap: {fundamentals.get('market_cap', 'N/A')}",
            f"- Current Price: {fundamentals.get('current_price', 'N/A')}",
            f"- PE Ratio: {fundamentals.get('pe_ratio', 'N/A')}",
            "",
            "TECHNICAL DATA:",
            f"- OHLCV Data Points: {len(ohlcv) if isinstance(ohlcv, list) else 'N/A'}",
            f"- Latest Close: {ohlcv[-1].get('close') if isinstance(ohlcv, list) and ohlcv else 'N/A'}",
            "",
            "NEWS:",
            f"- News Items: {len(news) if isinstance(news, list) else 'N/A'}",
        ]

        if isinstance(news, list) and news:
            prompt_parts.append("Recent headlines:")
            for item in news[:3]:  # Limit to 3 recent items
                if isinstance(item, dict):
                    title = item.get("title", "N/A")
                    prompt_parts.append(f"- {title}")

        prompt_parts.extend(
            [
                "",
                "Provide a concise, professional analysis covering:",
                "1. Key financial metrics and valuation",
                "2. Technical outlook",
                "3. Recent news impact",
                "4. Overall investment recommendation (Buy/Hold/Sell)",
                "",
                "Keep the analysis under 200 words and focus on actionable insights.",
            ]
        )

        return "\n".join(prompt_parts)

    async def _cache_response(
        self, ticker: str, data: dict[str, Any], request_id: str
    ) -> None:
        """Cache the response data with dynamic TTL based on data type."""
        cache_key = f"stock_data:{ticker}"
        try:
            # Dynamic TTL based on data freshness requirements
            ttl = self._get_cache_ttl(data)
            await self.cache.set(cache_key, data, ttl=ttl)
            logger.debug(f"[{request_id}] Cached response for {ticker} with TTL {ttl}s")
        except Exception as cache_error:
            logger.warning(f"[{request_id}] Cache set failed: {cache_error}")

    def _get_cache_ttl(self, data: dict[str, Any]) -> int:
        """Get appropriate cache TTL based on data type and freshness requirements."""
        # Fundamentals data changes less frequently - cache longer
        if "fundamentals" in data and data.get("fundamentals"):
            return 7200  # 2 hours for fundamentals

        # News data changes frequently - cache shorter
        if "news" in data and data.get("news"):
            return 1800  # 30 minutes for news

        # OHLCV data changes every market session - cache medium
        if "ohlcv" in data and data.get("ohlcv"):
            return 3600  # 1 hour for OHLCV

        # Default TTL for mixed data
        return 3600  # 1 hour default

    # Legacy compatibility methods
    async def get_basic_stock_data(
        self, symbol: str, client: httpx.AsyncClient
    ) -> dict[str, Any] | None:
        """Legacy compatibility: Orchestrate basic stock data retrieval for ticker-tape and simple displays."""
        request_id = f"basic-{symbol}-{uuid.uuid4().hex[:6]}"
        start_time = time.monotonic()

        logger.info(
            f"[{request_id}] Starting basic stock data orchestration for {symbol}"
        )

        try:
            ticker_info = await self.fetcher.fetch_company_info(symbol, request_id)
            if not ticker_info:
                logger.warning(
                    f"[{request_id}] Primary fetcher failed – falling back to direct yfinance lookup for {symbol}."
                )
                try:
                    import yfinance as yf

                    yf_ticker = yf.Ticker(symbol)
                    ticker_info = yf_ticker.info or {}
                except Exception as yf_error:
                    logger.error(f"[{request_id}] yfinance fallback failed: {yf_error}")
                    return None

            price_metrics = self.processor.calculate_price_metrics(
                ticker_info, request_id
            )

            basic_data = {
                "symbol": symbol,
                "company_name": ticker_info.get("longName")
                or ticker_info.get("shortName"),
                **price_metrics,
                "currency": ticker_info.get("currency", "USD"),
                "exchange": ticker_info.get("exchange"),
                "market_cap": ticker_info.get("marketCap"),
                "sector": ticker_info.get("sector"),
                "industry": ticker_info.get("industry"),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
            }

            basic_data = self.processor.validate_and_clean_data(
                basic_data, ["symbol", "current_price"], request_id
            )

            duration = round((time.monotonic() - start_time) * 1000, 2)
            logger.info(
                f"[{request_id}] Basic data orchestration completed in {duration}ms"
            )
            return basic_data

        except Exception as e:
            logger.error(f"[{request_id}] Error in basic stock data orchestration: {e}")
            return None

    async def get_chart_data(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        period: str = "1y",
        interval: str = "1d",
    ) -> dict[str, Any] | None:
        """Legacy compatibility: Orchestrate chart data retrieval and processing."""
        request_id = f"chart-{symbol}-{uuid.uuid4().hex[:6]}"
        start_time = time.monotonic()

        logger.info(f"[{request_id}] Starting chart data orchestration for {symbol}")

        try:
            # Fetch OHLCV data
            ohlcv_df = await self.fetcher.fetch_ohlcv_data(
                symbol, client, period, interval, request_id
            )

            if ohlcv_df is None or ohlcv_df.empty:
                logger.warning(f"[{request_id}] No chart data available for {symbol}")
                return None

            # Process OHLCV data
            latest_ohlcv = self.processor.process_ohlcv_dataframe(
                ohlcv_df, symbol, request_id
            )

            # Build chart response
            chart_data = self.response_builder.build_chart_response(
                symbol, ohlcv_df, latest_ohlcv, request_id
            )

            duration = round((time.monotonic() - start_time) * 1000, 2)
            logger.info(
                f"[{request_id}] Chart data orchestration completed in {duration}ms"
            )

            return chart_data

        except Exception as e:
            logger.error(f"[{request_id}] Error in chart data orchestration: {e}")
            return None

    async def get_fundamentals_data(
        self, symbol: str, client: httpx.AsyncClient
    ) -> dict[str, Any] | None:
        """Legacy compatibility: Orchestrate fundamentals data retrieval and processing."""
        request_id = f"fundamentals-{symbol}-{uuid.uuid4().hex[:6]}"
        start_time = time.monotonic()

        logger.info(
            f"[{request_id}] Starting fundamentals data orchestration for {symbol}"
        )

        try:
            # Fetch company information
            ticker_info = await self.fetcher.fetch_company_info(symbol, request_id)

            if not ticker_info:
                logger.warning(
                    f"[{request_id}] No fundamentals data available for {symbol}"
                )
                return None

            # Process company information
            company_overview = self.processor.process_company_info(
                ticker_info, symbol, request_id
            )
            price_metrics = self.processor.calculate_price_metrics(
                ticker_info, request_id
            )

            # Build fundamentals response
            fundamentals_data = self.response_builder.build_fundamentals_response(
                symbol, company_overview, price_metrics, ticker_info, request_id
            )

            duration = round((time.monotonic() - start_time) * 1000, 2)
            logger.info(
                f"[{request_id}] Fundamentals data orchestration completed in {duration}ms"
            )

            return fundamentals_data

        except Exception as e:
            logger.error(
                f"[{request_id}] Error in fundamentals data orchestration: {e}"
            )
            return None

    async def get_stock_data(self, symbol: str) -> FinBotStockResponse:
        """Legacy compatibility: Get complete stock data."""
        return await build_stock_response_from_parallel_data(
            symbol,
            # ... parameters would be passed here
        )

    async def fetch_parallel_data(
        self,
        symbol: str,
        client,
        cache,
        request_id: str,
        force_refresh: bool = False,
        period: str = "1y",
        interval: str = "1d",
    ):
        """Legacy compatibility: Fetch parallel data for technical analysis."""
        try:
            logger.info(f"[{request_id}] Starting parallel data fetch for {symbol}")

            # Fetch OHLCV data
            ohlcv_df = await self.fetcher.fetch_ohlcv_data(
                symbol, client, period, interval, request_id
            )

            if ohlcv_df is None or ohlcv_df.empty:
                logger.warning(f"[{request_id}] No OHLCV data available for {symbol}")
                return None, {}, None, None

            # Calculate technical indicators
            technical_indicators = {}
            try:
                from backend.core.indicator_service.service import (
                    calculate_and_format_indicators,
                )

                indicator_history = calculate_and_format_indicators(ohlcv_df, symbol)
                if indicator_history:
                    # Convert to dict format for compatibility
                    technical_indicators = {
                        "sma": {
                            "short": getattr(indicator_history.sma, "SMA_SHORT", {}),
                            "long": getattr(indicator_history.sma, "SMA_LONG", {}),
                        }
                        if hasattr(indicator_history, "sma")
                        else {},
                        "rsi": getattr(indicator_history.rsi, "RSI", {})
                        if hasattr(indicator_history, "rsi")
                        else {},
                        "macd": {
                            "line": getattr(indicator_history.macd, "MACD_LINE", {}),
                            "signal": getattr(
                                indicator_history.macd, "MACD_SIGNAL", {}
                            ),
                            "histogram": getattr(
                                indicator_history.macd, "MACD_HIST", {}
                            ),
                        }
                        if hasattr(indicator_history, "macd")
                        else {},
                        "bbands": {
                            "upper": getattr(
                                indicator_history.bbands, "BBANDS_UPPER", {}
                            ),
                            "middle": getattr(
                                indicator_history.bbands, "BBANDS_MIDDLE", {}
                            ),
                            "lower": getattr(
                                indicator_history.bbands, "BBANDS_LOWER", {}
                            ),
                        }
                        if hasattr(indicator_history, "bbands")
                        else {},
                    }
                    logger.info(
                        f"[{request_id}] Successfully calculated technical indicators for {symbol}"
                    )
                else:
                    logger.warning(
                        f"[{request_id}] Failed to calculate technical indicators for {symbol}"
                    )

            except Exception as indicator_error:
                logger.error(
                    f"[{request_id}] Error calculating indicators: {indicator_error}"
                )
                technical_indicators = {}

            # Fetch fundamentals data
            fundamentals_data = None
            try:
                ticker_info = await self.fetcher.fetch_company_info(symbol, request_id)
                if ticker_info:
                    company_overview = self.processor.process_company_info(
                        ticker_info, symbol, request_id
                    )
                    price_metrics = self.processor.calculate_price_metrics(
                        ticker_info, request_id
                    )
                    fundamentals_data = {
                        "company_overview": company_overview,
                        "price_metrics": price_metrics,
                        "ticker_info": ticker_info,
                    }
                    logger.info(
                        f"[{request_id}] Successfully fetched fundamentals for {symbol}"
                    )
                else:
                    logger.warning(
                        f"[{request_id}] No fundamentals data available for {symbol}"
                    )

            except Exception as fundamentals_error:
                logger.error(
                    f"[{request_id}] Error fetching fundamentals: {fundamentals_error}"
                )
                fundamentals_data = None

            # Fetch news data
            news_data = None
            try:
                news_data = await self.fetcher.fetch_news(symbol, request_id)
                if news_data:
                    logger.info(
                        f"[{request_id}] Successfully fetched {len(news_data)} news items for {symbol}"
                    )
                else:
                    logger.info(f"[{request_id}] No news data available for {symbol}")

            except Exception as news_error:
                logger.error(f"[{request_id}] Error fetching news: {news_error}")
                news_data = None

            logger.info(f"[{request_id}] Parallel data fetch completed for {symbol}")
            return fundamentals_data, technical_indicators, news_data, ohlcv_df

        except Exception as error:
            logger.error(f"[{request_id}] Error in fetch_parallel_data: {error}")
            return None, {}, None, None


def get_orchestrator() -> StockOrchestrator:
    """
    Development factory function to create a StockOrchestrator instance.

    Note: This is a development convenience function. In production,
    dependencies should be injected through proper DI container.

    For production use:
    - cache: Use SupabaseCacheService or RedisCacheService
    - ai_service: Use UnifiedAIService with proper OpenRouterGateway configuration
    """
    try:
        cache = CacheService()
        ai_service = UnifiedAIService()
        return StockOrchestrator(cache, ai_service)
    except Exception as e:
        logger.error(f"Failed to create orchestrator: {e}")
        # Fallback: create with minimal dependencies
        cache = CacheService()
        return StockOrchestrator(cache, None)

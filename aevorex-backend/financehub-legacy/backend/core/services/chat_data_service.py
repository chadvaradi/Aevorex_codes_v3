"""
Chat Data Service

This service orchestrates data fetching required for AI chat context.
It replaces the monolithic `process_premium_stock_data` function by
calling the new modular services (`FundamentalsService`, `TechnicalService`, etc.)
in parallel.
"""

import asyncio

import httpx

from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.models.stock import FinBotStockResponse

# Import new modular services
from backend.core.services.stock.fundamentals_service import FundamentalsService
from backend.core.services.stock.technical_service import TechnicalService
from backend.core.services.stock.news_service import NewsService
from backend.core.services.stock.chart_service import ChartService
from backend.core.orchestrator import StockOrchestrator

logger = get_logger("aevorex_finbot.ChatDataService")


class ChatDataService:
    """Service to gather all necessary data for a chat prompt."""

    def __init__(self):
        self.fundamentals_service = FundamentalsService()
        self.technical_service = TechnicalService()
        self.news_service = NewsService()
        self.chart_service = ChartService()
        self.orchestrator = StockOrchestrator()

    async def get_stock_data_for_chat(
        self,
        symbol: str,
        client: httpx.AsyncClient,
        cache: CacheService,
        force_refresh: bool = False,
    ) -> FinBotStockResponse | None:
        """
        Fetches all required stock data for chat context in parallel.
        This method is the modular replacement for `process_premium_stock_data`.
        """
        log_prefix = f"[ChatDataService:{symbol}]"
        logger.info(f"{log_prefix} Starting parallel data fetch for chat context.")

        try:
            # Define all data fetching tasks
            tasks = {
                "fundamentals": self.fundamentals_service.get_fundamentals_data(
                    symbol, client, cache
                ),
                "technicals": self.technical_service.get_technical_analysis(
                    symbol, client, cache, force_refresh
                ),
                "news": self.news_service.get_news_data(
                    symbol, client, cache, limit=20, force_refresh=force_refresh
                ),
                "chart": self.chart_service.get_chart_data(
                    symbol,
                    client,
                    cache,
                    period="1y",
                    interval="1d",
                    force_refresh=force_refresh,
                ),
            }

            # Run all tasks concurrently
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)

            # Process results
            task_keys = list(tasks.keys())
            processed_results = {}
            for i, result in enumerate(results):
                task_name = task_keys[i]
                if isinstance(result, Exception):
                    logger.error(
                        f"{log_prefix} Task '{task_name}' failed: {result}",
                        exc_info=result,
                    )
                    processed_results[task_name] = None
                else:
                    logger.debug(f"{log_prefix} Task '{task_name}' succeeded.")
                    processed_results[task_name] = result

            # Use the orchestrator to build the final Pydantic model response
            # This ensures the data structure is consistent with what the prompt builders expect.
            final_response_model = self.orchestrator.build_response_model(
                symbol=symbol,
                fundamentals_data=processed_results.get("fundamentals"),
                technical_indicators=processed_results.get("technicals"),
                news_items=processed_results.get("news"),
                ohlcv_df=processed_results.get("chart"),
            )

            if not final_response_model:
                logger.error(
                    f"{log_prefix} Orchestrator failed to build response model."
                )
                return None

            logger.info(
                f"{log_prefix} Successfully fetched and orchestrated data for chat context."
            )
            return final_response_model

        except Exception as e:
            logger.error(
                f"{log_prefix} An unexpected error occurred during chat data fetching: {e}",
                exc_info=True,
            )
            return None

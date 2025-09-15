"""
Daily Market Summary Scheduled Job

This module contains the scheduled job that generates daily pre-market summaries
at 15:00 CET (09:00 ET) - NYSE pre-open time.
"""

import asyncio
from typing import Optional

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.core.ai.unified_service import get_unified_ai_service
from backend.utils.logger_config import get_logger

logger = get_logger("aevorex_finbot.tasks.daily_market_summary")


class DailyMarketSummaryScheduler:
    """Scheduler for daily market summary generation."""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.ai_service = get_unified_ai_service()

    async def generate_daily_summary(self) -> Optional[dict]:
        """
        Generate the daily market summary.

        Returns:
            Dict with summary data or None if failed
        """
        try:
            logger.info("Starting daily market summary generation")

            # Create HTTP client for AI service
            async with httpx.AsyncClient(timeout=60.0) as http_client:
                # Generate summary using AI service
                summary_result = await self.ai_service.generate_market_daily_summary(
                    http_client=http_client,
                    news_data=None,  # TODO: Integrate with news service when available
                )

                logger.info("Daily market summary generated successfully")
                logger.info(
                    f"Summary length: {len(summary_result.get('summary', ''))} characters"
                )

                # TODO: Store in database (Supabase/Postgres placeholder)
                # await self._store_summary_in_db(summary_result)

                return summary_result

        except Exception as e:
            logger.error(f"Failed to generate daily market summary: {e}", exc_info=True)
            return None

    async def _store_summary_in_db(self, summary_data: dict) -> None:
        """
        Store the summary in database (placeholder for future implementation).

        Args:
            summary_data: Summary data to store
        """
        # TODO: Implement database storage
        # This would connect to Supabase/Postgres and store the summary
        # with timestamp, summary text, and metadata
        logger.info(
            "Database storage not yet implemented - summary would be stored here"
        )
        pass

    def start_scheduler(self) -> None:
        """Start the scheduler with daily market summary job."""
        try:
            # Schedule job for 15:00 CET (09:00 ET) daily
            # Cron format: minute, hour, day, month, day_of_week
            self.scheduler.add_job(
                func=self.generate_daily_summary,
                trigger=CronTrigger(hour=15, minute=0),  # 15:00 CET
                id="daily_market_summary",
                name="Daily Market Summary Generation",
                replace_existing=True,
                max_instances=1,  # Prevent overlapping executions
                misfire_grace_time=300,  # 5 minutes grace period
            )

            self.scheduler.start()
            logger.info(
                "Daily market summary scheduler started - will run at 15:00 CET daily"
            )

        except Exception as e:
            logger.error(
                f"Failed to start daily market summary scheduler: {e}", exc_info=True
            )
            raise

    def stop_scheduler(self) -> None:
        """Stop the scheduler."""
        try:
            self.scheduler.shutdown(wait=True)
            logger.info("Daily market summary scheduler stopped")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}", exc_info=True)


# Global scheduler instance
_daily_summary_scheduler: Optional[DailyMarketSummaryScheduler] = None


def get_daily_summary_scheduler() -> DailyMarketSummaryScheduler:
    """
    Get or create the global daily summary scheduler instance.

    Returns:
        DailyMarketSummaryScheduler instance
    """
    global _daily_summary_scheduler
    if _daily_summary_scheduler is None:
        _daily_summary_scheduler = DailyMarketSummaryScheduler()
    return _daily_summary_scheduler


async def run_manual_summary() -> Optional[dict]:
    """
    Manually trigger a daily summary generation (for testing/debugging).

    Returns:
        Summary data or None if failed
    """
    scheduler = get_daily_summary_scheduler()
    return await scheduler.generate_daily_summary()


if __name__ == "__main__":
    # For testing the scheduler
    async def test_scheduler():
        scheduler = get_daily_summary_scheduler()
        scheduler.start_scheduler()

        # Test manual generation
        result = await run_manual_summary()
        if result:
            print("Manual summary generation successful")
            print(f"Summary: {result.get('summary', '')[:200]}...")
        else:
            print("Manual summary generation failed")

        # Keep running for a bit to test scheduling
        await asyncio.sleep(10)
        scheduler.stop_scheduler()

    asyncio.run(test_scheduler())

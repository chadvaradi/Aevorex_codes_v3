"""
Summary Logic
Provides the business logic for generating market summaries.
"""

from datetime import date, datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import Request

from backend.utils.logger_config import get_logger
from .handlers.daily_handler import generate_daily_summary as daily_handler
from .handlers.weekly_handler import generate_weekly_summary as weekly_handler
from .handlers.monthly_handler import generate_monthly_summary as monthly_handler

logger = get_logger(__name__)


async def generate_daily_summary(request: Request, target_date: Optional[date] = None) -> Dict[str, Any]:
    """
    Generate daily market summary.
    
    Args:
        request: FastAPI request object
        target_date: Date to summarize (defaults to today)
    
    Returns:
        Dict containing the daily summary data
    """
    try:
        if target_date is None:
            target_date = date.today()
        
        # Get default tickers for summary
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        
        # Mock AI service and cache for now
        # TODO: Implement proper AI service and cache integration
        ai_service = None
        http_client = None
        cache = None
        
        result = await daily_handler(ai_service, http_client, cache, tickers)
        
        return {
            "type": "daily",
            "period": {
                "start": target_date.isoformat(),
                "end": target_date.isoformat()
            },
            "summary": result,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate daily summary: {e}", exc_info=True)
        raise


async def generate_weekly_summary(request: Request, week_start: Optional[date] = None) -> Dict[str, Any]:
    """
    Generate weekly market summary.
    
    Args:
        request: FastAPI request object
        week_start: Start date of the week (defaults to current week)
    
    Returns:
        Dict containing the weekly summary data
    """
    try:
        if week_start is None:
            # Get start of current week (Monday)
            today = date.today()
            week_start = today - timedelta(days=today.weekday())
        
        # Get default tickers for summary
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        
        # Mock AI service and cache for now
        # TODO: Implement proper AI service and cache integration
        ai_service = None
        http_client = None
        cache = None
        
        result = await weekly_handler(ai_service, http_client, cache, tickers)
        
        return {
            "type": "weekly",
            "period": {
                "start": week_start.isoformat(),
                "end": (week_start + timedelta(days=6)).isoformat()
            },
            "summary": result,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate weekly summary: {e}", exc_info=True)
        raise


async def generate_custom_summary(request: Request, start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Generate custom market summary for a date range.
    
    Args:
        request: FastAPI request object
        start_date: Start date for the summary
        end_date: End date for the summary
    
    Returns:
        Dict containing the custom summary data
    """
    try:
        # Validate date range
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
        
        # Get default tickers for summary
        tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"]
        
        # Mock AI service and cache for now
        # TODO: Implement proper AI service and cache integration
        ai_service = None
        http_client = None
        cache = None
        
        # Use monthly handler for custom summaries
        result = await monthly_handler(ai_service, http_client, cache, tickers)
        
        return {
            "type": "custom",
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "summary": result,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to generate custom summary: {e}", exc_info=True)
        raise


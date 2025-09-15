
"""
Summary API Router
Provides endpoints for generating market digests (daily, weekly, custom).
"""

from fastapi import APIRouter, Query, Request, Depends
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional

from backend.utils.logger_config import get_logger
from . import summary_logic

router = APIRouter()

logger = get_logger(__name__)


@router.get("/daily", summary="Get Daily Market Summary")
async def get_daily_summary(
    request: Request,
    target_date: Optional[date] = Query(None, description="Date to summarize (defaults to today)"),
):
    """
    Returns a daily market summary.  
    By default, it generates the summary for today.  
    Optionally, a target_date can be provided.
    """
    try:
        result = await summary_logic.generate_daily_summary(request, target_date)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        logger.error(f"Daily summary failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Failed to generate daily summary."},
        )


@router.get("/weekly", summary="Get Weekly Market Summary")
async def get_weekly_summary(
    request: Request,
    week_start: Optional[date] = Query(None, description="Start date of the week"),
):
    """
    Returns a weekly market summary.  
    If week_start is not provided, defaults to the current week.
    """
    try:
        result = await summary_logic.generate_weekly_summary(request, week_start)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        logger.error(f"Weekly summary failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Failed to generate weekly summary."},
        )


@router.get("/custom", summary="Get Custom Market Summary")
async def get_custom_summary(
    request: Request,
    start_date: date = Query(..., description="Start date for the summary"),
    end_date: date = Query(..., description="End date for the summary"),
):
    """
    Returns a custom market summary for a given date range.
    Both start_date and end_date are required.
    """
    try:
        result = await summary_logic.generate_custom_summary(request, start_date, end_date)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        logger.error(f"Custom summary failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Failed to generate custom summary."},
        )


@router.get("/monthly", summary="Get Monthly Market Summary")
async def get_monthly_summary(
    request: Request,
    month_start: Optional[date] = Query(None, description="Start date of the month (defaults to current month)"),
):
    """
    Returns a monthly market summary.
    If month_start is not provided, defaults to the current month.
    Uses the custom summary logic with month boundaries.
    """
    try:
        # Calculate month boundaries
        if month_start is None:
            from datetime import datetime
            now = datetime.now()
            month_start = now.replace(day=1).date()
        
        # Calculate month end
        if month_start.month == 12:
            month_end = month_start.replace(year=month_start.year + 1, month=1, day=1)
        else:
            month_end = month_start.replace(month=month_start.month + 1, day=1)
        
        # Use custom summary logic for the month
        result = await summary_logic.generate_custom_summary(request, month_start, month_end)
        return JSONResponse(content={"status": "success", "data": result})
    except Exception as e:
        logger.error(f"Monthly summary failed: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"status": "error", "message": "Failed to generate monthly summary."},
        )
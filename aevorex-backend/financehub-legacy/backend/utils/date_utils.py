"""
Date Utilities for FinanceHub Backend
====================================

Centralized date calculation utilities.
"""

from datetime import date, timedelta
from typing import Union
from enum import Enum


class PeriodEnum(str, Enum):
    """Standard period enumeration for date calculations."""

    ONE_DAY = "1d"
    ONE_WEEK = "1w"
    ONE_MONTH = "1m"
    SIX_MONTHS = "6m"
    ONE_YEAR = "1y"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUALLY = "annually"


def calculate_start_date(period: Union[PeriodEnum, str], end_date: date) -> date:
    """
    Calculate start date based on period and end date.

    Args:
        period: Time period enum value or string
        end_date: End date for calculation

    Returns:
        Calculated start date
    """
    if isinstance(period, str):
        period = PeriodEnum(period)

    if period in [PeriodEnum.ONE_DAY, PeriodEnum.DAILY]:
        return end_date - timedelta(days=1)
    elif period in [PeriodEnum.ONE_WEEK, PeriodEnum.WEEKLY]:
        return end_date - timedelta(weeks=1)
    elif period in [PeriodEnum.ONE_MONTH, PeriodEnum.MONTHLY]:
        return end_date - timedelta(days=30)
    elif period == PeriodEnum.SIX_MONTHS:
        return end_date - timedelta(days=180)
    elif period in [PeriodEnum.ONE_YEAR, PeriodEnum.ANNUALLY]:
        return end_date - timedelta(days=365)
    elif period == PeriodEnum.QUARTERLY:
        return end_date - timedelta(days=90)
    else:
        return end_date - timedelta(days=30)  # Default to 1 month


def get_date_range_for_period(
    period: Union[PeriodEnum, str], end_date: date = None
) -> tuple[date, date]:
    """
    Get start and end dates for a given period.

    Args:
        period: Time period enum value or string
        end_date: End date (defaults to today)

    Returns:
        Tuple of (start_date, end_date)
    """
    if end_date is None:
        end_date = date.today()

    start_date = calculate_start_date(period, end_date)
    return start_date, end_date


def validate_date_range(start_date: date, end_date: date) -> bool:
    """
    Validate that start_date is before end_date.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        True if valid, False otherwise
    """
    return start_date <= end_date


def format_date_range(start_date: date, end_date: date) -> dict:
    """
    Format date range for API responses.

    Args:
        start_date: Start date
        end_date: End date

    Returns:
        Dictionary with formatted date range
    """
    return {
        "start": start_date.isoformat(),
        "end": end_date.isoformat(),
        "days": (end_date - start_date).days,
    }

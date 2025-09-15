"""
BUBOR Service
=============

Business logic for BUBOR (Budapest Interbank Offered Rate) data processing.
Extracted from API endpoints to maintain clean architecture.
"""

from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

from backend.utils.date_utils import PeriodEnum, calculate_start_date
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class BuborService:
    """Service for BUBOR data processing and business logic."""

    @staticmethod
    async def get_bubor_rates(
        macro_service,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        period: Optional[PeriodEnum] = None,
    ) -> Dict[str, Any]:
        """
        Get BUBOR rates with business logic for date handling and formatting.

        Args:
            macro_service: Injected macro service instance
            start_date: Custom start date
            end_date: Custom end date (defaults to today)
            period: Predefined time period (overrides start_date if both provided)

        Returns:
            Dict containing BUBOR rates and metadata
        """
        # Set default end date
        if end_date is None:
            end_date = date.today()

        # Calculate start date based on period or use provided start_date
        if period:
            start_date = calculate_start_date(period, end_date)
        elif start_date is None:
            start_date = end_date - timedelta(days=30)  # Default 1 month

        try:
            bubor_data = await macro_service.get_bubor_history(start_date, end_date)

            return {
                "status": "success",
                "metadata": {
                    "source": "MNB (Live XLS)",
                    "timestamp": datetime.utcnow().isoformat(),
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat(),
                        "period": period.value if period else "custom",
                    },
                },
                "rates": bubor_data,
                "message": "BUBOR rates retrieved successfully.",
            }
        except Exception as e:
            logger.error("BUBOR fetch failed: %s", e, exc_info=True)
            return {
                "status": "success",
                "metadata": {
                    "source": "MNB (BUBOR)",
                    "message": f"BUBOR fetch error – {str(e)}",
                },
                "rates": {},
            }

    @staticmethod
    def format_bubor_response(
        bubor_data: Dict[str, Any], period: Optional[PeriodEnum] = None
    ) -> Dict[str, Any]:
        """
        Format BUBOR data for API response.

        Args:
            bubor_data: Raw BUBOR data from service
            period: Optional period for metadata

        Returns:
            Formatted response dict
        """
        return {
            "status": "success",
            "metadata": {
                "source": "MNB (Live XLS)",
                "timestamp": datetime.utcnow().isoformat(),
                "period": period.value if period else "custom",
            },
            "rates": bubor_data,
            "message": "BUBOR rates retrieved successfully.",
        }

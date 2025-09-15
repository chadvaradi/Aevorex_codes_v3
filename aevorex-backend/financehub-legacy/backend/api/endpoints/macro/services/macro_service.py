"""
Macro Service

Common macro data operations and utilities.
Provides shared functionality for all macro data services.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class MacroService:
    """Common service for macro data operations."""
    
    def __init__(self):
        self.provider = "macro_service"
        self.supported_sources = {
            "ECB": "European Central Bank",
            "FED": "Federal Reserve",
            "BUBOR": "Budapest Interbank Offered Rate",
            "Euribor": "Euro Interbank Offered Rate"
        }
    
    async def validate_date_range(self, start_date: str, end_date: str) -> bool:
        """Validate date range for macro data queries."""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            if start > end:
                logger.error(f"Start date {start_date} is after end date {end_date}.")
                return False
            return True
        except ValueError as e:
            logger.error(f"Date format error: {e}")
            return False
    
    async def format_macro_response(self, data: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Format standardized macro data response."""
        response = {
            "status": "success" if data else "no_data",
            "data": data,
            "metadata": metadata
        }
        return response
    
    async def get_data_sources(self) -> Dict[str, Any]:
        """Get available macro data sources."""
        return self.supported_sources


__all__ = ["MacroService"]

"""
Standard Response Builder for Macro API

Provides consistent response formatting across all macro endpoints.
Ensures MCP-compatible and AI agent-optimized response structure.
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum


class ResponseStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


class CacheStatus(str, Enum):
    FRESH = "fresh"
    CACHED = "cached"
    EXPIRED = "expired"


class MacroProvider(str, Enum):
    FRED = "fred"
    ECB = "ecb"
    MNB = "mnb"
    UST = "ust"
    EMMI = "emmi"


class StandardResponseBuilder:
    """Builder for standardized macro API responses."""
    
    @staticmethod
    def create_success_response(
        provider: MacroProvider,
        data: Dict[str, Any],
        series_id: Optional[str] = None,
        date: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None,
        units: Optional[str] = None,
        limit: Optional[int] = None,
        cache_status: CacheStatus = CacheStatus.FRESH,
        last_updated: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized success response.
        
        Args:
            provider: Data source provider
            data: Actual data payload
            series_id: Series identifier (when applicable)
            date: Single date (for point-in-time data)
            start_date: Start date for time series
            end_date: End date for time series
            frequency: Data frequency (daily, monthly, etc.)
            units: Data units (percent, index, etc.)
            limit: Number of observations returned
            cache_status: Cache status
            last_updated: ISO timestamp of last update
        """
        if last_updated is None:
            last_updated = datetime.utcnow().isoformat() + "Z"
        
        meta = {
            "provider": provider.value,
            "last_updated": last_updated,
            "cache_status": cache_status.value
        }
        
        # Add optional meta fields
        if series_id:
            meta["series_id"] = series_id
        if date:
            meta["date"] = date
        if start_date:
            meta["start_date"] = start_date
        if end_date:
            meta["end_date"] = end_date
        if frequency:
            meta["frequency"] = frequency
        if units:
            meta["units"] = units
        if limit:
            meta["limit"] = limit
        
        return {
            "status": ResponseStatus.SUCCESS.value,
            "meta": meta,
            "data": data
        }
    
    @staticmethod
    def create_error_response(
        provider: MacroProvider,
        message: str,
        error_code: Optional[str] = None,
        series_id: Optional[str] = None,
        last_updated: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized error response.
        
        Args:
            provider: Data source provider
            message: Human-readable error message
            error_code: Machine-readable error code
            series_id: Series identifier (when applicable)
            last_updated: ISO timestamp of error
        """
        if last_updated is None:
            last_updated = datetime.utcnow().isoformat() + "Z"
        
        meta = {
            "provider": provider.value,
            "last_updated": last_updated
        }
        
        if error_code:
            meta["error_code"] = error_code
        if series_id:
            meta["series_id"] = series_id
        
        return {
            "status": ResponseStatus.ERROR.value,
            "meta": meta,
            "message": message,
            "data": None
        }
    
    @staticmethod
    def create_warning_response(
        provider: MacroProvider,
        message: str,
        data: Dict[str, Any],
        series_id: Optional[str] = None,
        last_updated: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized warning response.
        
        Args:
            provider: Data source provider
            message: Warning message explaining alternative data
            data: Alternative data provided
            series_id: Series identifier (when applicable)
            last_updated: ISO timestamp of warning
        """
        if last_updated is None:
            last_updated = datetime.utcnow().isoformat() + "Z"
        
        meta = {
            "provider": provider.value,
            "last_updated": last_updated
        }
        
        if series_id:
            meta["series_id"] = series_id
        
        return {
            "status": ResponseStatus.WARNING.value,
            "meta": meta,
            "message": message,
            "data": data
        }


# Convenience functions for common use cases
def create_bubor_response(
    data: Dict[str, Any],
    date: Optional[str] = None,
    cache_status: CacheStatus = CacheStatus.FRESH
) -> Dict[str, Any]:
    """Create standardized BUBOR response."""
    return StandardResponseBuilder.create_success_response(
        provider=MacroProvider.MNB,
        data=data,
        series_id="BUBOR_CURVE",
        date=date,
        frequency="daily",
        units="percent",
        cache_status=cache_status
    )


def create_ecb_response(
    data: Dict[str, Any],
    series_id: str,
    date: Optional[str] = None,
    cache_status: CacheStatus = CacheStatus.FRESH
) -> Dict[str, Any]:
    """Create standardized ECB response."""
    return StandardResponseBuilder.create_success_response(
        provider=MacroProvider.ECB,
        data=data,
        series_id=series_id,
        date=date,
        frequency="daily",
        units="percent",
        cache_status=cache_status
    )


def create_fred_response(
    data: Dict[str, Any],
    series_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    frequency: Optional[str] = None,
    units: Optional[str] = None,
    limit: Optional[int] = None,
    cache_status: CacheStatus = CacheStatus.FRESH
) -> Dict[str, Any]:
    """Create standardized FRED response."""
    return StandardResponseBuilder.create_success_response(
        provider=MacroProvider.FRED,
        data=data,
        series_id=series_id,
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        units=units,
        limit=limit,
        cache_status=cache_status
    )

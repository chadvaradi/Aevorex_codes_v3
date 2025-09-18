"""
Standard Response Builder for FinanceHub API
Provides consistent response formatting across all endpoints.
Ensures MCP-compatible and AI agent-optimized response structure.
"""

from datetime import datetime
from typing import Any, Dict, Optional
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


class GlobalProvider(str, Enum):
    """Global provider enum for all MCP-ready endpoints."""
    # Macro providers
    FRED = "fred"
    ECB = "ecb"
    MNB = "mnb"
    UST = "ust"
    EMMI = "emmi"
    
    # Data providers
    EODHD = "eodhd"
    YAHOO_FINANCE = "yahoo_finance"
    
    # System providers
    SEARCH = "search"
    PREMIUM = "premium"
    SYSTEM = "system"


class StandardResponseBuilder:
    """Standard response builder for consistent API responses."""
    
    @staticmethod
    def create_unified_meta(
        provider: str,
        data_type: str,
        symbol: Optional[str] = None,
        cache_status: CacheStatus = CacheStatus.FRESH,
        frequency: Optional[str] = None,
        units: Optional[str] = None,
        additional_meta: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create unified meta structure for all MCP-ready responses.
        
        Args:
            provider: Data provider (eodhd, yahoo_finance, fred, etc.)
            data_type: Type of data (stock, crypto, macro, fundamentals, etc.)
            symbol: Symbol/ticker (when applicable)
            cache_status: Cache status (fresh, cached, expired)
            frequency: Data frequency (realtime, daily, monthly, static)
            units: Data units (currency, percentage, count, etc.)
            additional_meta: Additional provider-specific metadata
            
        Returns:
            Unified meta structure for MCP compatibility
        """
        meta = {
            "provider": provider,
            "mcp_ready": True,
            "data_type": data_type,
            "cache_status": cache_status.value,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
        
        if symbol:
            meta["symbol"] = symbol
        if frequency:
            meta["frequency"] = frequency
        if units:
            meta["units"] = units
        if additional_meta:
            meta.update(additional_meta)
            
        return meta
    
    @staticmethod
    def success(data: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build a success response.
        
        Args:
            data: The response data
            meta: Optional metadata
            
        Returns:
            Standardized success response
            
        HTTP Status: 200 OK
        """
        return {
            "status": "success",
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                "cache_status": "fresh",
                **(meta or {})
            },
            "data": data
        }
    
    @staticmethod
    def error(message: str, error_code: Optional[str] = None, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build an error response.
        
        Args:
            message: Error message
            error_code: Optional error code
            meta: Optional metadata
            
        Returns:
            Standardized error response
            
        HTTP Status: 400/404/500 (depends on error_code)
        - SYMBOL_NOT_FOUND: 404 Not Found
        - NO_DATA_AVAILABLE: 404 Not Found  
        - API_ERROR: 503 Service Unavailable
        - HANDLER_ERROR: 500 Internal Server Error
        """
        return {
            "status": "error",
            "message": message,
            "error_code": error_code,
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                **(meta or {})
            },
            "data": None
        }
    
    @staticmethod
    def warning(message: str, data: Any, meta: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Build a warning response.
        
        Args:
            message: Warning message
            data: Alternative data provided
            meta: Optional metadata
            
        Returns:
            Standardized warning response
            
        HTTP Status: 200 OK (with warning flag)
        
        Usage Examples:
        - API temporarily down → cached data provided
        - Partial data available → some fields missing
        - Rate limit approaching → throttled response
        - Deprecated endpoint → alternative suggested
        """
        return {
            "status": "warning",
            "message": message,
            "meta": {
                "timestamp": datetime.utcnow().isoformat(),
                **(meta or {})
            },
            "data": data
        }
    
    # Macro-specific methods for MCP agent optimization
    @staticmethod
    def create_macro_success_response(
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
        Create standardized macro success response for MCP agents.
        
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
            "cache_status": cache_status.value,
            "mcp_ready": True
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
    def create_macro_error_response(
        provider: MacroProvider,
        message: str,
        error_code: Optional[str] = None,
        series_id: Optional[str] = None,
        last_updated: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized macro error response for MCP agents.
        
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
            "last_updated": last_updated,
            "mcp_ready": True
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
    def create_macro_warning_response(
        provider: MacroProvider,
        message: str,
        data: Dict[str, Any],
        series_id: Optional[str] = None,
        last_updated: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create standardized macro warning response for MCP agents.
        
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
            "last_updated": last_updated,
            "mcp_ready": True
        }
        
        if series_id:
            meta["series_id"] = series_id
        
        return {
            "status": ResponseStatus.WARNING.value,
            "meta": meta,
            "message": message,
            "data": data
        }


# Convenience functions for common macro use cases
def create_bubor_response(
    data: Dict[str, Any],
    date: Optional[str] = None,
    cache_status: CacheStatus = CacheStatus.FRESH
) -> Dict[str, Any]:
    """Create standardized BUBOR response."""
    return StandardResponseBuilder.create_macro_success_response(
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
    return StandardResponseBuilder.create_macro_success_response(
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
    return StandardResponseBuilder.create_macro_success_response(
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


# EODHD-specific response builders for MCP compatibility
def create_eodhd_success_response(
    data: Any,
    data_type: str,
    symbol: Optional[str] = None,
    frequency: str = "daily",
    cache_status: CacheStatus = CacheStatus.FRESH,
    provider_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized EODHD success response for MCP agents.
    
    Args:
        data: The response data
        data_type: Type of data (e.g., "stock_eod", "crypto_intraday", "forex_quote")
        symbol: Symbol/ticker (when applicable)
        frequency: Data frequency (daily, intraday, etc.)
        cache_status: Cache status
        provider_meta: Additional provider-specific metadata
        
    Returns:
        Standardized EODHD success response
    """
    meta = {
        "provider": "eodhd",
        "mcp_ready": True,
        "cache_status": cache_status.value,
        "data_type": data_type,
        "frequency": frequency,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    if symbol:
        meta["symbol"] = symbol
    if provider_meta:
        meta.update(provider_meta)
    
    return StandardResponseBuilder.success(data=data, meta=meta)


def create_eodhd_error_response(
    message: str,
    error_code: Optional[str] = None,
    symbol: Optional[str] = None,
    data_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized EODHD error response for MCP agents.
    
    Args:
        message: Human-readable error message
        error_code: Machine-readable error code
        symbol: Symbol/ticker (when applicable)
        data_type: Type of data that failed
        
    Returns:
        Standardized EODHD error response
    """
    meta = {
        "provider": "eodhd",
        "mcp_ready": True,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    if error_code:
        meta["error_code"] = error_code
    if symbol:
        meta["symbol"] = symbol
    if data_type:
        meta["data_type"] = data_type
    
    return StandardResponseBuilder.error(
        message=message,
        error_code=error_code,
        meta=meta
    )


def create_eodhd_warning_response(
    message: str,
    data: Any,
    data_type: str,
    symbol: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized EODHD warning response for MCP agents.
    
    Args:
        message: Warning message explaining alternative data
        data: Alternative data provided
        data_type: Type of data
        symbol: Symbol/ticker (when applicable)
        
    Returns:
        Standardized EODHD warning response
    """
    meta = {
        "provider": "eodhd",
        "mcp_ready": True,
        "data_type": data_type,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    if symbol:
        meta["symbol"] = symbol
    
    return StandardResponseBuilder.warning(
        message=message,
        data=data,
        meta=meta
    )


# Fundamentals-specific response builders for MCP compatibility
def create_fundamentals_success_response(
    data: Any,
    data_type: str,
    symbol: str,
    cache_status: CacheStatus = CacheStatus.FRESH,
    provider_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized fundamentals success response for MCP agents.
    
    Args:
        data: The response data
        data_type: Type of data (e.g., "company_overview", "financial_ratios", "earnings_data", "financial_statements")
        symbol: Stock symbol/ticker
        cache_status: Cache status
        provider_meta: Additional provider-specific metadata (e.g., processing_time_ms, data_points_count)
        
    Returns:
        Standardized fundamentals success response
        
    HTTP Status: 200 OK
        
    Example:
        >>> response = create_fundamentals_success_response(
        ...     data={"longName": "Apple Inc.", "sector": "Technology"},
        ...     data_type="company_overview",
        ...     symbol="AAPL",
        ...     cache_status=CacheStatus.FRESH,
        ...     provider_meta={"processing_time_ms": 1417.33}
        ... )
        >>> response["meta"]["mcp_ready"]
        True
        >>> response["meta"]["data_type"]
        "company_overview"
    """
    meta = StandardResponseBuilder.create_unified_meta(
        provider=GlobalProvider.YAHOO_FINANCE.value,
        data_type=data_type,
        symbol=symbol,
        cache_status=cache_status,
        additional_meta=provider_meta
    )
    
    return StandardResponseBuilder.success(data=data, meta=meta)


def create_fundamentals_error_response(
    message: str,
    error_code: Optional[str] = None,
    symbol: Optional[str] = None,
    data_type: Optional[str] = None,
    provider_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized fundamentals error response for MCP agents.
    
    Args:
        message: Human-readable error message
        error_code: Machine-readable error code (e.g., "SYMBOL_NOT_FOUND", "PREMIUM_DATA_REQUIRED", "YAHOO_API_ERROR")
        symbol: Stock symbol/ticker (when applicable)
        data_type: Type of data that failed (e.g., "company_overview", "financial_ratios")
        provider_meta: Additional provider-specific metadata
        
    Returns:
        Standardized fundamentals error response
        
    Example:
        >>> response = create_fundamentals_error_response(
        ...     message="Symbol AAPL not found",
        ...     error_code="SYMBOL_NOT_FOUND",
        ...     symbol="AAPL",
        ...     data_type="company_overview"
        ... )
        >>> response["meta"]["error_code"]
        "SYMBOL_NOT_FOUND"
        >>> response["meta"]["mcp_ready"]
        True
    """
    meta = {
        "provider": "yahoo_finance",
        "mcp_ready": True,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    if error_code:
        meta["error_code"] = error_code
    if symbol:
        meta["symbol"] = symbol
    if data_type:
        meta["data_type"] = data_type
    if provider_meta:
        meta.update(provider_meta)
    
    return StandardResponseBuilder.error(
        message=message,
        error_code=error_code,
        meta=meta
    )


def create_fundamentals_warning_response(
    message: str,
    data: Any,
    data_type: str,
    symbol: str,
    provider_meta: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized fundamentals warning response for MCP agents.
    
    Args:
        message: Warning message explaining alternative data or limitations
        data: Alternative data provided (e.g., cached data, partial data)
        data_type: Type of data (e.g., "company_overview", "financial_ratios")
        symbol: Stock symbol/ticker
        provider_meta: Additional provider-specific metadata
        
    Returns:
        Standardized fundamentals warning response
        
    Example:
        >>> response = create_fundamentals_warning_response(
        ...     message="Using cached data - Yahoo Finance API temporarily unavailable",
        ...     data={"longName": "Apple Inc.", "sector": "Technology"},
        ...     data_type="company_overview",
        ...     symbol="AAPL"
        ... )
        >>> response["meta"]["mcp_ready"]
        True
        >>> response["status"]
        "warning"
    """
    meta = {
        "provider": "yahoo_finance",
        "mcp_ready": True,
        "data_type": data_type,
        "symbol": symbol,
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    if provider_meta:
        meta.update(provider_meta)
    
    return StandardResponseBuilder.warning(
        message=message,
        data=data,
        meta=meta
    )


def create_paywall_error_response(
    message: str,
    subscription_required: bool = True,
    plan_required: str = "pro",
    symbol: Optional[str] = None,
    data_type: Optional[str] = None,
    provider: str = "premium",
    alternative_endpoints: Optional[list] = None,
    upgrade_url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create standardized paywall error response for MCP agents.
    
    Args:
        message: Human-readable error message
        subscription_required: Whether subscription is required
        plan_required: Required subscription plan
        symbol: Symbol/ticker (when applicable)
        data_type: Type of data that requires premium access
        provider: Data provider name
        alternative_endpoints: List of alternative free endpoints
        upgrade_url: URL to upgrade subscription
        
    Returns:
        Standardized paywall error response
        
    HTTP Status: 402 Payment Required
    ""
    Example:
        >>> response = create_paywall_error_response(
        ...     message="Premium subscription required for financial statements",
        ...     symbol="AAPL",
        ...     data_type="financial_statements",
        ...     alternative_endpoints=["/fundamentals/overview/AAPL", "/fundamentals/ratios/AAPL"]
        ... )
        >>> response["meta"]["subscription_required"]
        True
        >>> response["meta"]["error_code"]
        "UPGRADE_REQUIRED"
    """
    meta = {
        "provider": provider,
        "mcp_ready": True,
        "subscription_required": subscription_required,
        "plan_required": plan_required,
        "error_code": "UPGRADE_REQUIRED",
        "error_type": "subscription_error",
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    if symbol:
        meta["symbol"] = symbol
    if data_type:
        meta["data_type"] = data_type
    if alternative_endpoints:
        meta["alternative_endpoints"] = alternative_endpoints
    if upgrade_url:
        meta["upgrade_url"] = upgrade_url
    
    return StandardResponseBuilder.error(
        message=message,
        error_code="UPGRADE_REQUIRED",
        meta=meta
    )


# def create_subscription_required_response(
    message: str = "Premium subscription required for this data",

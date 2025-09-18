"""
Standardized Metadata Utilities for Macro Endpoints

Provides consistent metadata formatting across all macro endpoints
to ensure uniform response structure and better API usability.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_standard_metadata(
    provider: str,
    cache_status: str = "fresh",
    last_updated: Optional[str] = None,
    data_source_url: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized metadata for macro endpoint responses.
    
    Args:
        provider: Data provider name (e.g., "FRED", "ECB", "MNB", "US Treasury")
        cache_status: Cache status ("fresh", "stale", "cached")
        last_updated: ISO timestamp of last data update
        data_source_url: URL of the data source
        description: Human-readable description of the data
        **kwargs: Additional metadata fields
        
    Returns:
        Standardized metadata dictionary
    """
    if last_updated is None:
        last_updated = datetime.now().isoformat()
    
    metadata = {
        "last_updated": last_updated,
        "provider": provider,
        "cache_status": cache_status,
    }
    
    if data_source_url:
        metadata["data_source_url"] = data_source_url
    
    if description:
        metadata["description"] = description
    
    # Add any additional metadata fields
    metadata.update(kwargs)
    
    return metadata


def create_standard_response(
    status: str,
    data: Any,
    metadata: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized response format for macro endpoints.
    
    Args:
        status: Response status ("success", "error", "warning")
        data: Actual data payload
        metadata: Standardized metadata
        **kwargs: Additional response fields
        
    Returns:
        Standardized response dictionary
    """
    response = {
        "status": status,
        "data": data,
        "metadata": metadata,
    }
    
    # Add any additional response fields
    response.update(kwargs)
    
    return response


def create_error_response(
    error_message: str,
    provider: str,
    error_code: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized error response for macro endpoints.
    
    Args:
        error_message: Human-readable error message
        provider: Data provider name
        error_code: Optional error code
        **kwargs: Additional error fields
        
    Returns:
        Standardized error response dictionary
    """
    metadata = create_standard_metadata(
        provider=provider,
        cache_status="error",
        description=f"Error: {error_message}"
    )
    
    if error_code:
        metadata["error_code"] = error_code
    
    return create_standard_response(
        status="error",
        data={"error": error_message},
        metadata=metadata,
        **kwargs
    )


def create_warning_response(
    warning_message: str,
    data: Any,
    provider: str,
    **kwargs
) -> Dict[str, Any]:
    """
    Create standardized warning response for macro endpoints.
    
    Args:
        warning_message: Human-readable warning message
        data: Actual data payload (may be partial or fallback data)
        provider: Data provider name
        **kwargs: Additional warning fields
        
    Returns:
        Standardized warning response dictionary
    """
    metadata = create_standard_metadata(
        provider=provider,
        cache_status="warning",
        description=f"Warning: {warning_message}"
    )
    
    return create_standard_response(
        status="warning",
        data=data,
        metadata=metadata,
        warning=warning_message,
        **kwargs
    )


# Common metadata templates for different providers
FRED_METADATA = {
    "provider": "FRED",
    "data_source_url": "https://fred.stlouisfed.org/",
    "description": "Federal Reserve Economic Data"
}

ECB_METADATA = {
    "provider": "ECB",
    "data_source_url": "https://www.ecb.europa.eu/",
    "description": "European Central Bank"
}

MNB_METADATA = {
    "provider": "MNB",
    "data_source_url": "https://www.mnb.hu/",
    "description": "Magyar Nemzeti Bank"
}

US_TREASURY_METADATA = {
    "provider": "US Treasury",
    "data_source_url": "https://home.treasury.gov/",
    "description": "US Department of the Treasury"
}

EMMI_METADATA = {
    "provider": "EMMI",
    "data_source_url": "https://www.euribor-rates.eu/",
    "description": "European Money Markets Institute"
}

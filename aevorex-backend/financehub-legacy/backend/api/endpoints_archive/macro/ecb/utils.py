"""
ECB Endpoints Utilities
=======================

Utility functions for ECB API endpoints.
"""

from fastapi import Depends
from backend.api.deps import get_cache_service
from backend.core.services.macro_service import MacroDataService
from backend.utils.cache_service import CacheService


def get_macro_service(
    cache: CacheService = Depends(get_cache_service),
) -> MacroDataService:
    """
    Dependency injector for MacroDataService.

    Args:
        cache: Cache service instance

    Returns:
        Configured MacroDataService instance
    """
    return MacroDataService(cache_service=cache)


# Export the macro service function
__all__ = ["get_macro_service"]

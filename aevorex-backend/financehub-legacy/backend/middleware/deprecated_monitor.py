"""
Deprecated Route Monitor Middleware

Monitors usage of deprecated routes and logs warnings.
"""

import logging
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class DeprecatedRouteMonitorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor deprecated route usage.
    """
    
    def __init__(self, app, cache_service_factory: Optional[Callable] = None):
        super().__init__(app)
        self.cache_service_factory = cache_service_factory
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and monitor for deprecated routes.
        """
        # For now, just pass through without monitoring
        # This can be extended later to track deprecated route usage
        response = await call_next(request)
        return response
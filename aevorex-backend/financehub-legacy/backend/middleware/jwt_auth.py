"""
JWT Authentication Middleware for FinanceHub
============================================

Legacy compatibility module that imports from the new modular structure.
This file maintains backward compatibility while using the new modular JWT system.
"""

import logging

# Import from new modular structure
from .jwt_auth import (
    JWTAuthMiddleware,
    JWTTokenService,
    create_jwt_middleware,
    SECURITY_HEADERS,
)

logger = logging.getLogger("aevorex_finbot_api.middleware.jwt_auth_legacy")

# Re-export for backward compatibility
__all__ = [
    "JWTAuthMiddleware",
    "JWTTokenService",
    "create_jwt_middleware",
    "SECURITY_HEADERS",
]

logger.info("JWT Auth legacy compatibility module loaded")

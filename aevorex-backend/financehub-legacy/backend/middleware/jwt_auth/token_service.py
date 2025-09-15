"""
JWT Token Service
================

Unified service that combines token validation and creation functionality.
"""

import logging
from typing import Dict, Any, Optional
import redis.asyncio as redis

from .token_validator import JWTTokenValidator
from .token_creator import JWTTokenCreator

logger = logging.getLogger("aevorex_finbot_api.middleware.jwt_auth.service")


class JWTTokenService:
    """
    Unified JWT Token Service

    Combines token validation and creation in a single service interface.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        token_expiration: int = 900,
        redis_client: Optional[redis.Redis] = None,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expiration = token_expiration
        self.redis_client = redis_client

        # Initialize component services
        self.validator = JWTTokenValidator(
            secret_key=secret_key, algorithm=algorithm, redis_client=redis_client
        )

        self.creator = JWTTokenCreator(
            secret_key=secret_key,
            algorithm=algorithm,
            token_expiration=token_expiration,
            redis_client=redis_client,
        )

        logger.info("JWT Token Service initialized")

    # Token validation methods
    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Validate JWT token and return user data"""
        return await self.validator.validate_token(token)

    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if token is blacklisted"""
        return await self.validator.is_token_blacklisted(token)

    # Token creation methods
    async def create_token(self, user_data: Dict[str, Any]) -> str:
        """Create new JWT token"""
        return await self.creator.create_token(user_data)

    async def refresh_token(self, token: str) -> str:
        """Refresh existing JWT token"""
        return await self.creator.refresh_token(token)

    async def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""
        return await self.creator.revoke_token(token)

    # Session management
    async def get_user_session(self, user_id: str) -> Optional[str]:
        """Get active session token for user"""
        if not self.redis_client:
            return None

        try:
            token = await self.redis_client.get(f"session:{user_id}")
            return token.decode() if token else None
        except Exception as e:
            logger.error(f"Error getting user session: {str(e)}")
            return None

    async def clear_user_session(self, user_id: str) -> bool:
        """Clear user session"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(f"session:{user_id}")
            logger.info(f"Session cleared for user: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing user session: {str(e)}")
            return False

    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        if not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys("session:*")
            return len(keys)
        except Exception as e:
            logger.error(f"Error counting active sessions: {str(e)}")
            return 0

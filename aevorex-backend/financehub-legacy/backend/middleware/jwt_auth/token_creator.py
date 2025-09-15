"""
JWT Token Creation Module
========================

Handles JWT token creation, refresh, and session management.
"""

import jwt
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, status
import redis.asyncio as redis

from .config import JWT_DEFAULTS

logger = logging.getLogger("aevorex_finbot_api.middleware.jwt_auth.creator")


class JWTTokenCreator:
    """
    JWT Token Creation and Management Service

    Handles token creation, refresh, and session management.
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

    async def create_token(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new JWT token for a user
        """
        now = datetime.utcnow()
        exp = now + timedelta(seconds=self.token_expiration)

        payload = {
            "user_id": user_data["user_id"],
            "email": user_data["email"],
            "name": user_data.get("name", ""),
            "roles": user_data.get("roles", ["user"]),
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "jti": f"{user_data['user_id']}_{int(now.timestamp())}",  # JWT ID
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

        # Store token in Redis for session management
        if self.redis_client:
            await self.redis_client.setex(
                f"session:{user_data['user_id']}", self.token_expiration, token
            )

        logger.info(f"Created JWT token for user: {user_data['email']}")
        return token

    async def refresh_token(self, token: str) -> str:
        """
        Refresh an existing JWT token
        """
        try:
            # Decode token without expiration check
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )

            # Check if token is not too old (max 1 hour)
            iat = payload.get("iat")
            max_age = JWT_DEFAULTS["max_refresh_age"]
            if iat and datetime.utcfromtimestamp(iat) < datetime.utcnow() - timedelta(
                seconds=max_age
            ):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token is too old to refresh",
                )

            # Create new token
            user_data = {
                "user_id": payload["user_id"],
                "email": payload["email"],
                "name": payload.get("name", ""),
                "roles": payload.get("roles", ["user"]),
            }

            new_token = await self.create_token(user_data)

            # Blacklist old token
            if self.redis_client:
                await self.redis_client.setex(
                    f"blacklist:{token}", JWT_DEFAULTS["blacklist_ttl"], "refreshed"
                )

            logger.info(f"Token refreshed for user: {payload.get('email', 'unknown')}")
            return new_token

        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token for refresh",
            )

    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a JWT token (add to blacklist)
        """
        if not self.redis_client:
            logger.warning("Cannot revoke token: Redis client not available")
            return False

        try:
            # Add token to blacklist
            await self.redis_client.setex(
                f"blacklist:{token}", self.token_expiration, "revoked"
            )

            # Remove from active sessions
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": False},
            )

            await self.redis_client.delete(f"session:{payload['user_id']}")

            logger.info(f"Token revoked for user: {payload.get('email', 'unknown')}")
            return True

        except Exception as e:
            logger.error(f"Error revoking token: {str(e)}")
            return False

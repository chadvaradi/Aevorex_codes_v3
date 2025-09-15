"""
JWT Token Validation Module
===========================

Handles JWT token extraction, validation, and payload verification.
"""

import jwt
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import Request, HTTPException, status
import redis.asyncio as redis

from .config import REQUIRED_JWT_FIELDS

logger = logging.getLogger("aevorex_finbot_api.middleware.jwt_auth.validator")


class JWTTokenValidator:
    """
    JWT Token Validation Service

    Handles token extraction from requests and validation logic.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        redis_client: Optional[redis.Redis] = None,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.redis_client = redis_client

    async def extract_token(self, request: Request) -> str:
        """
        Extract JWT token from Authorization header
        """
        authorization = request.headers.get("Authorization")

        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing",
            )

        try:
            scheme, token = authorization.split(" ", 1)
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authorization scheme",
                )
            return token
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format",
            )

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate JWT token and return user data
        """
        try:
            # Check if token is blacklisted
            if self.redis_client:
                is_blacklisted = await self.redis_client.get(f"blacklist:{token}")
                if is_blacklisted:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Token has been revoked",
                    )

            # Decode and validate token
            payload = jwt.decode(
                token,  # PyJWT v2+ handles string tokens directly
                self.secret_key,
                algorithms=[self.algorithm],
                options={"verify_exp": True},
            )

            # Check token expiration
            exp = payload.get("exp")
            if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
                )

            # Validate required fields
            for field in REQUIRED_JWT_FIELDS:
                if field not in payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid token: missing {field}",
                    )

            logger.debug(f"Token validated for user: {payload.get('email', 'unknown')}")
            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}",
            )

    async def is_token_blacklisted(self, token: str) -> bool:
        """
        Check if token is in blacklist
        """
        if not self.redis_client:
            return False

        try:
            result = await self.redis_client.get(f"blacklist:{token}")
            return result is not None
        except Exception as e:
            logger.error(f"Error checking token blacklist: {str(e)}")
            return False

    async def blacklist_token(self, token: str, ttl: int = 3600) -> bool:
        """
        Add token to blacklist
        """
        if not self.redis_client:
            logger.warning("Cannot blacklist token: Redis client not available")
            return False

        try:
            await self.redis_client.setex(f"blacklist:{token}", ttl, "revoked")
            logger.info("Token blacklisted successfully")
            return True
        except Exception as e:
            logger.error(f"Error blacklisting token: {str(e)}")
            return False

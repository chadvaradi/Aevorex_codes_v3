"""
JWT Authentication Middleware
============================

Main middleware class that handles JWT authentication for FastAPI requests.
"""

import logging
from typing import Optional
from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import redis.asyncio as redis

from .config import SECURITY_HEADERS, is_public_endpoint
from .token_validator import JWTTokenValidator
from .token_creator import JWTTokenCreator

logger = logging.getLogger("aevorex_finbot_api.middleware.jwt_auth")


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    JWT Authentication Middleware

    Handles JWT token validation and adds security headers to responses.
    """

    def __init__(
        self,
        app,
        secret_key: str,
        redis_client: Optional[redis.Redis] = None,
        algorithm: str = "HS256",
        token_expiration: int = 900,
    ):
        super().__init__(app)
        self.secret_key = secret_key
        self.redis_client = redis_client
        self.algorithm = algorithm
        self.token_expiration = token_expiration

        # Initialize token services
        self.validator = JWTTokenValidator(
            secret_key=secret_key, algorithm=algorithm, redis_client=redis_client
        )

        self.creator = JWTTokenCreator(
            secret_key=secret_key,
            algorithm=algorithm,
            token_expiration=token_expiration,
            redis_client=redis_client,
        )

        logger.info("JWT Authentication Middleware initialized")

    async def dispatch(self, request: Request, call_next):
        """
        Process incoming requests with JWT authentication
        """
        # Add security headers to all responses
        response = await self._process_request(request, call_next)
        self._add_security_headers(response)
        return response

    async def _process_request(self, request: Request, call_next):
        """
        Process request with JWT validation
        """
        path = request.url.path

        # Skip authentication for public endpoints
        if is_public_endpoint(path):
            logger.debug(f"Skipping auth for public endpoint: {path}")
            return await call_next(request)

        try:
            # Extract and validate JWT token
            token = await self.validator.extract_token(request)
            user_data = await self.validator.validate_token(token)

            # Add user data to request state
            request.state.user = user_data
            request.state.token = token

            logger.debug(f"Authenticated user: {user_data.get('email', 'unknown')}")

            # Process request
            response = await call_next(request)
            return response

        except HTTPException as e:
            logger.warning(f"Authentication failed for {path}: {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail, "authenticated": False},
            )
        except Exception as e:
            logger.error(f"Unexpected error in JWT middleware: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal authentication error"},
            )

    def _add_security_headers(self, response: Response):
        """
        Add security headers to response
        """
        for header, value in SECURITY_HEADERS.items():
            response.headers[header] = value

        # Add CORS headers if needed
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"

    async def get_current_user(self, request: Request) -> dict:
        """
        Get current authenticated user from request
        """
        if hasattr(request.state, "user"):
            return request.state.user
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not authenticated"
        )

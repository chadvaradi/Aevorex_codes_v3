"""
JWT Authentication Middleware for FinanceHub Backend
"""

import jwt
import time
from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from backend.config import settings
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class JWTBearer(HTTPBearer):
    """JWT Bearer token authentication"""

    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        credentials: HTTPAuthorizationCredentials = await super(
            JWTBearer, self
        ).__call__(request)

        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme.",
                )

            token_data = self.verify_jwt(credentials.credentials)
            if not token_data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token.",
                )

            # Add user info to request state
            request.state.user = token_data
            return credentials.credentials
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid authorization code.",
            )

    def verify_jwt(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and return payload"""
        try:
            # Decode the token
            payload = jwt.decode(
                token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
            )

            # Check expiration
            if payload.get("exp", 0) < time.time():
                logger.warning("JWT token expired")
                return None

            return payload

        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {e}")
            return None
        except Exception as e:
            logger.error(f"JWT verification error: {e}")
            return None

    def create_access_token(
        self, data: Dict[str, Any], expires_delta: Optional[int] = None
    ) -> str:
        """Create a new JWT access token"""
        to_encode = data.copy()

        if expires_delta:
            expire = time.time() + expires_delta
        else:
            expire = time.time() + settings.JWT_EXPIRATION_TIME

        to_encode.update({"exp": expire, "iat": time.time()})

        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )

        return encoded_jwt


# Global JWT bearer instance
jwt_bearer = JWTBearer()


# Dependency for protected routes
async def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current user from JWT token"""
    if not hasattr(request.state, "user"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )
    return request.state.user


# Optional authentication (for public endpoints that can benefit from user context)
async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    """Get current user from JWT token (optional)"""
    return getattr(request.state, "user", None)

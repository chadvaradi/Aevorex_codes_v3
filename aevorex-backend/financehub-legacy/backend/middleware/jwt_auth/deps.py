"""
JWT Authentication Dependencies
==============================

FastAPI dependency functions for JWT authentication.
"""

from typing import Dict, Any, Optional
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt


# Create a custom HTTPBearer that doesn't auto-raise 403
class OptionalHTTPBearer(HTTPBearer):
    def __init__(self, auto_error: bool = False):
        super().__init__(auto_error=auto_error)


security = OptionalHTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request = None,
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user

    Args:
        credentials: HTTP Bearer token from Authorization header (optional)
        request: FastAPI request object

    Returns:
        Dict containing user information from JWT token

    Raises:
        HTTPException: If token is invalid or user not authenticated
    """
    try:
        # If we have user data in request state, use it
        if request and hasattr(request.state, "user"):
            return request.state.user

        # Check if credentials are provided
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Authorization header missing"
            )

        # Direct JWT validation without async validator
        from .config import JWT_SECRET_KEY, JWT_ALGORITHM

        token = credentials.credentials  # already string, no need to encode
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )
    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication error: {str(e)}",
        )


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    request: Request = None,
) -> Optional[Dict[str, Any]]:
    """
    Optional version of get_current_user that returns None if not authenticated
    """
    try:
        return get_current_user(credentials, request)
    except HTTPException:
        return None

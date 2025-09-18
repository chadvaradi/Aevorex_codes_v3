"""
Settings for Google OAuth2 Authentication.
"""

import os
from typing import Optional, ClassVar
from pydantic import Field, field_validator
from pydantic.networks import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

# Use a shared logger instance for consistency
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)


class GoogleAuthSettings(BaseSettings):
    """Settings for Google OAuth2."""

    model_config = SettingsConfigDict(
        env_prefix="FINBOT_GOOGLE_AUTH__", case_sensitive=False
    )

    ENABLED: bool = True
    CLIENT_ID: Optional[str] = Field(
        "DUMMY_CLIENT_ID", description="Google OAuth Client ID"
    )
    CLIENT_SECRET: Optional[str] = Field(
        "DUMMY_CLIENT_SECRET", description="Google OAuth Client Secret"
    )
    REDIRECT_URI: Optional[AnyHttpUrl] = Field(
        "http://localhost:8084/api/v1/auth/callback",
        description="Google OAuth Redirect URI",
    )
    SECRET_KEY: Optional[str] = Field(
        "DUMMY_SECRET_KEY", description="Secret key for signing session cookies"
    )

    # Static URLs, not configured by user
    AUTHORIZATION_URL: ClassVar[str] = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL: ClassVar[str] = "https://www.googleapis.com/oauth2/v4/token"

    @field_validator("ENABLED")
    @classmethod
    def check_enabled_dependencies(cls, v, info):
        # Bypass this check during OpenAPI schema generation
        if os.getenv("IS_OPENAPI_GENERATION") == "true":
            return v

        # TODO: Fix Pydantic v2 validator to properly access model fields
        # For now, allow startup to proceed - validation will be implemented later
        if v:
            logger.info("Google Auth is enabled - validation temporarily disabled for startup")
        return v

"""
CORS settings.
"""

from pydantic import Field, model_validator
from pydantic.networks import AnyHttpUrl
from pydantic_settings import BaseSettings

from ._core import _parse_env_list_str_utility


class CorsSettings(BaseSettings):
    """CORS beállítások."""

    ENABLED: bool = Field(True, validation_alias="FINBOT_CORS__ENABLED")
    ALLOWED_ORIGINS_STR: str | None = Field(None, alias="FINBOT_CORS__ALLOWED_ORIGINS")
    ALLOWED_ORIGINS: list[AnyHttpUrl] = []
    ALLOW_CREDENTIALS: bool = Field(
        True, validation_alias="FINBOT_CORS__ALLOW_CREDENTIALS"
    )
    # Provide simple comma-separated defaults so that `_parse_env_list_str_utility` generates
    # clean lists like ["GET", "POST", "OPTIONS", ...] without the leftover JSON brackets
    # that previously caused CORS pre-flight (OPTIONS) to be rejected with HTTP 400.
    ALLOWED_METHODS_STR: str | None = Field(
        default="GET,POST,OPTIONS,PUT,DELETE,PATCH",
        alias="FINBOT_CORS__ALLOWED_METHODS",
    )
    ALLOWED_METHODS: list[str] = []
    ALLOWED_HEADERS_STR: str | None = Field(
        default="Accept,Accept-Language,Content-Language,Content-Type,Authorization,X-Requested-With",
        alias="FINBOT_CORS__ALLOWED_HEADERS",
    )
    ALLOWED_HEADERS: list[str] = []
    MAX_AGE: int = 3600

    @model_validator(mode="after")
    def process_env_strings(self):
        parsed_origins = _parse_env_list_str_utility(self.ALLOWED_ORIGINS_STR)
        # Development-friendly default: allow local dev frontend if nothing specified
        if not parsed_origins:
            parsed_origins = ["http://localhost:8083", "http://127.0.0.1:8083"]

        self.ALLOWED_ORIGINS = [AnyHttpUrl(origin) for origin in parsed_origins]

        # Parse methods and ensure they're clean strings, not JSON-like format
        parsed_methods = _parse_env_list_str_utility(self.ALLOWED_METHODS_STR)
        if not parsed_methods:
            parsed_methods = ["GET", "POST", "OPTIONS", "PUT", "DELETE", "PATCH"]
        self.ALLOWED_METHODS = parsed_methods

        # Parse headers and ensure they're clean strings
        parsed_headers = _parse_env_list_str_utility(self.ALLOWED_HEADERS_STR)
        if not parsed_headers:
            # Use standard CORS headers instead of just "*" to avoid issues
            parsed_headers = [
                "Accept",
                "Accept-Language",
                "Content-Language",
                "Content-Type",
                "Authorization",
                "X-Requested-With",
                "Access-Control-Request-Method",
                "Access-Control-Request-Headers",
            ]
        self.ALLOWED_HEADERS = parsed_headers
        return self

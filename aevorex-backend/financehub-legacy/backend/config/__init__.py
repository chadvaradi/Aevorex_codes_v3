"""
Central configuration module for the Aevorex FinBot Backend.

This __init__.py file orchestrates the modular configuration by:
1. Importing all individual setting classes from their respective files.
2. Composing them into a single, top-level `Settings` model.
3. Instantiating a global `settings` object to be used throughout the application.
"""

from .env_loader import load_environment_once

# Load environment variables once (idempotens)
load_environment_once()

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Import individual settings classes
from .meta import ApplicationMetaSettings
from .environment import EnvironmentSettings
from .paths import PathSettings
from .cors import CorsSettings
from .api_keys import APIKeysSettings
from .auth import GoogleAuthSettings
from .redis import RedisSettings
from .uvicorn import UvicornSettings
from .http import HttpClientSettings
from .cache import CacheSettings
from .data_source import DataSourceSettings
from .eodhd import EODHDSettings
from .ai import AISettings
from .news import NewsProcessingSettings
from .data_processing import DataProcessingSettings
from .ticker_tape import TickerTapeSettings
from .file_processing import FileProcessingSettings
from .subscription import SubscriptionSettings


class Settings(BaseSettings):
    """
    Aevorex FinBot Backend central configuration model.
    """

    API_PREFIX: str = Field(
        default="/api/v1", description="Global prefix for API endpoints."
    )

    # Database configuration
    DATABASE_URL: str = Field(
        default="postgresql://username:password@localhost:5432/financehub",
        description="PostgreSQL database connection URL for subscription data",
    )

    # Supabase configuration
    SUPABASE_URL: str = Field(default="", description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(default="", description="Supabase anonymous API key")

    # JWT configuration
    JWT_SECRET_KEY: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_EXPIRATION_TIME: int = Field(
        default=3600, description="JWT token expiration time in seconds"
    )

    # Embedded settings groups
    APP_META: ApplicationMetaSettings = Field(default_factory=ApplicationMetaSettings)
    ENVIRONMENT: EnvironmentSettings = Field(default_factory=EnvironmentSettings)
    PATHS: PathSettings = Field(default_factory=PathSettings)
    CORS: CorsSettings = Field(default_factory=CorsSettings)
    API_KEYS: APIKeysSettings = Field(default_factory=APIKeysSettings)
    GOOGLE_AUTH: GoogleAuthSettings = Field(default_factory=GoogleAuthSettings)
    REDIS: RedisSettings = Field(default_factory=RedisSettings)
    UVICORN: UvicornSettings = Field(default_factory=UvicornSettings)
    HTTP_CLIENT: HttpClientSettings = Field(default_factory=HttpClientSettings)
    CACHE: CacheSettings = Field(default_factory=CacheSettings)
    DATA_SOURCE: DataSourceSettings = Field(default_factory=DataSourceSettings)
    EODHD: EODHDSettings = Field(default_factory=EODHDSettings)
    AI: AISettings = Field(default_factory=AISettings)
    NEWS: NewsProcessingSettings = Field(default_factory=NewsProcessingSettings)
    DATA_PROCESSING: DataProcessingSettings = Field(
        default_factory=DataProcessingSettings
    )
    TICKER_TAPE: TickerTapeSettings = Field(default_factory=TickerTapeSettings)
    FILE_PROCESSING: FileProcessingSettings = Field(
        default_factory=FileProcessingSettings
    )
    SUBSCRIPTION: SubscriptionSettings = Field(default_factory=SubscriptionSettings)
    # Optional feature flags for fine-grained fallback control (NODE_ENV already gates behavior)
    AI__ALLOW_FALLBACK: bool = Field(default=False)
    NEWS__ALLOW_FALLBACK: bool = Field(default=False)
    CRYPTO__ALLOW_FALLBACK: bool = Field(default=False)
    MACRO__ALLOW_CACHE_FALLBACK: bool = Field(default=False)
    AUTH__ALLOW_MOCK: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_nested_delimiter="__", env_file="env.local", extra="ignore"
    )


# Instantiate the global settings object
settings = Settings()

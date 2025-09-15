"""
Cache Helper Functions
======================

Centralized cache utilities for the FinanceHub application.
Consolidated from cache_ops and cache_utils modules.
"""

import hashlib
import logging
from typing import Any
from collections.abc import Callable, Awaitable

import pandas as pd
from pydantic import SecretStr

try:
    from backend.config import settings
    from backend.utils.logger_config import get_logger
    from backend.core.cache_init import CacheService

    package_logger = get_logger(f"aevorex_finbot.core.helpers.{__name__}")
except ImportError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    package_logger = logging.getLogger(
        f"aevorex_finbot.core.helpers_fallback.{__name__}"
    )
    CacheService = object  # Placeholder

FETCH_FAILED_MARKER = "FETCH_FAILED_V1"


# --- Cache Operations Section ---


def generate_cache_key(
    data_type: str,
    source: str,
    identifier: str,
    params: dict[str, Any] | None = None,
) -> str:
    """
    Generál egy egyedi cache kulcsot a megadott paraméterek alapján.
    """
    key_parts = [data_type, source, identifier]

    if params:
        # Rendezi a paramétereket a konzisztencia érdekében
        sorted_params = sorted(params.items())
        param_str = "&".join(f"{k}={v}" for k, v in sorted_params)
        key_parts.append(param_str)

    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


async def get_from_cache_or_fetch(
    cache_key: str,
    fetch_func: Callable[[], Awaitable[Any]],
    cache_service: CacheService,
    ttl_seconds: int,
) -> Any | None:
    """
    Megpróbálja lekérni az adatot a cache-ből, ha nincs ott, akkor fetch-eli.
    """
    try:
        # Cache-ből próbálja lekérni
        cached_data = await cache_service.get(cache_key)
        if cached_data is not None:
            if cached_data == FETCH_FAILED_MARKER:
                package_logger.warning(f"Cache hit for failed fetch: {cache_key}")
                return None
            return cached_data

        # Ha nincs cache-ben, fetch-eli
        package_logger.info(f"Cache miss, fetching: {cache_key}")
        data = await fetch_func()

        if data is not None:
            await cache_service.set(cache_key, data, ttl_seconds)
        else:
            # Ha a fetch sikertelen volt, cache-be tesz egy marker-t
            await cache_service.set(cache_key, FETCH_FAILED_MARKER, ttl_seconds)

        return data

    except Exception as e:
        package_logger.error(f"Error in get_from_cache_or_fetch: {e}")
        # Ha hiba van, próbálja fetch-elni közvetlenül
        try:
            return await fetch_func()
        except Exception as fetch_error:
            package_logger.error(f"Fetch also failed: {fetch_error}")
            return None


# --- Cache Utilities Section ---


async def get_api_key(key_name: str) -> str | None:
    """
    Visszaadja az API kulcsot stringként, ha megtalálható és érvényes.
    """
    log_prefix = f"[get_api_key({key_name})]"
    key_name_upper = key_name.upper()

    try:
        if not hasattr(settings, "API_KEYS") or settings.API_KEYS is None:
            package_logger.warning(
                f"{log_prefix} 'settings.API_KEYS' structure not found or is None."
            )
            return None

        api_key_secret = getattr(settings.API_KEYS, key_name_upper, None)

        if api_key_secret is None:
            package_logger.warning(
                f"{log_prefix} API Key attribute '{key_name_upper}' not found."
            )
            return None

        if not isinstance(api_key_secret, SecretStr):
            package_logger.error(
                f"{log_prefix} API Key '{key_name_upper}' is not a SecretStr type."
            )
            return None

        secret_value = api_key_secret.get_secret_value()

        if not secret_value or not secret_value.strip():
            package_logger.warning(
                f"{log_prefix} API Key '{key_name_upper}' is empty or whitespace."
            )
            return None

        return secret_value.strip()

    except Exception as e:
        package_logger.error(f"{log_prefix} Error retrieving API key: {e}")
        return None


def safe_get(data: dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Biztonságosan lekér egy értéket a dictionary-ből, ha a kulcs nem létezik,
    akkor a default értéket adja vissza.
    """
    if not isinstance(data, dict):
        return default

    return data.get(key, default)


def _ensure_datetime_index(df: pd.DataFrame) -> pd.DataFrame:
    """
    Biztosítja, hogy a DataFrame indexe datetime típusú legyen.
    """
    if df.empty:
        return df

    if not isinstance(df.index, pd.DatetimeIndex):
        try:
            df.index = pd.to_datetime(df.index)
        except Exception as e:
            package_logger.warning(f"Could not convert index to datetime: {e}")

    return df

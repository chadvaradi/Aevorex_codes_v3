"""
Network Helper Functions
========================

Centralized network utilities for the FinanceHub application.
Consolidated from network_ops and network_utils modules.
"""

import logging
from typing import Any
import uuid

import httpx
from fastapi import Request

try:
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

# --- Constants ---
FETCH_FAILED_MARKER: str = "FETCH_FAILED_V1"


# --- Network Operations Section ---


async def make_api_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    *,
    source_name_for_log: str,
    params: dict[str, Any] | None = None,
    headers: dict[str, Any] | None = None,
    cache_service: CacheService | None = None,
    cache_key_for_failure: str | None = None,
    http_timeout: float = 30.0,
    cache_enabled: bool = True,
    fetch_failure_cache_ttl: int = 600,
) -> dict[str, Any] | None:
    """
    Általános API kérés végrehajtása cache támogatással.
    """
    log_prefix = f"[{source_name_for_log}]"

    try:
        package_logger.info(f"{log_prefix} Making {method} request to {url}")

        response = await client.request(
            method=method,
            url=url,
            params=params,
            headers=headers,
            timeout=http_timeout,
        )

        response.raise_for_status()
        data = response.json()

        package_logger.info(
            f"{log_prefix} Request successful, got {len(str(data))} chars"
        )
        return data

    except httpx.HTTPStatusError as e:
        package_logger.error(f"{log_prefix} HTTP error {e.response.status_code}: {e}")

        # Cache failure marker if cache service available
        if cache_enabled and cache_service and cache_key_for_failure:
            try:
                await cache_service.set(
                    cache_key_for_failure, FETCH_FAILED_MARKER, fetch_failure_cache_ttl
                )
            except Exception as cache_error:
                package_logger.warning(
                    f"{log_prefix} Failed to cache failure marker: {cache_error}"
                )

        return None

    except httpx.TimeoutException:
        package_logger.error(f"{log_prefix} Request timeout after {http_timeout}s")
        return None

    except Exception as e:
        package_logger.error(f"{log_prefix} Unexpected error: {e}")
        return None


# --- Network Utilities Section ---


def get_request_id(request: Request | None = None) -> str:
    """
    Lekéri a request ID-t a request-ből vagy generál egy újat.
    """
    if request and hasattr(request, "state") and hasattr(request.state, "request_id"):
        return request.state.request_id

    return str(uuid.uuid4())


def get_user_id(request: Request | None = None) -> str | None:
    """
    Lekéri a user ID-t a request-ből.
    """
    if not request:
        return None

    if hasattr(request, "state") and hasattr(request.state, "user_id"):
        return request.state.user_id

    return None


def get_default_headers(request: Request | None = None) -> dict[str, str]:
    """
    Lekéri az alapértelmezett HTTP header-eket.
    """
    headers = {
        "User-Agent": "FinanceHub-API/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    if request:
        request_id = get_request_id(request)
        headers["X-Request-ID"] = request_id

        user_id = get_user_id(request)
        if user_id:
            headers["X-User-ID"] = user_id

    return headers

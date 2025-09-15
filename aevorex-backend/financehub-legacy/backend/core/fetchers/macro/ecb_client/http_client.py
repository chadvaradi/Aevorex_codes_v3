"""
ECB SDMX HTTP Client
===================

HTTP client for ECB SDMX API requests with retry logic and error handling.
"""

import json
import time
import logging
from datetime import date
from typing import Any, Dict, Optional

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from .config import ECB_BASE_URL, ECB_REQUEST_HEADERS, ECB_TIMEOUT, ECB_RETRY_ATTEMPTS
from .exceptions import (
    ECBAPIError,
    ECBConnectionError,
    ECBTimeoutError,
    ECBRateLimitError,
)
from backend.core.metrics import METRICS_EXPORTER

logger = logging.getLogger(__name__)


class ECBHTTPClient:
    """
    HTTP client for ECB SDMX API requests.

    Handles request construction, retry logic, and error handling.
    """

    def __init__(self, timeout: int = ECB_TIMEOUT):
        self.timeout = timeout
        self.base_url = ECB_BASE_URL
        self.headers = ECB_REQUEST_HEADERS.copy()

    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        stop=stop_after_attempt(ECB_RETRY_ATTEMPTS),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.RequestError)),
        reraise=True,
    )
    async def download_ecb_sdmx(
        self, dataflow: str, filter_key: str, start: date, end: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Download data from ECB SDMX-JSON API.

        Args:
            dataflow: ECB dataflow identifier
            filter_key: SDMX series key filter
            start: Start date for data
            end: End date for data (optional)

        Returns:
            JSON response as dictionary

        Raises:
            ECBAPIError: When API request fails
            ECBConnectionError: When connection fails
            ECBTimeoutError: When request times out
        """
        url = f"{self.base_url}/{dataflow}/{filter_key}"

        # Build URL parameters
        params = {
            "startPeriod": start.isoformat(),
            "detail": "dataonly",
            "format": "jsondata",
        }

        if end:
            params["endPeriod"] = end.isoformat()

        logger.info(f"Requesting ECB data from: {url} with params: {params}")

        start_time = time.monotonic()

        try:
            async with httpx.AsyncClient(
                timeout=self.timeout, headers=self.headers
            ) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()

                duration = time.monotonic() - start_time
                METRICS_EXPORTER.observe_ecb_request(duration)

                return response.json()

        except httpx.TimeoutException as e:
            duration = time.monotonic() - start_time
            METRICS_EXPORTER.observe_ecb_request(duration)

            logger.error(f"ECB API request timed out after {duration:.2f}s")
            raise ECBTimeoutError(
                f"ECB API request timed out after {duration:.2f}s", duration
            ) from e

        except httpx.HTTPStatusError as e:
            duration = time.monotonic() - start_time
            METRICS_EXPORTER.observe_ecb_request(duration)

            error_text = e.response.text
            logger.error(
                f"HTTP error fetching ECB data: {e.response.status_code} - {error_text}"
            )

            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                raise ECBRateLimitError(
                    f"ECB API rate limit exceeded: {error_text}",
                    int(retry_after) if retry_after else None,
                ) from e

            raise ECBAPIError(
                f"HTTP error fetching ECB data: {e.response.status_code} - {error_text}",
                e.response.status_code,
                error_text,
            ) from e

        except httpx.RequestError as e:
            duration = time.monotonic() - start_time
            METRICS_EXPORTER.observe_ecb_request(duration)

            logger.error(f"Request error fetching ECB data: {e}")
            raise ECBConnectionError(f"Request error fetching ECB data: {e}", e) from e

        except json.JSONDecodeError as e:
            duration = time.monotonic() - start_time
            METRICS_EXPORTER.observe_ecb_request(duration)

            logger.error(f"Failed to decode JSON from ECB response: {e}")
            raise ECBAPIError(f"Failed to decode JSON from ECB response: {e}") from e

    async def health_check(self) -> bool:
        """
        Check if ECB API is accessible.

        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Simple health check using a minimal request
            from datetime import datetime, timedelta

            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=1)

            await self.download_ecb_sdmx(
                "FM", "B.U2.EUR.4F.KR.MRR_FR.LEV", start_date, end_date
            )

            logger.info("ECB API health check passed")
            return True

        except Exception as e:
            logger.warning(f"ECB API health check failed: {e}")
            return False

    def update_headers(self, headers: Dict[str, str]):
        """
        Update HTTP headers for requests.

        Args:
            headers: Dictionary of headers to update
        """
        self.headers.update(headers)
        logger.debug(f"Updated ECB HTTP client headers: {headers}")

    def set_timeout(self, timeout: int):
        """
        Set request timeout.

        Args:
            timeout: Timeout in seconds
        """
        self.timeout = timeout
        logger.debug(f"Updated ECB HTTP client timeout to {timeout}s")

    async def close(self):
        """
        Close the HTTP client.

        Note: This client uses context managers for connections,
        so no persistent connections need to be closed.
        """
        logger.debug("ECB HTTP client close called (no-op)")

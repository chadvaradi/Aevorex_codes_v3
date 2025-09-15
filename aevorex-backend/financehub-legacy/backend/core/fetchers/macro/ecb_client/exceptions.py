"""
ECB SDMX Client Exceptions
==========================

Custom exceptions for ECB SDMX client operations.
"""

import logging

logger = logging.getLogger(__name__)


class ECBAPIError(Exception):
    """
    Custom exception for ECB API errors.

    Raised when there are issues with ECB SDMX API requests or responses.
    """

    def __init__(
        self, message: str, status_code: int = None, response_text: str = None
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

        # Log the error
        if status_code:
            logger.error(f"ECB API Error [{status_code}]: {message}")
        else:
            logger.error(f"ECB API Error: {message}")

    def __str__(self):
        if self.status_code:
            return f"ECB API Error [{self.status_code}]: {super().__str__()}"
        return f"ECB API Error: {super().__str__()}"


class ECBDataParsingError(Exception):
    """
    Exception raised when ECB SDMX data parsing fails.
    """

    def __init__(self, message: str, series_key: str = None):
        super().__init__(message)
        self.series_key = series_key

        logger.error(f"ECB Data Parsing Error: {message}")
        if series_key:
            logger.error(f"Series key: {series_key}")


class ECBConnectionError(Exception):
    """
    Exception raised when ECB API connection fails.
    """

    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(message)
        self.original_error = original_error

        logger.error(f"ECB Connection Error: {message}")
        if original_error:
            logger.error(f"Original error: {str(original_error)}")


class ECBTimeoutError(Exception):
    """
    Exception raised when ECB API request times out.
    """

    def __init__(self, message: str, timeout_duration: float = None):
        super().__init__(message)
        self.timeout_duration = timeout_duration

        logger.error(f"ECB Timeout Error: {message}")
        if timeout_duration:
            logger.error(f"Timeout duration: {timeout_duration}s")


class ECBRateLimitError(Exception):
    """
    Exception raised when ECB API rate limit is exceeded.
    """

    def __init__(self, message: str, retry_after: int = None):
        super().__init__(message)
        self.retry_after = retry_after

        logger.warning(f"ECB Rate Limit Error: {message}")
        if retry_after:
            logger.warning(f"Retry after: {retry_after}s")

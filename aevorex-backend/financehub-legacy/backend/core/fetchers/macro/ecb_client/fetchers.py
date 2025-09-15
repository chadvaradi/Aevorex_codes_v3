"""
ECB Data Fetchers
================

High-level fetcher functions for ECB data with caching support.
"""

import logging
from datetime import date, timedelta
from typing import Dict, Optional

from .client import ECBSDMXClient
from .exceptions import ECBAPIError
from backend.utils.cache_service import CacheService

logger = logging.getLogger(__name__)


async def fetch_ecb_policy_rates(
    cache: CacheService,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch ECB policy rates with caching support.

    Args:
        cache: Cache service instance
        start_date: Start date for data (defaults to 30 days ago)
        end_date: End date for data (defaults to today)

    Returns:
        Dictionary with policy rates by date

    Raises:
        ECBAPIError: When fetching fails
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    cache_key = f"ecb_policy_rates_{start_date}_{end_date}"

    logger.info(f"Fetching ECB policy rates from {start_date} to {end_date}")

    try:
        # Try to get from cache first
        if cache:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Retrieved ECB policy rates from cache")
                return cached_data

        # Fetch from ECB API
        client = ECBSDMXClient(cache)

        try:
            data = await client.get_policy_rates(start_date, end_date)

            # Cache the result for 1 hour
            if cache and data:
                await cache.set(cache_key, data, ttl=3600)
                logger.debug("Cached ECB policy rates data")

            return data

        finally:
            await client.close()

    except Exception as e:
        logger.error(f"Error fetching ECB policy rates: {e}")
        raise ECBAPIError(f"Error fetching ECB policy rates: {e}") from e


async def fetch_ecb_fx_rates(
    cache: CacheService,
    currency_pair: str = "USD+GBP+JPY+CHF",
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch ECB FX rates with caching support.

    Args:
        cache: Cache service instance
        currency_pair: Currency pair string (e.g., 'USD+GBP+JPY+CHF')
        start_date: Start date for data (defaults to 30 days ago)
        end_date: End date for data (defaults to today)

    Returns:
        Dictionary with FX rates by date and currency

    Raises:
        ECBAPIError: When fetching fails
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    cache_key = f"ecb_fx_rates_{currency_pair}_{start_date}_{end_date}"

    logger.info(
        f"Fetching ECB FX rates for {currency_pair} from {start_date} to {end_date}"
    )

    try:
        # Try to get from cache first
        if cache:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Retrieved ECB FX rates from cache")
                return cached_data

        # Fetch from ECB API
        client = ECBSDMXClient(cache)

        try:
            data = await client.get_fx_rates(start_date, end_date)

            # Cache the result for 1 hour
            if cache and data:
                await cache.set(cache_key, data, ttl=3600)
                logger.debug("Cached ECB FX rates data")

            return data

        finally:
            await client.close()

    except Exception as e:
        logger.error(f"Error fetching ECB FX rates: {e}")

        # -----------------------------------------------------------------
        # Fallback: return cached data if available (stale-while-revalidate)
        # -----------------------------------------------------------------
        if cache:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.warning(
                    "Returning STALE ECB FX rates from cache due to fetch error"
                )
                return cached_data  # type: ignore[return-value]

        raise ECBAPIError(f"Error fetching ECB FX rates: {e}") from e


async def fetch_ecb_yield_curve(
    cache: CacheService,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch ECB yield curve data with caching support.

    Args:
        cache: Cache service instance
        start_date: Start date for data (defaults to 30 days ago)
        end_date: End date for data (defaults to today)

    Returns:
        Dictionary with yield curve data by date and maturity

    Raises:
        ECBAPIError: When fetching fails
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    cache_key = f"ecb_yield_curve_{start_date}_{end_date}"

    logger.info(f"Fetching ECB yield curve from {start_date} to {end_date}")

    try:
        # Try to get from cache first
        if cache:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Retrieved ECB yield curve from cache")
                return cached_data

        # Fetch from ECB API
        client = ECBSDMXClient(cache)

        try:
            data = await client.get_yield_curve(start_date, end_date)

            # Cache the result for 1 hour
            if cache and data:
                await cache.set(cache_key, data, ttl=3600)
                logger.debug("Cached ECB yield curve data")

            return data

        finally:
            await client.close()

    except Exception as e:
        logger.error(f"Error fetching ECB yield curve: {e}")
        raise ECBAPIError(f"Error fetching ECB yield curve: {e}") from e


async def fetch_ecb_comprehensive_data(
    cache: CacheService,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Fetch comprehensive ECB economic data with caching support.

    Args:
        cache: Cache service instance
        start_date: Start date for data (defaults to 1 year ago)
        end_date: End date for data (defaults to today)

    Returns:
        Dictionary with comprehensive economic data by category

    Raises:
        ECBAPIError: When fetching fails
    """
    if not start_date:
        start_date = date.today() - timedelta(days=365)
    if not end_date:
        end_date = date.today()

    cache_key = f"ecb_comprehensive_{start_date}_{end_date}"

    logger.info(f"Fetching comprehensive ECB data from {start_date} to {end_date}")

    try:
        # Try to get from cache first
        if cache:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Retrieved comprehensive ECB data from cache")
                return cached_data

        # Fetch from ECB API
        client = ECBSDMXClient(cache)

        try:
            data = await client.get_comprehensive_economic_data(start_date, end_date)

            # Cache the result for 4 hours (longer for comprehensive data)
            if cache and data:
                await cache.set(cache_key, data, ttl=14400)
                logger.debug("Cached comprehensive ECB data")

            return data

        finally:
            await client.close()

    except Exception as e:
        logger.error(f"Error fetching comprehensive ECB data: {e}")
        raise ECBAPIError(f"Error fetching comprehensive ECB data: {e}") from e


async def fetch_ecb_bop_data(
    cache: CacheService,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch ECB Balance of Payments data with caching support.

    Args:
        cache: Cache service instance
        start_date: Start date for data (defaults to 2 years ago)
        end_date: End date for data (defaults to today)

    Returns:
        Dictionary with BOP data by date and component

    Raises:
        ECBAPIError: When fetching fails
    """
    if not start_date:
        start_date = date.today() - timedelta(days=730)  # 2 years for quarterly data
    if not end_date:
        end_date = date.today()

    cache_key = f"ecb_bop_{start_date}_{end_date}"

    logger.info(f"Fetching ECB BOP data from {start_date} to {end_date}")

    try:
        # Try to get from cache first
        if cache:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Retrieved ECB BOP data from cache")
                return cached_data

        # Fetch from ECB API
        client = ECBSDMXClient(cache)

        try:
            data = await client.get_bop_data(start_date, end_date)

            # Cache the result for 6 hours (quarterly data updates less frequently)
            if cache and data:
                await cache.set(cache_key, data, ttl=21600)
                logger.debug("Cached ECB BOP data")

            return data

        finally:
            await client.close()

    except Exception as e:
        logger.error(f"Error fetching ECB BOP data: {e}")
        raise ECBAPIError(f"Error fetching ECB BOP data: {e}") from e


async def fetch_ecb_sts_data(
    cache: CacheService,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch ECB Short-term Statistics data with caching support.

    Args:
        cache: Cache service instance
        start_date: Start date for data (defaults to 1 year ago)
        end_date: End date for data (defaults to today)

    Returns:
        Dictionary with STS data by date and indicator

    Raises:
        ECBAPIError: When fetching fails
    """
    if not start_date:
        start_date = date.today() - timedelta(days=365)
    if not end_date:
        end_date = date.today()

    cache_key = f"ecb_sts_{start_date}_{end_date}"

    logger.info(f"Fetching ECB STS data from {start_date} to {end_date}")

    try:
        # Try to get from cache first
        if cache:
            cached_data = await cache.get(cache_key)
            if cached_data:
                logger.debug("Retrieved ECB STS data from cache")
                return cached_data

        # Fetch from ECB API
        client = ECBSDMXClient(cache)

        try:
            data = await client.get_sts_data(start_date, end_date)
        except Exception as inner_exc:
            logger.error("ECB STS series fetch failed: %s", inner_exc, exc_info=True)
            # Graceful degradation – return empty dict so API can respond with
            # structured status:error payload instead of HTTP 500.
            data = {}

        # Cache the result for 4 hours (monthly data) **only** if we obtained data.
        if cache and data:
            await cache.set(cache_key, data, ttl=14400)
            logger.debug("Cached ECB STS data")

        return data

    finally:
        # Ensure underlying HTTP session is properly closed even when errors occur
        await client.close()

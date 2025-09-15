"""
ECB Policy Rates fetcher for key ECB interest rates.
Fetches Deposit Facility Rate, Main Refinancing Operations Rate, and Marginal Lending Facility Rate.
"""

from datetime import date, timedelta
from typing import Optional, Dict, List
from backend.utils.logger_config import get_logger
from ..client import ECBSDMXClient
from ..exceptions import ECBAPIError

logger = get_logger(__name__)

# FM dataflow keys for ECB policy rates
POLICY_RATES_SERIES_KEYS = {
    "DFR": "D.EZB.DFR.LEV",  # Deposit Facility Rate
    "MRO": "D.EZB.MRO.LEV",  # Main Refinancing Operations Rate
    "MSF": "D.EZB.MSF.LEV",  # Marginal Lending Facility Rate
}

# Policy rate descriptions
POLICY_RATES_INFO = {
    "DFR": {
        "name": "Deposit Facility Rate",
        "description": "Rate on overnight deposits by banks with the ECB",
        "symbol": "ECB_DFR",
    },
    "MRO": {
        "name": "Main Refinancing Operations Rate",
        "description": "Main policy rate for weekly refinancing operations",
        "symbol": "ECB_MRO",
    },
    "MSF": {
        "name": "Marginal Lending Facility Rate",
        "description": "Rate for overnight lending to banks by the ECB",
        "symbol": "ECB_MSF",
    },
}


async def fetch_policy_rates(
    cache_service=None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    rates: Optional[List[str]] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch ECB policy rates from ECB FM dataflow.

    Args:
        cache_service: Cache service instance (can be None for no caching)
        start_date: Start date for historical data
        end_date: End date for historical data
        rates: List of rates to fetch (DFR, MRO, MSF) - default: all

    Returns:
        Dict with date keys and policy rates
        Format: {
            "2025-08-01": {
                "DFR": 4.00,
                "MRO": 4.25,
                "MSF": 4.50
            }
        }
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=90)  # 3 months default for policy rates

    if not rates:
        rates = list(POLICY_RATES_SERIES_KEYS.keys())

    logger.info(f"Fetching policy rates {rates} from {start_date} to {end_date}")

    try:
        client = ECBSDMXClient()

        # Validate requested rates
        for rate in rates:
            if rate not in POLICY_RATES_SERIES_KEYS:
                logger.warning(f"Unknown policy rate: {rate}")

        # Fetch data from ECB SDMX API
        policy_data = await client.get_policy_rates(start_date, end_date)

        if not policy_data:
            logger.warning("No policy rates data received from ECB")
            return {}

        # Filter for requested rates (policy_data already in correct format)
        result = {}
        for date_str, rate_data in policy_data.items():
            filtered_data = {}
            for rate in rates:
                if rate in rate_data:
                    filtered_data[rate] = rate_data[rate]

            if filtered_data:
                result[date_str] = filtered_data

        logger.info(f"Successfully fetched policy rates data for {len(result)} dates")

        # Cache the result if cache service is available
        if cache_service and result:
            cache_key = f"ecb_policy_rates_{start_date}_{end_date}_{'_'.join(rates)}"
            try:
                await cache_service.set(
                    cache_key, result, ttl=1800
                )  # 30 min TTL (rates change rarely)
                logger.debug(f"Cached policy rates data with key: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to cache policy rates data: {e}")

        return result

    except ECBAPIError as e:
        logger.error(f"ECB API error fetching policy rates data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching policy rates data: {e}")
        raise ECBAPIError(f"Failed to fetch policy rates data: {str(e)}")


async def fetch_single_policy_rate(
    rate_type: str,
    cache_service=None,
    target_date: Optional[date] = None,
) -> Optional[float]:
    """
    Fetch a single policy rate for specific type and date.

    Args:
        rate_type: Rate type (DFR, MRO, MSF)
        cache_service: Cache service instance
        target_date: Specific date (default: latest available)

    Returns:
        Policy rate as float or None if not available
    """
    if not target_date:
        target_date = date.today()

    # Check if we have recent data in cache first
    if cache_service:
        cache_key = f"ecb_policy_{rate_type}_{target_date}"
        try:
            cached_rate = await cache_service.get(cache_key)
            if cached_rate is not None:
                logger.debug(
                    f"Retrieved cached policy rate for {rate_type}: {cached_rate}"
                )
                return float(cached_rate)
        except Exception as e:
            logger.debug(f"Cache lookup failed: {e}")

    # Fetch from API with small date range
    start_date = target_date - timedelta(days=30)  # Last month
    rates_data = await fetch_policy_rates(
        cache_service=cache_service,
        start_date=start_date,
        end_date=target_date,
        rates=[rate_type],
    )

    if not rates_data:
        return None

    # Find the most recent rate
    sorted_dates = sorted(rates_data.keys(), reverse=True)
    for obs_date in sorted_dates:
        if rate_type in rates_data[obs_date]:
            rate = rates_data[obs_date][rate_type]

            # Cache individual rate
            if cache_service:
                cache_key = f"ecb_policy_{rate_type}_{obs_date}"
                try:
                    await cache_service.set(cache_key, rate, ttl=1800)
                except Exception as e:
                    logger.debug(f"Failed to cache individual rate: {e}")

            return rate

    return None


async def fetch_current_policy_corridor(
    cache_service=None,
    target_date: Optional[date] = None,
) -> Optional[Dict[str, float]]:
    """
    Fetch the current ECB policy rate corridor (DFR, MRO, MSF).

    Args:
        cache_service: Cache service instance
        target_date: Specific date (default: today)

    Returns:
        Dict with all three policy rates or None if not available
        Format: {"DFR": 4.00, "MRO": 4.25, "MSF": 4.50}
    """
    if not target_date:
        target_date = date.today()

    # Fetch all rates at once for efficiency
    rates_data = await fetch_policy_rates(
        cache_service=cache_service,
        start_date=target_date - timedelta(days=30),
        end_date=target_date,
        rates=["DFR", "MRO", "MSF"],
    )

    if not rates_data:
        return None

    # Find the most recent complete set
    sorted_dates = sorted(rates_data.keys(), reverse=True)
    for obs_date in sorted_dates:
        date_rates = rates_data[obs_date]
        # Check if we have all three rates for this date
        if all(rate_type in date_rates for rate_type in ["DFR", "MRO", "MSF"]):
            return {
                "DFR": date_rates["DFR"],
                "MRO": date_rates["MRO"],
                "MSF": date_rates["MSF"],
                "date": obs_date,
            }

    return None

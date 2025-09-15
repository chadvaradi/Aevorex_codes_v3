"""
ECB Yield Curve (YC) data fetcher for Euro area government bond spot rates.
Fetches risk-free spot rates derived from Euro area government bonds using Svensson method.
"""

from datetime import date, timedelta
from typing import Optional, Dict, List
from backend.utils.logger_config import get_logger
from ..client import ECBSDMXClient
from ..exceptions import ECBAPIError

logger = get_logger(__name__)

# YC dataflow keys for Euro area spot rates
YIELD_CURVE_SERIES_KEYS = {
    "1Y": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_1Y",  # 1 Year spot rate
    "2Y": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y",  # 2 Year spot rate
    "5Y": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_5Y",  # 5 Year spot rate
    "10Y": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y",  # 10 Year spot rate
    "30Y": "B.U2.EUR.4F.G_N_A.SV_C_YM.SR_30Y",  # 30 Year spot rate
}


async def fetch_yield_curve_rates(
    cache_service=None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    maturities: Optional[List[str]] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch Euro area yield curve spot rates from ECB YC dataflow.

    Args:
        cache_service: Cache service instance (can be None for no caching)
        start_date: Start date for historical data
        end_date: End date for historical data
        maturities: List of maturities to fetch (default: all)

    Returns:
        Dict with date keys and yield curve rates by maturity
        Format: {
            "2025-08-01": {
                "1Y": 2.156,
                "2Y": 2.089,
                "5Y": 2.234,
                "10Y": 2.456,
                "30Y": 2.678
            }
        }
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)  # 30 days default for yield curve

    if not maturities:
        maturities = list(YIELD_CURVE_SERIES_KEYS.keys())

    logger.info(
        f"Fetching yield curve rates for maturities {maturities} from {start_date} to {end_date}"
    )

    try:
        client = ECBSDMXClient()

        # Fetch data from ECB SDMX API (this returns properly formatted data)
        yc_data = await client.get_yield_curve(start_date, end_date)

        if not yc_data:
            logger.warning("No yield curve data received from ECB")
            return {}

        # Filter for requested maturities
        result = {}
        for date_str, maturity_data in yc_data.items():
            filtered_data = {}
            for maturity in maturities:
                if maturity in maturity_data:
                    filtered_data[maturity] = maturity_data[maturity]

            if filtered_data:
                result[date_str] = filtered_data

        logger.info(f"Successfully fetched yield curve data for {len(result)} dates")

        # Cache the result if cache service is available
        if cache_service and result:
            cache_key = (
                f"ecb_yield_curve_{start_date}_{end_date}_{'_'.join(maturities)}"
            )
            try:
                await cache_service.set(cache_key, result, ttl=3600)  # 1 hour TTL
                logger.debug(f"Cached yield curve data with key: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to cache yield curve data: {e}")

        return result

    except ECBAPIError as e:
        logger.error(f"ECB API error fetching yield curve data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching yield curve data: {e}")
        raise ECBAPIError(f"Failed to fetch yield curve data: {str(e)}")


async def fetch_single_yield_rate(
    maturity: str,
    cache_service=None,
    target_date: Optional[date] = None,
) -> Optional[float]:
    """
    Fetch a single yield curve rate for specific maturity and date.

    Args:
        maturity: Maturity (1Y, 2Y, 5Y, 10Y, 30Y)
        cache_service: Cache service instance
        target_date: Specific date (default: latest available)

    Returns:
        Yield rate as float or None if not available
    """
    if not target_date:
        target_date = date.today()

    # Check if we have recent data in cache first
    if cache_service:
        cache_key = f"ecb_yield_{maturity}_{target_date}"
        try:
            cached_rate = await cache_service.get(cache_key)
            if cached_rate is not None:
                logger.debug(
                    f"Retrieved cached yield rate for {maturity}: {cached_rate}"
                )
                return float(cached_rate)
        except Exception as e:
            logger.debug(f"Cache lookup failed: {e}")

    # Fetch from API with small date range
    start_date = target_date - timedelta(days=7)  # Last week
    rates_data = await fetch_yield_curve_rates(
        cache_service=cache_service,
        start_date=start_date,
        end_date=target_date,
        maturities=[maturity],
    )

    if not rates_data:
        return None

    # Find the most recent rate
    sorted_dates = sorted(rates_data.keys(), reverse=True)
    for obs_date in sorted_dates:
        if maturity in rates_data[obs_date]:
            rate = rates_data[obs_date][maturity]

            # Cache individual rate
            if cache_service:
                cache_key = f"ecb_yield_{maturity}_{obs_date}"
                try:
                    await cache_service.set(cache_key, rate, ttl=3600)
                except Exception as e:
                    logger.debug(f"Failed to cache individual rate: {e}")

            return rate

    return None

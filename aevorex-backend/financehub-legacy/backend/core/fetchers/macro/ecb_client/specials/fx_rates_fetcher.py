"""
ECB FX Rates fetcher for EUR reference exchange rates.
Fetches official ECB reference exchange rates vs EUR from EXR dataflow.
"""

from datetime import date, timedelta
from typing import Optional, Dict, List
from backend.utils.logger_config import get_logger
from ..client import ECBSDMXClient
from ..exceptions import ECBAPIError

logger = get_logger(__name__)

# EXR dataflow keys for major currencies vs EUR
FX_RATES_SERIES_KEYS = {
    "USD": "D.USD.EUR.SP00.A",  # USD/EUR daily reference rate
    "GBP": "D.GBP.EUR.SP00.A",  # GBP/EUR daily reference rate
    "HUF": "D.HUF.EUR.SP00.A",  # HUF/EUR daily reference rate
    "CHF": "D.CHF.EUR.SP00.A",  # CHF/EUR daily reference rate
    "JPY": "D.JPY.EUR.SP00.A",  # JPY/EUR daily reference rate
    "CAD": "D.CAD.EUR.SP00.A",  # CAD/EUR daily reference rate
    "AUD": "D.AUD.EUR.SP00.A",  # AUD/EUR daily reference rate
    "SEK": "D.SEK.EUR.SP00.A",  # SEK/EUR daily reference rate
    "NOK": "D.NOK.EUR.SP00.A",  # NOK/EUR daily reference rate
    "DKK": "D.DKK.EUR.SP00.A",  # DKK/EUR daily reference rate
    "PLN": "D.PLN.EUR.SP00.A",  # PLN/EUR daily reference rate
    "CZK": "D.CZK.EUR.SP00.A",  # CZK/EUR daily reference rate
}

# Priority currencies for FinanceHub
PRIORITY_CURRENCIES = ["USD", "HUF", "GBP", "CHF", "JPY"]


async def fetch_fx_rates(
    cache_service=None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    currencies: Optional[List[str]] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch ECB FX reference rates from ECB EXR dataflow.

    Args:
        cache_service: Cache service instance (can be None for no caching)
        start_date: Start date for historical data
        end_date: End date for historical data
        currencies: List of currencies to fetch (default: priority currencies)

    Returns:
        Dict with date keys and FX rates
        Format: {
            "2025-08-01": {
                "USD": 1.0825,
                "HUF": 389.45,
                "GBP": 0.8567
            }
        }
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=14)  # 2 weeks default for FX rates

    if not currencies:
        currencies = PRIORITY_CURRENCIES

    logger.info(f"Fetching FX rates for {currencies} from {start_date} to {end_date}")

    try:
        client = ECBSDMXClient()

        # Validate requested currencies
        for currency in currencies:
            if currency not in FX_RATES_SERIES_KEYS:
                logger.warning(f"Unknown currency: {currency}")

        # Fetch data from ECB SDMX API
        fx_data = await client.get_fx_rates(start_date, end_date)

        if not fx_data:
            logger.warning("No FX rates data received from ECB")
            return {}

        # Filter for requested currencies (fx_data already in correct format)
        result = {}
        for date_str, currency_data in fx_data.items():
            filtered_data = {}
            for currency in currencies:
                if currency in currency_data:
                    filtered_data[currency] = currency_data[currency]

            if filtered_data:
                result[date_str] = filtered_data

        logger.info(f"Successfully fetched FX rates data for {len(result)} dates")

        # Cache the result if cache service is available
        if cache_service and result:
            cache_key = f"ecb_fx_rates_{start_date}_{end_date}_{'_'.join(currencies)}"
            try:
                await cache_service.set(cache_key, result, ttl=1800)  # 30 min TTL
                logger.debug(f"Cached FX rates data with key: {cache_key}")
            except Exception as e:
                logger.warning(f"Failed to cache FX rates data: {e}")

        return result

    except ECBAPIError as e:
        logger.error(f"ECB API error fetching FX rates data: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching FX rates data: {e}")
        raise ECBAPIError(f"Failed to fetch FX rates data: {str(e)}")


async def fetch_single_fx_rate(
    currency: str,
    cache_service=None,
    target_date: Optional[date] = None,
) -> Optional[float]:
    """
    Fetch a single FX rate for specific currency and date.

    Args:
        currency: Currency code (USD, HUF, GBP, etc.)
        cache_service: Cache service instance
        target_date: Specific date (default: latest available)

    Returns:
        FX rate as float or None if not available
    """
    if not target_date:
        target_date = date.today()

    # Check if we have recent data in cache first
    if cache_service:
        cache_key = f"ecb_fx_{currency}_{target_date}"
        try:
            cached_rate = await cache_service.get(cache_key)
            if cached_rate is not None:
                logger.debug(f"Retrieved cached FX rate for {currency}: {cached_rate}")
                return float(cached_rate)
        except Exception as e:
            logger.debug(f"Cache lookup failed: {e}")

    # Fetch from API with small date range
    start_date = target_date - timedelta(days=7)  # Last week
    rates_data = await fetch_fx_rates(
        cache_service=cache_service,
        start_date=start_date,
        end_date=target_date,
        currencies=[currency],
    )

    if not rates_data:
        return None

    # Find the most recent rate
    sorted_dates = sorted(rates_data.keys(), reverse=True)
    for obs_date in sorted_dates:
        if currency in rates_data[obs_date]:
            rate = rates_data[obs_date][currency]

            # Cache individual rate
            if cache_service:
                cache_key = f"ecb_fx_{currency}_{obs_date}"
                try:
                    await cache_service.set(cache_key, rate, ttl=1800)
                except Exception as e:
                    logger.debug(f"Failed to cache individual rate: {e}")

            return rate

    return None


async def fetch_major_fx_rates(
    cache_service=None,
    target_date: Optional[date] = None,
) -> Optional[Dict[str, float]]:
    """
    Fetch major FX rates (USD, HUF, GBP) for specific date.

    Args:
        cache_service: Cache service instance
        target_date: Specific date (default: today)

    Returns:
        Dict with major FX rates or None if not available
        Format: {"USD": 1.0825, "HUF": 389.45, "GBP": 0.8567}
    """
    if not target_date:
        target_date = date.today()

    # Fetch priority currencies
    rates_data = await fetch_fx_rates(
        cache_service=cache_service,
        start_date=target_date - timedelta(days=7),
        end_date=target_date,
        currencies=PRIORITY_CURRENCIES,
    )

    if not rates_data:
        return None

    # Find the most recent complete set
    sorted_dates = sorted(rates_data.keys(), reverse=True)
    for obs_date in sorted_dates:
        date_rates = rates_data[obs_date]
        # Return the first date that has data (even if not all currencies)
        if date_rates:
            result = dict(date_rates)
            result["date"] = obs_date
            return result

    return None


async def convert_currency(
    from_currency: str,
    to_currency: str,
    amount: float,
    cache_service=None,
    target_date: Optional[date] = None,
) -> Optional[float]:
    """
    Convert amount from one currency to another using ECB reference rates.

    Args:
        from_currency: Source currency (EUR or other)
        to_currency: Target currency (EUR or other)
        amount: Amount to convert
        cache_service: Cache service instance
        target_date: Rate date (default: today)

    Returns:
        Converted amount or None if rates not available
    """
    if from_currency == to_currency:
        return amount

    if not target_date:
        target_date = date.today()

    # Handle EUR as base currency
    if from_currency == "EUR":
        # EUR to other currency
        rate = await fetch_single_fx_rate(to_currency, cache_service, target_date)
        if rate:
            return amount * rate
    elif to_currency == "EUR":
        # Other currency to EUR
        rate = await fetch_single_fx_rate(from_currency, cache_service, target_date)
        if rate:
            return amount / rate
    else:
        # Cross-currency conversion via EUR
        from_rate = await fetch_single_fx_rate(
            from_currency, cache_service, target_date
        )
        to_rate = await fetch_single_fx_rate(to_currency, cache_service, target_date)
        if from_rate and to_rate:
            eur_amount = amount / from_rate  # Convert to EUR first
            return eur_amount * to_rate  # Then to target currency

    return None

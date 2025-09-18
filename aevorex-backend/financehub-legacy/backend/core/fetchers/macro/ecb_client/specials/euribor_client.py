"""
Official Euribor rates fetcher using web scraping from euribor-rates.eu
Provides EMMI-compliant Euribor fixing rates with T+1 delay.
License-clean alternative to API dependencies.
"""

import os
from datetime import date
from typing import Optional, Dict, List
from backend.utils.logger_config import get_logger
from .euribor_scraper import fetch_euribor_rates_from_web

logger = get_logger(__name__)

# Euribor maturity mapping for backward compatibility
EURIBOR_RATE_NAMES = {
    "1W": "euribor_1_week",
    "1M": "euribor_1_month",
    "3M": "euribor_3_months",
    "6M": "euribor_6_months",
    "12M": "euribor_12_months",
}


class EuriborClientError(Exception):
    """Raised when Euribor data cannot be fetched"""

    pass


async def fetch_official_euribor_rates(
    cache_service=None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tenors: Optional[List[str]] = None,
    demo_mode: bool = False,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch official Euribor fixing rates from euribor-rates.eu (web scraping).
    EMMI-compliant with T+1 delay, license-clean alternative to API dependencies.

    Args:
        cache_service: Optional cache service for caching results
        start_date: Start date for historical data (optional)
        end_date: End date for data (defaults to today)
        tenors: List of tenors to fetch (defaults to all: 1W, 1M, 3M, 6M, 12M)
        demo_mode: If True, returns demo data for testing

    Returns:
        Dict with date -> tenor -> rate: {"2025-08-05": {"1W": 1.87, "1M": 1.911, ...}}

    Raises:
        EuriborClientError: If data cannot be scraped
    """
    # Demo mode for testing - returns static rates
    if demo_mode or os.getenv("EURIBOR_DEMO_MODE") == "true":
        logger.info("DEMO MODE: Returning static Euribor rates")
        demo_date = (end_date or date.today()).isoformat()
        return {
            demo_date: {
                "1W": 1.885,
                "1M": 1.886,
                "3M": 2.008,
                "6M": 2.075,
                "12M": 2.126,
            }
        }

    logger.info("Fetching official Euribor rates from euribor-rates.eu...")

    try:
        # Use the web scraper to get current rates
        result = await fetch_euribor_rates_from_web(
            cache_service=cache_service,
            start_date=start_date,
            end_date=end_date,
            tenors=tenors,
        )

        if not result:
            raise EuriborClientError("No Euribor rates could be scraped")

        # Normalize the scraped data
        normalized_result = {}
        for date_str, rates in result.items():
            normalized_rates = {}
            for tenor, rate in rates.items():
                try:
                    # Normalize rate value (remove %, convert to float)
                    if isinstance(rate, str):
                        cleaned_rate = rate.strip().rstrip('%').strip().replace(',', '.')
                        normalized_rates[tenor] = float(cleaned_rate)
                    else:
                        normalized_rates[tenor] = float(rate)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to normalize rate for {tenor}: {rate} - {e}")
                    continue
            
            if normalized_rates:
                normalized_result[date_str] = normalized_rates

        if not normalized_result:
            raise EuriborClientError("No valid Euribor rates could be parsed from scraped data")

        logger.info(f"Successfully fetched and normalized Euribor data for {len(normalized_result)} dates")
        return normalized_result

    except Exception as e:
        logger.error(f"Failed to fetch Euribor rates via web scraping: {e}")
        raise EuriborClientError(f"Euribor web scraping failed: {e}")


async def get_latest_euribor_rates(
    tenors: Optional[List[str]] = None,
) -> Dict[str, float]:
    """
    Get latest Euribor rates in legacy format for backward compatibility.
    Returns: {"1W": 1.87, "1M": 1.911, ...}
    """
    try:
        data = await fetch_official_euribor_rates(tenors=tenors)
        if data:
            # Get the latest date's rates
            latest_date = max(data.keys())
            latest_rates = data[latest_date]
            
            # Normalize the rates to ensure they are floats
            normalized_rates = {}
            for tenor, rate in latest_rates.items():
                try:
                    if isinstance(rate, str):
                        cleaned_rate = rate.strip().rstrip('%').strip().replace(',', '.')
                        normalized_rates[tenor] = float(cleaned_rate)
                    else:
                        normalized_rates[tenor] = float(rate)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Failed to normalize rate for {tenor}: {rate} - {e}")
                    continue
            
            if normalized_rates:
                logger.info(f"Successfully normalized {len(normalized_rates)} Euribor rates: {list(normalized_rates.keys())}")
                return normalized_rates
            else:
                logger.warning("No valid rates found after normalization")
                return {}
        else:
            logger.warning("No data returned from fetch_official_euribor_rates")
            return {}
    except Exception as e:
        logger.error(f"Failed to get latest Euribor rates: {e}")
        raise EuriborClientError(f"Failed to get latest rates: {e}")

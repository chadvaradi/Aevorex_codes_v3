# modules/financehub/backend/core/fetchers/macro/ecb_client/euribor_scraper.py
"""
Euribor rates web scraper from euribor-rates.eu
Provides official EMMI-compliant Euribor fixing rates with T+1 delay.
License-clean alternative to API Ninjas.
"""

import httpx
from datetime import date, timedelta
from typing import Dict, Optional, List
from bs4 import BeautifulSoup
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

# Official Euribor rate URL (T+1 delayed, EMMI compliant)
EURIBOR_URL = "https://www.euribor-rates.eu/en/current-euribor-rates/"

# Euribor maturity mapping
EURIBOR_MATURITY_MAP = {
    "1W": "1 week",
    "1M": "1 month",
    "3M": "3 months",
    "6M": "6 months",
    "12M": "12 months",
}


class EuriborScrapingError(Exception):
    """Raised when Euribor scraping fails"""

    pass


async def fetch_euribor_rates_from_web(
    cache_service=None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    tenors: Optional[List[str]] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch current Euribor rates from euribor-rates.eu
    Returns data in format: {date_str: {tenor: rate_value}}
    """
    if not tenors:
        tenors = list(EURIBOR_MATURITY_MAP.keys())

    if not end_date:
        end_date = date.today()

    logger.info(f"Fetching Euribor rates from web for tenors: {tenors}")

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                EURIBOR_URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (FinanceHub Bot) AppleWebKit/537.36"
                },
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Find the rates table
            rates_table = soup.find("table")
            if not rates_table:
                raise EuriborScrapingError("Could not find rates table on webpage")

            # Extract current rates
            current_rates = {}
            rows = rates_table.find_all("tr")

            for row in rows[1:]:  # Skip header row
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    # First cell contains the maturity text
                    maturity_cell = cells[0]
                    rate_cell = cells[1]  # Most recent rate (today's column)

                    # Extract maturity from text
                    maturity_text = maturity_cell.get_text(strip=True)
                    rate_text = rate_cell.get_text(strip=True)

                    logger.debug(f"Processing row: '{maturity_text}' -> '{rate_text}'")

                    # Find matching tenor
                    for tenor, description in EURIBOR_MATURITY_MAP.items():
                        if description.lower() in maturity_text.lower():
                            try:
                                # Extract rate value (remove % sign and spaces)
                                rate_value = float(
                                    rate_text.replace("%", "").replace(" ", "").strip()
                                )
                                current_rates[tenor] = rate_value
                                logger.debug(f"✅ Parsed {tenor}: {rate_value}%")
                                break
                            except (ValueError, AttributeError) as e:
                                logger.warning(
                                    f"Could not parse rate for {tenor}: '{rate_text}' - {e}"
                                )
                    else:
                        logger.debug(f"No matching tenor found for: '{maturity_text}'")

            if not current_rates:
                raise EuriborScrapingError(
                    "No Euribor rates could be parsed from webpage"
                )

            logger.info(f"Successfully scraped {len(current_rates)} Euribor rates")

            # Create result with requested date range (T+1 delayed data)
            result = {}
            current_date = start_date or (end_date - timedelta(days=7))

            # For simplicity, use the latest rate for the requested date range
            # In production, you might want to scrape historical data or use the same rate
            latest_business_day = end_date
            # Adjust for weekends (Euribor is not published on weekends)
            while latest_business_day.weekday() >= 5:  # Saturday=5, Sunday=6
                latest_business_day -= timedelta(days=1)

            # Filter only requested tenors
            filtered_rates = {k: v for k, v in current_rates.items() if k in tenors}

            if filtered_rates:
                result[latest_business_day.isoformat()] = filtered_rates

            # Cache the result
            if cache_service and result:
                cache_key = f"euribor_web_rates_{end_date.isoformat()}"
                try:
                    await cache_service.set(cache_key, result, ttl=3600)  # 1 hour cache
                    logger.debug(f"Cached Euribor rates with key: {cache_key}")
                except Exception as e:
                    logger.warning(f"Failed to cache Euribor rates: {e}")

            return result

    except httpx.RequestError as e:
        logger.error(f"HTTP error fetching Euribor rates: {e}")
        raise EuriborScrapingError(f"Failed to fetch Euribor webpage: {e}")
    except Exception as e:
        logger.error(f"Unexpected error scraping Euribor rates: {e}")
        raise EuriborScrapingError(f"Euribor scraping failed: {e}")


async def get_latest_euribor_rate(tenor: str) -> Optional[float]:
    """Get single latest Euribor rate for specified tenor"""
    try:
        data = await fetch_euribor_rates_from_web(tenors=[tenor])
        if data:
            latest_date = max(data.keys())
            return data[latest_date].get(tenor)
        return None
    except Exception as e:
        logger.error(f"Failed to get latest {tenor} Euribor rate: {e}")
        return None

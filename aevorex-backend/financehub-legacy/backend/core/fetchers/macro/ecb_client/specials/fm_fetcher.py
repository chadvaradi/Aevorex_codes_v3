"""
ECB Financial Markets (FM) data fetcher for Euribor rates.
Fetches 1W and 1M Euribor daily fixings from ECB SDMX API.
"""

from datetime import date, timedelta
from typing import Optional, Dict
from backend.utils.logger_config import get_logger
from ..client import ECBSDMXClient
from ..exceptions import ECBAPIError

logger = get_logger(__name__)

# FM dataflow keys for Euribor rates
EURIBOR_SERIES_KEYS = {
    "1W": "D.U2.EUR.RT.MM.EURIBOR1WD_.LEV",  # 1 week daily fixing
    "1M": "D.U2.EUR.RT.MM.EURIBOR1MD_.LEV",  # 1 month daily fixing
}


async def fetch_euribor_rates(
    cache_service=None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
) -> Dict[str, Dict[str, float]]:
    """
    Fetch Euribor 1W and 1M daily fixing rates from ECB FM dataflow.

    Args:
        cache_service: Cache service instance (can be None for no caching)
        start_date: Start date for historical data
        end_date: End date for historical data

    Returns:
        Dict with date keys and Euribor rates by tenor
        Format: {
            "2025-08-01": {
                "1W": 1.885,
                "1M": 1.886
            }
        }
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=7)

    logger.info(f"Fetching Euribor rates from {start_date} to {end_date}")

    try:
        client = ECBSDMXClient()
        all_data = {}

        # Fetch each Euribor series
        for tenor, series_key in EURIBOR_SERIES_KEYS.items():
            logger.info(f"Fetching Euribor {tenor}: {series_key}")

            try:
                data = await client.fetch_series(
                    dataflow="FM",
                    key=series_key,
                    params={
                        "startPeriod": start_date.isoformat(),
                        "endPeriod": end_date.isoformat(),
                        "detail": "dataonly",
                        "format": "jsondata",
                    },
                )

                # Parse the data
                if data and "dataSets" in data and len(data["dataSets"]) > 0:
                    dataset = data["dataSets"][0]

                    if "observations" in dataset:
                        observations = dataset["observations"]
                        structure = data.get("structure", {})
                        dimensions = structure.get("dimensions", {}).get(
                            "observation", []
                        )

                        # Find time dimension
                        time_dim_index = None
                        for i, dim in enumerate(dimensions):
                            if dim.get("id") == "TIME_PERIOD":
                                time_dim_index = i
                                break

                        if time_dim_index is not None:
                            for obs_key, obs_value in observations.items():
                                if obs_value and len(obs_value) > 0:
                                    # Parse observation key (e.g., "0:0" -> date index)
                                    key_parts = obs_key.split(":")
                                    if len(key_parts) > time_dim_index:
                                        time_index = int(key_parts[time_dim_index])

                                        # Get date from structure
                                        if "attributes" in structure:
                                            time_values = None
                                            for attr in structure["attributes"].get(
                                                "observation", []
                                            ):
                                                if attr.get("id") == "TIME_PERIOD":
                                                    time_values = attr.get("values", [])
                                                    break

                                            if time_values and time_index < len(
                                                time_values
                                            ):
                                                obs_date = time_values[time_index]["id"]
                                                rate_value = float(obs_value[0])

                                                if obs_date not in all_data:
                                                    all_data[obs_date] = {}
                                                all_data[obs_date][tenor] = rate_value

                                                logger.info(
                                                    f"Retrieved Euribor {tenor}: {rate_value} for {obs_date}"
                                                )

            except Exception as e:
                logger.warning(f"Failed to fetch Euribor {tenor}: {e}")
                continue

        logger.info(f"Total Euribor data fetched: {len(all_data)} dates")
        return all_data

    except Exception as e:
        logger.error(f"Failed to fetch Euribor data: {e}")
        raise ECBAPIError(f"Euribor fetch failed: {e}")
    finally:
        if "client" in locals():
            await client.close()

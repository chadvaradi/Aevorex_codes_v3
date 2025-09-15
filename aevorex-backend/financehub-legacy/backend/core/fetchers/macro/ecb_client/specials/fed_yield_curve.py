# modules/financehub/backend/core/fetchers/macro/fed_yield_curve.py
import httpx
import pandas as pd
import io

# from backend.core.fetchers.common.base_fetcher import get_latest_from_to_df
from backend.utils.logger_config import get_logger

logger = get_logger(__name__)

# Official US Treasury daily yield curve data (always up-to-date)
DATA_URL = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2025/all?type=daily_treasury_yield_curve&field_tdr_date_value=2025&page&_format=csv"


class FedYieldCurveError(Exception):
    """Custom exception for FED yield curve fetcher."""


async def fetch_fed_policy_rates(
    series: list[str] = None,
    start_date: str = None,
    end_date: str = None
) -> dict:
    """
    Fetch Fed policy rates from FRED API.
    
    Args:
        series: List of FRED series symbols (e.g., ['EFFR', 'IORB', 'ONRRP']) or comma-separated string
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        Dictionary with policy rates data
    """
    import os
    from datetime import datetime, timedelta
    import httpx
    
    if not series:
        series = ["EFFR"]  # Default to Federal Funds Rate
    elif isinstance(series, str):
        # Handle string parameter by splitting on comma
        series = [s.strip() for s in series.split(",") if s.strip()]
    
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Get FRED API key from environment
    fred_api_key = os.getenv("FINBOT_API_KEYS__FRED")
    if not fred_api_key:
        logger.error("FRED API key not found in environment variables")
        return {"error": "FRED API key not configured"}
    
    try:
        logger.info(f"Fetching Fed policy rates for series: {series}")
        
        # FRED API base URL
        base_url = "https://api.stlouisfed.org/fred/series/observations"
        
        # Fetch data for each series
        all_data = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for series_id in series:
                try:
                    params = {
                        "series_id": series_id,
                        "api_key": fred_api_key,
                        "file_type": "json",
                        "observation_start": start_date,
                        "observation_end": end_date,
                        "sort_order": "desc",
                        "limit": 1000
                    }
                    
                    logger.info(f"Fetching {series_id} from FRED API")
                    response = await client.get(base_url, params=params)
                    
                    # Handle specific FRED API errors for individual series
                    if response.status_code == 400:
                        logger.warning(f"FRED API error: Series {series_id} not found or invalid (400)")
                        all_data[series_id] = {
                            "title": series_id,
                            "units": "Percent",
                            "frequency": "Daily",
                            "observations": [],
                            "error": "Series not found or invalid"
                        }
                        continue
                    elif response.status_code == 404:
                        logger.warning(f"FRED API error: Series {series_id} not found (404)")
                        all_data[series_id] = {
                            "title": series_id,
                            "units": "Percent",
                            "frequency": "Daily",
                            "observations": [],
                            "error": "Series not found"
                        }
                        continue
                    
                    response.raise_for_status()
                    data = response.json()
                    
                    if "observations" in data:
                        # Process observations
                        observations = []
                        for obs in data["observations"]:
                            if obs["value"] != ".":  # Skip missing values
                                observations.append({
                                    "date": obs["date"],
                                    "value": float(obs["value"])
                                })
                        
                        all_data[series_id] = {
                            "title": data.get("title", series_id),
                            "units": data.get("units", "Percent"),
                            "frequency": data.get("frequency", "Daily"),
                            "observations": observations
                        }
                        
                        logger.info(f"Successfully fetched {len(observations)} observations for {series_id}")
                    else:
                        logger.warning(f"No observations found for {series_id}")
                        all_data[series_id] = {
                            "title": series_id,
                            "units": "Percent",
                            "frequency": "Daily",
                            "observations": []
                        }
                except Exception as e:
                    logger.error(f"Error fetching {series_id}: {e}")
                    all_data[series_id] = {
                        "title": series_id,
                        "units": "Percent",
                        "frequency": "Daily",
                        "observations": [],
                        "error": f"Failed to fetch: {str(e)}"
                    }
        
        return {
            "status": "success",
            "source": "FRED",
            "series": all_data,
            "date_range": {
                "start": start_date,
                "end": end_date
            },
            "last_updated": datetime.now().isoformat()
        }
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching FRED data: {e.response.status_code}")
        return {"error": f"FRED API error: {e.response.status_code}"}
    except Exception as e:
        logger.error(f"Error fetching Fed policy rates: {e}", exc_info=True)
        return {"error": f"Failed to fetch Fed policy rates: {str(e)}"}


# async def fetch_fed_yield_curve_historical(start_date: date, end_date: date) -> list:
#     """
#     Fetch historical daily FED yield curve data from the Treasury.gov API.
#     """
#     return []


async def fetch_fed_yield_curve_historical() -> pd.DataFrame:
    """
    Fetches the entire historical U.S. Treasury yield curve data from the
    official US Treasury website as a pandas DataFrame.

    The data is the official Treasury daily yield curve data, always up-to-date.

    Returns:
        pd.DataFrame: A DataFrame with 'Date' as the index and Treasury
                      maturities as columns.
    """
    logger.info(
        "Fetching historical U.S. Treasury yield curve data from official Treasury website."
    )
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(DATA_URL)
            response.raise_for_status()

            # Read the CSV directly - Treasury CSV is well-formatted
            df = pd.read_csv(io.StringIO(response.text))

            # ------------------------------------------------------------------
            # 1) Normalise column names for official Treasury data
            # ------------------------------------------------------------------
            # Official Treasury CSV format: Date,"1 Mo","1.5 Month","2 Mo","3 Mo","4 Mo","6 Mo","1 Yr","2 Yr","3 Yr","5 Yr","7 Yr","10 Yr","20 Yr","30 Yr"
            rename_map = {
                "Date": "Date",
                "1 Mo": "1M",
                "1.5 Month": "1.5M",
                "2 Mo": "2M", 
                "3 Mo": "3M",
                "4 Mo": "4M",
                "6 Mo": "6M",
                "1 Yr": "1Y",
                "2 Yr": "2Y",
                "3 Yr": "3Y",
                "5 Yr": "5Y",
                "7 Yr": "7Y",
                "10 Yr": "10Y",
                "20 Yr": "20Y",
                "30 Yr": "30Y",
            }

            # Rename columns to standard format
            df.rename(columns=rename_map, inplace=True)

            # ------------------------------------------------------------------
            # 2) Keep only the standard maturity columns
            # ------------------------------------------------------------------
            KEEP_COLS = ["Date", "1M", "1.5M", "2M", "3M", "4M", "6M", "1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]
            present_cols = [c for c in KEEP_COLS if c in df.columns]
            df = df[present_cols]

            # ------------------------------------------------------------------
            # 3) Convert Date column to datetime index and coerce numeric values
            # ------------------------------------------------------------------
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df.dropna(subset=["Date"], inplace=True)
            df.set_index("Date", inplace=True)
            # Ensure chronological order for date-slice to work reliably
            df.sort_index(inplace=True)

            # Coerce all yield values to float and replace non-finite values with NaN
            df = df.apply(pd.to_numeric, errors="coerce")

            logger.info(
                "Parsed %s rows of UST yield curve data with columns: %s",
                len(df),
                list(df.columns),
            )
            return df

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error while fetching Treasury yield curve data: {e}")
        raise FedYieldCurveError(
            f"HTTP error fetching data: {e.response.status_code}"
        ) from e
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while fetching Treasury yield curve data: {e}",
            exc_info=True,
        )
        raise FedYieldCurveError("An unexpected error occurred.") from e


if __name__ == "__main__":
    import asyncio

    async def main():
        try:
            yield_curve_df = await fetch_fed_yield_curve_historical()
            print("Successfully fetched data:")
            print(yield_curve_df.head())
            print("\nLatest data point:")
            print(yield_curve_df.iloc[-1])
        except FedYieldCurveError as e:
            print(f"Error: {e}")

    asyncio.run(main())

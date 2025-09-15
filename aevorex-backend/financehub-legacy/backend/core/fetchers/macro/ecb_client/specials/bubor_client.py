from __future__ import annotations
import io
import json
from datetime import date

import httpx
import pandas as pd
from tenacity import retry, stop_after_attempt, wait_exponential, RetryError
from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService

logger = get_logger(__name__)

# Updated tenor list (2025-07-10): added 4M, 5M, 7M, 8M, 10M, 11M for full MNB coverage
BUBOR_TENORS = [
    "O/N",
    "1W",
    "2W",
    "1M",
    "2M",
    "3M",
    "4M",
    "5M",
    "6M",
    "7M",
    "8M",
    "9M",
    "10M",
    "11M",
    "12M",
]

# Lenient mapping from various Hungarian spellings to the definitive tenor.
HUN_TO_TENOR = {
    "O/N": "O/N",
    "ON": "O/N",
    "O/N ": "O/N",
    # Uppercase versions
    "1HÉT": "1W",
    "1 HÉT": "1W",
    "1HET": "1W",
    "2HÉT": "2W",
    "2 HÉT": "2W",
    "2HET": "2W",
    "1HÓNAP": "1M",
    "1 HÓNAP": "1M",
    "1HONAP": "1M",
    "1H": "1M",
    "2HÓNAP": "2M",
    "2 HÓNAP": "2M",
    "2HONAP": "2M",
    "2H": "2M",
    "3HÓNAP": "3M",
    "3 HÓNAP": "3M",
    "3HONAP": "3M",
    "3H": "3M",
    "4HÓNAP": "4M",
    "4 HÓNAP": "4M",
    "4HONAP": "4M",
    "4H": "4M",
    "5HÓNAP": "5M",
    "5 HÓNAP": "5M",
    "5HONAP": "5M",
    "5H": "5M",
    "6HÓNAP": "6M",
    "6 HÓNAP": "6M",
    "6HONAP": "6M",
    "6H": "6M",
    "7HÓNAP": "7M",
    "7 HÓNAP": "7M",
    "7HONAP": "7M",
    "7H": "7M",
    "8HÓNAP": "8M",
    "8 HÓNAP": "8M",
    "8HONAP": "8M",
    "8H": "8M",
    "9HÓNAP": "9M",
    "9 HÓNAP": "9M",
    "9HONAP": "9M",
    "9H": "9M",
    "10HÓNAP": "10M",
    "10 HÓNAP": "10M",
    "10HONAP": "10M",
    "10H": "10M",
    "11HÓNAP": "11M",
    "11 HÓNAP": "11M",
    "11HONAP": "11M",
    "11H": "11M",
    "12HÓNAP": "12M",
    "12 HÓNAP": "12M",
    "12HONAP": "12M",
    "12H": "12M",
    # Lowercase versions (as seen in MNB XLS)
    "1hét": "1W",
    "1 hét": "1W",
    "1het": "1W",
    "2hét": "2W",
    "2 hét": "2W",
    "2het": "2W",
    "1hónap": "1M",
    "1 hónap": "1M",
    "1honap": "1M",
    "2hónap": "2M",
    "2 hónap": "2M",
    "2honap": "2M",
    "3hónap": "3M",
    "3 hónap": "3M",
    "3honap": "3M",
    "4hónap": "4M",
    "4 hónap": "4M",
    "4honap": "4M",
    "5hónap": "5M",
    "5 hónap": "5M",
    "5honap": "5M",
    "6hónap": "6M",
    "6 hónap": "6M",
    "6honap": "6M",
    "7hónap": "7M",
    "7 hónap": "7M",
    "7honap": "7M",
    "8hónap": "8M",
    "8 hónap": "8M",
    "8honap": "8M",
    "9hónap": "9M",
    "9 hónap": "9M",
    "9honap": "9M",
    "10hónap": "10M",
    "10 hónap": "10M",
    "10honap": "10M",
    "11hónap": "11M",
    "11 hónap": "11M",
    "11honap": "11M",
    "12hónap": "12M",
    "12 hónap": "12M",
    "12honap": "12M",
}

# New MNB URL structure (2025 update)
BUBOR_XLS_URL = "https://www.mnb.hu/letoltes/bubor2.xls"


class BUBORAPIError(Exception):
    """Custom exception for BUBOR data fetching errors."""


class BUBORParsingError(Exception):
    """Custom exception for errors during BUBOR data parsing."""


def _normalise_tenor(col_name: str) -> str | None:
    """Normalises different Hungarian tenor representations to a standard format."""
    if not col_name or pd.isna(col_name):
        return None

    # Clean the column name: strip whitespace, convert to uppercase, remove spaces
    clean_name = str(col_name).strip().upper().replace(" ", "")

    # First check if it's already in the standard format
    if clean_name in BUBOR_TENORS:
        return clean_name

    # Then check the mapping
    result = HUN_TO_TENOR.get(clean_name)
    if result:
        return result

    # Debug logging for unmapped tenors
    logger.debug(f"Unmapped tenor column: '{col_name}' -> '{clean_name}'")
    return None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def _download_bubor_xls() -> bytes:
    """
    Download BUBOR term-structure historical XLS from MNB using the new direct URL.
    Updated for 2025 MNB URL structure change.
    """
    logger.info(f"Downloading BUBOR data from: {BUBOR_XLS_URL}")

    # Increased timeout for potentially slow MNB responses.
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(BUBOR_XLS_URL)
        resp.raise_for_status()
        return resp.content


def _parse_bubor_xls(
    xls_binary: bytes, start_date: date, end_date: date
) -> dict[str, dict[str, float]]:
    """
    Parse BUBOR XLS and filter by date range.
    Return nested dict date→tenor→value with improved robustness for headers and values.
    Enhanced to handle the new MNB XLS structure with yearly sheets.
    """
    try:
        with io.BytesIO(xls_binary) as fh:
            # Read all sheets and find the relevant yearly sheets
            sheets = pd.read_excel(fh, sheet_name=None, header=None)

        curve: dict[str, dict[str, float]] = {}

        # Get the years we need to process based on date range
        years_to_process = set()
        current_date = start_date
        while current_date <= end_date:
            years_to_process.add(str(current_date.year))
            current_date = current_date.replace(
                year=current_date.year + 1, month=1, day=1
            )
            if current_date > end_date:
                break

        logger.info(f"Processing BUBOR years: {years_to_process}")

        for year in years_to_process:
            if year not in sheets:
                logger.warning(f"Year {year} not found in BUBOR XLS sheets")
                continue

            yearly_sheet = sheets[year]
            
            # Skip empty sheets
            if yearly_sheet.empty:
                logger.warning(f"Year {year} sheet is empty, skipping")
                continue

            # Find the header row by looking for 'jegyzési nap', 'date of fixing' or similar keywords
            header_row_index = -1
            for i, row in yearly_sheet.iterrows():
                row_str = " ".join(
                    str(cell).strip().upper() for cell in row if pd.notna(cell)
                )
                if any(
                    keyword in row_str
                    for keyword in [
                        "JEGYZÉSI NAP",
                        "DATE OF FIXING",
                        "DÁTUM",
                        "DATE",
                        "DATUM",
                    ]
                ):
                    header_row_index = i
                    break

            if header_row_index == -1:
                logger.warning(
                    f"Could not find a valid header row in BUBOR XLS sheet for year {year}"
                )
                continue

            # Use the Hungarian header row (first row) for column names, but skip the first 2 rows for data
            yearly_sheet.columns = yearly_sheet.iloc[0]  # Use first row as column names
            yearly_sheet = yearly_sheet.drop([0, 1]).reset_index(
                drop=True
            )  # Skip both header rows

            yearly_sheet.columns = [str(c).strip() for c in yearly_sheet.columns]
            date_col = yearly_sheet.columns[0]  # First column is always the date

            for _, row in yearly_sheet.iterrows():
                try:
                    # Enhanced date parsing with multiple formats
                    date_value = row[date_col]
                    if pd.isna(date_value):
                        continue

                    # Try to parse date with various formats
                    parsed_date = pd.to_datetime(date_value, errors="coerce")
                    if pd.isna(parsed_date):
                        continue

                    row_date = parsed_date.date()

                    # Filter by date range
                    if row_date < start_date or row_date > end_date:
                        continue

                    date_str = row_date.isoformat()

                except Exception as e:
                    logger.debug(f"Failed to parse date from row in year {year}: {e}")
                    continue

                if date_str not in curve:
                    curve[date_str] = {}

                for raw_col, val in row.items():
                    if not raw_col or pd.isna(raw_col):
                        continue

                    tenor = _normalise_tenor(str(raw_col))
                    if tenor and pd.notna(val) and val not in ("-", "", None):
                        try:
                            # Replace comma decimal separator and handle percentage
                            if isinstance(val, str):
                                val = val.replace(",", ".").replace("%", "")
                            curve[date_str][tenor] = float(val)
                        except (ValueError, TypeError):
                            continue

        return curve

    except Exception as e:
        logger.error(f"Failed to parse BUBOR XLS file: {e}", exc_info=True)
        raise BUBORParsingError("Error parsing BUBOR XLS file.") from e


class BUBORClient:
    def __init__(self, cache_service=None):
        self.cache = cache_service
        self.cache_ttl = 3600  # 1 hour
        self.stale_ttl = self.cache_ttl + 300  # 1 hour + 5 minutes for stale serving

    async def get_bubor_history(
        self, start_date: date, end_date: date
    ) -> dict[str, dict[str, float]]:
        """
        Fetches BUBOR history with retries using the new MNB URL structure.
        If the live fetch fails, it attempts to serve data from a stale cache.
        """
        cache_key = f"bubor_history:v4:{start_date}:{end_date}"
        stale_cache_key = f"{cache_key}:stale"

        if self.cache:
            cached_data = await self.cache.get(cache_key)
            if cached_data:
                logger.info("Returning cached BUBOR data")
                return json.loads(cached_data)

        try:
            # Download the full XLS file (no date parameters in new URL)
            xls_data = await _download_bubor_xls()

            # Parse and filter by date range
            parsed_data = _parse_bubor_xls(xls_data, start_date, end_date)

            if not parsed_data:
                logger.warning(
                    "Parsing BUBOR XLS resulted in empty data for the requested date range."
                )
                # Don't raise error for empty date range, just return empty dict
                parsed_data = {}

            if self.cache:
                await self.cache.set(
                    cache_key, json.dumps(parsed_data), ttl=self.cache_ttl
                )
                await self.cache.set(
                    stale_cache_key, json.dumps(parsed_data), ttl=self.stale_ttl
                )

            return parsed_data

        except RetryError as e:
            logger.error(
                f"BUBOR API request failed after multiple retries: {e}. Attempting to serve from stale cache."
            )
            if self.cache:
                stale_data = await self.cache.get(stale_cache_key)
                if stale_data:
                    logger.warning(f"Serving stale BUBOR data for key {cache_key}")
                    return json.loads(stale_data)

            logger.critical(
                f"No stale cache available for BUBOR. Failing request. Error: {e}"
            )
            raise BUBORAPIError(
                f"Failed to fetch data from BUBOR API and no stale cache was available: {e}"
            ) from e
        except httpx.HTTPStatusError as e:
            logger.error(
                f"BUBOR API request failed: {e.response.status_code} - {e.response.text}"
            )
            raise BUBORAPIError(f"Failed to fetch data from BUBOR API: {e}") from e
        except BUBORParsingError as e:
            logger.error(f"Failed to parse BUBOR XLS file: {e}", exc_info=True)
            raise e  # Reraise the original parsing error
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while fetching BUBOR data: {e}",
                exc_info=True,
            )
            raise BUBORAPIError(f"An unexpected error occurred: {e}") from e


async def fetch_bubor_curve(
    start_date: date,
    end_date: date,
    cache: CacheService,
) -> dict[str, dict[str, float]]:
    """
    Public fetcher for BUBOR curve data using the updated MNB URL structure.
    """
    logger.info(f"Fetching BUBOR curve from {start_date} to {end_date}")

    bubor_client = BUBORClient(cache_service=cache)
    return await bubor_client.get_bubor_history(start_date, end_date)

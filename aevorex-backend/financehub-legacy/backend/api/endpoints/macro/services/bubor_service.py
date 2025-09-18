"""
BUBOR Service

MNB (Hungarian National Bank) BUBOR data handling.
Provides BUBOR curve data fetching and processing from official MNB Excel files.
Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
"""

from typing import Dict, Any, Optional, List, TypedDict
from datetime import date, timedelta, datetime
import pandas as pd
import os
from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus
import httpx
import io

logger = get_logger(__name__)


class BuborService:
    """Service for MNB BUBOR data handling."""
    
    def __init__(self, cache_service: Optional[CacheService] = None):
        self.cache = cache_service or CacheService()
        self.provider = "mnb_bubor"
        self.base_url = "https://www.mnb.hu/arfolyamok/bubor"
        self._debug = False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """
        Get BUBOR provider information.
        
        Returns:
            Dictionary containing provider information
        """
        return {
            "provider": self.provider,
            "name": "Hungarian National Bank (MNB)",
            "description": "Official BUBOR data from MNB Excel files",
            "source_url": "https://www.mnb.hu/letoltes/bubor2.xls",
            "update_frequency": "daily",
            "supported_tenors": ["O/N", "1hét", "2hét", "1hónap", "2hónap", "3hónap", "4hónap", "5hónap", "6hónap", "7hónap", "8hónap", "9hónap", "10hónap", "11hónap", "12hónap"]
        }
    
    def _generate_cache_key(self, method: str, **params) -> str:
        """
        Generate deterministic cache key for method and parameters.
        
        Args:
            method: Method name (e.g., 'curve', 'rate', 'latest', 'metadata')
            **params: Method parameters
            
        Returns:
            Deterministic cache key string
        """
        # Sort params for consistent key generation
        sorted_params = sorted(params.items()) if params else []
        param_str = ":".join([f"{k}={v}" for k, v in sorted_params if v is not None])
        
        if param_str:
            return f"{self.provider}:{method}:{param_str}"
        else:
            return f"{self.provider}:{method}"

    def _error(self, message: str, cache_status: str = "error") -> Dict[str, Any]:
        """
        Helper method for consistent error responses.
        
        Args:
            message: Error message
            cache_status: Cache status for the error
            
        Returns:
            Standardized error response
        """
        return StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.MNB,
            message=message,
            error_code="BUBOR_SERVICE_ERROR"
        )

    async def _load_bubor_excel(self) -> tuple[Dict[str, Dict[str, float]], str]:
        """
        Load BUBOR data from MNB official website by downloading and parsing the XLS file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        
        Returns:
            Tuple of (data, cache_status) where cache_status is "cached" or "fresh"
        """
        cached_data = await self.cache.get("bubor_data")
        if cached_data:
            logger.debug("Using cached BUBOR data")
            return cached_data, "cached"

        try:
            url = "https://www.mnb.hu/letoltes/bubor2.xls"
            logger.info(f"Downloading BUBOR data from: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                response.raise_for_status()
            if self._debug:
                logger.debug(f"Download successful, content length: {len(response.content)}")
            
            excel_bytes = io.BytesIO(response.content)
            
            # Use xlrd engine for .xls files with explicit sheet selection
            excel_file = pd.ExcelFile(excel_bytes, engine="xlrd")
            available_sheets = excel_file.sheet_names
            if self._debug:
                logger.debug(f"Available Excel sheets: {available_sheets}")
            
            # Try to use "2025" sheet first, then fallback to latest year sheet
            target_sheet = None
            if "2025" in available_sheets:
                target_sheet = "2025"
                logger.info(f"Using explicit 2025 sheet")
            else:
                # Find the latest year sheet (skip non-year sheets like 'Sheet1', 'comment', 'hibalista-error list')
                year_sheets = [sheet for sheet in available_sheets if sheet.isdigit() and len(sheet) == 4]
                if year_sheets:
                    target_sheet = max(year_sheets)
                    logger.info(f"Using latest year sheet: {target_sheet}")
                else:
                    # Fallback to last sheet if no year sheets found
                    target_sheet = available_sheets[-1]
                    logger.info(f"No year sheets found, using last sheet: {target_sheet}")
            
            # Attempt to read the Excel sheet with header=0 to use the file's own headers
            try:
                df = pd.read_excel(excel_bytes, sheet_name=target_sheet, engine="xlrd", header=0)
                if self._debug:
                    logger.debug(f"Excel parsed successfully with file headers, shape: {df.shape}")
                    logger.debug(f"Excel columns (file headers): {df.columns.tolist()}")
                    logger.debug(f"First few rows:\n{df.head()}")
            except Exception as e:
                logger.warning(f"Failed to read Excel with header=0: {e}, falling back to manual Hungarian headers")
                df_raw = pd.read_excel(excel_bytes, sheet_name=target_sheet, engine="xlrd", header=None)
                # Set explicit Hungarian headers
                df = df_raw.copy()
                df.columns = ["jegyzési nap", "O/N", "1hét", "2hét", "1hónap", "2hónap", "3hónap", "4hónap", "5hónap", "6hónap", "7hónap", "8hónap", "9hónap", "10hónap", "11hónap", "12hónap"]
                df = df.drop(index=0).reset_index(drop=True)
                df = df.dropna(how="all")
                if self._debug:
                    logger.debug(f"Excel parsed successfully with Hungarian headers (fallback), shape: {df.shape}")
                    logger.debug(f"Excel columns (Hungarian headers): {df.columns.tolist()}")
                    logger.debug(f"First few rows:\n{df.head()}")
            
            # Check if dataframe is empty after cleaning
            if df.empty or df.shape[0] == 0:
                logger.error(f"Excel sheet '{target_sheet}' is empty after cleaning")
                return {}, "error"
            
            # Find the last row with actual BUBOR data (not header/error messages)
            for i in range(len(df) - 1, -1, -1):
                row = df.iloc[i]
                try:
                    date_key = pd.to_datetime(row.iloc[0]).date().isoformat()
                except Exception:
                    date_key = str(row.iloc[0])
                if self._debug:
                    logger.debug(f"Checking row {i}: {date_key}")
                
                # Skip rows with error messages or headers
                if any(keyword in date_key.lower() for keyword in ["nincs megjelenítendő", "no errors reported", "reporting period", "date of fixing"]):
                    logger.warning(f"Skipping row {i} with header/error message: {date_key}")
                    continue
                
                # Check if this row has numeric BUBOR data
                has_numeric_data = False
                for col in row.iloc[1:]:  # Skip first column (date)
                    try:
                        if pd.notna(col) and str(col).strip() != '-' and str(col).strip() != '':
                            float(str(col))
                            has_numeric_data = True
                            break
                    except (ValueError, TypeError):
                        continue
                
                if has_numeric_data:
                    last_row = row
                    if self._debug:
                        logger.debug(f"Found valid data row {i} with date: {date_key}")
                    break
            else:
                logger.error("No valid BUBOR data rows found in Excel")
                return {}, "error"
            
            # Use the Hungarian tenor column names directly from the file (columns after the first)
            expected_tenors = list(df.columns[1:])
            rates = {}
            
            for tenor in expected_tenors:
                if tenor in last_row:
                    value = last_row[tenor]
                    if pd.notna(value) and value != "-":
                        rates[tenor] = float(value)
                        if self._debug:
                            logger.debug(f"Added rate {tenor}: {value}")
            
            if self._debug:
                logger.debug(f"Final rates: {rates}")
            result = {date_key: rates}
            await self.cache.set("bubor_data", result, ttl=86400)
            return result, "fresh"
            
        except Exception as e:
            logger.error(f"Failed to load BUBOR Excel data: {e}", exc_info=True)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
            return {}, "error"
    
    async def get_bubor_curve(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get complete BUBOR curve from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        Returns all available tenors for the most recent date.
        """
        logger.info(f"Fetching BUBOR curve | start_date: {start_date}, end_date: {end_date}")
        
        # Generate deterministic cache key for this method and parameters
        cache_key = self._generate_cache_key("curve", start_date=start_date, end_date=end_date)
        logger.info(f"Generated cache key: {cache_key}")
        
        try:
            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache HIT for BUBOR curve: {cache_key}")
                return cached_result
            
            logger.info("Cache MISS - fetching fresh BUBOR curve data...")
            
            # Fetch fresh data
            bubor_data, data_cache_status = await self._load_bubor_excel()
            if not bubor_data:
                logger.error("No BUBOR data returned from _load_bubor_excel")
                return self._error("No BUBOR data available")
            
            latest_date = max(bubor_data.keys())
            result = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data=bubor_data[latest_date],
                series_id="BUBOR_CURVE",
                date=latest_date,
                frequency="daily",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
            
            # Cache the result for 1 hour (3600 seconds)
            await self.cache.set(cache_key, result, ttl=3600)
            logger.info(f"Cached BUBOR curve result: {cache_key}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching BUBOR curve: {e}", exc_info=True)
            return self._error(f"Failed to fetch BUBOR curve: {str(e)}")

    def _map_tenor(self, tenor: str) -> str:
        """
        Map standard tenor formats to BUBOR-specific formats.
        
        Args:
            tenor: Standard tenor format (e.g., '3M', '6M', '1Y')
            
        Returns:
            BUBOR-specific tenor format (e.g., '3hónap', '6hónap', '12hónap')
        """
        tenor_mapping = {
            "1M": "1hónap",
            "2M": "2hónap", 
            "3M": "3hónap",
            "4M": "4hónap",
            "5M": "5hónap",
            "6M": "6hónap",
            "7M": "7hónap",
            "8M": "8hónap",
            "9M": "9hónap",
            "10M": "10hónap",
            "11M": "11hónap",
            "12M": "12hónap",
            "1Y": "12hónap",
            "2Y": "24hónap",
            "3Y": "36hónap",
            "5Y": "60hónap",
            "10Y": "120hónap",
            "30Y": "360hónap"
        }
        return tenor_mapping.get(tenor, tenor)

    async def get_bubor_rate(self, tenor: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get BUBOR rate for specific tenor from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        """
        # Map tenor to BUBOR-specific format
        mapped_tenor = self._map_tenor(tenor)
        logger.info(f"Fetching BUBOR rate | tenor: {tenor} -> {mapped_tenor}, start_date: {start_date}, end_date: {end_date}")
        
        # Generate deterministic cache key for this method and parameters
        cache_key = self._generate_cache_key("rate", tenor=mapped_tenor, start_date=start_date, end_date=end_date)
        
        try:
            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache HIT for BUBOR rate: {cache_key}")
                return cached_result
            
            logger.info("Cache MISS - fetching fresh BUBOR rate data...")
            
            # Fetch fresh data
            bubor_data, data_cache_status = await self._load_bubor_excel()
            tenor_data = {}
            for date_str, rates in bubor_data.items():
                if mapped_tenor in rates:
                    tenor_data[date_str] = rates[mapped_tenor]
            
            if not tenor_data:
                # Get available tenors from the latest data
                available_tenors = []
                if bubor_data:
                    latest_date = max(bubor_data.keys())
                    available_tenors = list(bubor_data[latest_date].keys())
                
                error_result = StandardResponseBuilder.create_macro_error_response(
                    provider=MacroProvider.MNB,
                    message=f"Tenor '{tenor}' (mapped to '{mapped_tenor}') not found. Available tenors: {available_tenors}",
                    error_code="BUBOR_TENOR_NOT_FOUND",
                    series_id=f"BUBOR_{tenor}"
                )
                # Don't cache error results
                return error_result
            
            latest_date = max(tenor_data.keys())
            result = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data={latest_date: tenor_data[latest_date]},
                series_id=f"BUBOR_{tenor}",
                date=latest_date,
                frequency="daily",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
            
            # Cache the result for 1 hour (3600 seconds)
            await self.cache.set(cache_key, result, ttl=3600)
            logger.info(f"Cached BUBOR rate result: {cache_key}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching BUBOR rate for {tenor}: {e}", exc_info=True)
            return self._error(f"Failed to fetch BUBOR rate for {tenor}: {str(e)}")

    async def get_latest_bubor(self) -> Dict[str, Any]:
        """
        Get the latest BUBOR fixing from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        Returns all available tenors for the most recent date.
        """
        logger.info("Fetching latest BUBOR fixing")
        
        # Generate deterministic cache key for this method (no parameters)
        cache_key = self._generate_cache_key("latest")
        
        try:
            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache HIT for latest BUBOR: {cache_key}")
                return cached_result
            
            logger.info("Cache MISS - fetching fresh latest BUBOR data...")
            
            # Fetch fresh data
            bubor_data, data_cache_status = await self._load_bubor_excel()
            
            if not bubor_data:
                return self._error("No BUBOR data available")
            
            latest_date = max(bubor_data.keys())
            latest_rates = bubor_data[latest_date]
            
            result = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data=latest_rates,
                series_id="BUBOR_LATEST",
                date=latest_date,
                frequency="daily",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
            
            # Cache the result for 1 hour (3600 seconds)
            await self.cache.set(cache_key, result, ttl=3600)
            logger.info(f"Cached latest BUBOR result: {cache_key}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching latest BUBOR: {e}", exc_info=True)
            return self._error(f"Failed to fetch latest BUBOR: {str(e)}")

    async def get_bubor_metadata(self) -> Dict[str, Any]:
        """
        Get BUBOR metadata and available tenors from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls.
        """
        logger.info("Fetching BUBOR metadata (available tenors)")
        
        # Generate deterministic cache key for this method (no parameters)
        cache_key = self._generate_cache_key("metadata")
        
        try:
            # Check cache first
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Cache HIT for BUBOR metadata: {cache_key}")
                return cached_result
            
            logger.info("Cache MISS - fetching fresh BUBOR metadata...")
            
            # Get dynamic tenors from actual data
            bubor_data, data_cache_status = await self._load_bubor_excel()
            dynamic_tenors = []
            is_static = False
            
            if bubor_data:
                # Get tenors from the latest available data
                latest_date = max(bubor_data.keys())
                dynamic_tenors = list(bubor_data[latest_date].keys())
                is_static = False  # Dynamic metadata from actual data
            else:
                # Fallback to static list if no data available
                dynamic_tenors = ["O/N", "1hét", "2hét", "1hónap", "2hónap", "3hónap", "4hónap", "5hónap", "6hónap", "7hónap", "8hónap", "9hónap", "10hónap", "11hónap", "12hónap"]
                is_static = True  # Static fallback metadata
            
            result = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.MNB,
                data={
                    "tenors": dynamic_tenors,
                    "description": "Available BUBOR tenors from MNB official Excel file",
                    "source": "https://www.mnb.hu/letoltes/bubor2.xls",
                    "static_metadata": is_static,
                    "data_available": len(bubor_data) > 0 if bubor_data else False
                },
                series_id="BUBOR_METADATA",
                frequency="metadata",
                units="list",
                cache_status=CacheStatus.FRESH
            )
            
            # Cache the result for 2 hours (7200 seconds) - metadata changes less frequently
            await self.cache.set(cache_key, result, ttl=7200)
            logger.info(f"Cached BUBOR metadata result: {cache_key}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching BUBOR metadata: {e}", exc_info=True)
            return self._error(f"Failed to fetch BUBOR metadata: {str(e)}")


__all__ = ["BuborService"]

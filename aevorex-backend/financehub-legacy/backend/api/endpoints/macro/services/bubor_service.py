"""
BUBOR Service

MNB (Hungarian National Bank) BUBOR data handling.
Provides BUBOR curve data fetching and processing from official MNB Excel files.
Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
"""

from typing import Dict, Any, Optional
from datetime import date, timedelta
import pandas as pd
import os
from backend.utils.logger_config import get_logger
from backend.utils.cache_service import CacheService
import httpx
import io

logger = get_logger(__name__)


class BuborService:
    """Service for MNB BUBOR data handling."""
    
    def __init__(self, cache_service: Optional[CacheService] = None):
        self.provider = "mnb_bubor"
        self.base_url = "https://www.mnb.hu/arfolyamok/bubor"
        self.cache = cache_service or CacheService()

    async def _load_bubor_excel(self) -> Dict[str, Dict[str, float]]:
        """
        Load BUBOR data from MNB official website by downloading and parsing the XLS file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        """
        try:
            url = "https://www.mnb.hu/letoltes/bubor2.xls"
            logger.info(f"Downloading BUBOR data from: {url}")
            
            response = await httpx.AsyncClient().get(url)
            response.raise_for_status()
            logger.info(f"Download successful, content length: {len(response.content)}")
            
            excel_bytes = io.BytesIO(response.content)
            
            # Use xlrd engine for .xls files with explicit sheet selection
            excel_file = pd.ExcelFile(excel_bytes, engine="xlrd")
            available_sheets = excel_file.sheet_names
            logger.info(f"Available Excel sheets: {available_sheets}")
            
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
            
            df = pd.read_excel(excel_bytes, sheet_name=target_sheet, engine="xlrd")
            df = df.dropna(how="all")
            
            logger.info(f"Excel parsed successfully, shape: {df.shape}")
            logger.info(f"Excel columns: {df.columns.tolist()}")
            logger.info(f"First few rows:\n{df.head()}")
            
            # Check if dataframe is empty after cleaning
            if df.empty or df.shape[0] == 0:
                logger.error(f"Excel sheet '{target_sheet}' is empty after cleaning")
                return {}
            
            # Find the last row with actual BUBOR data (not header/error messages)
            for i in range(len(df) - 1, -1, -1):
                row = df.iloc[i]
                date_key = str(row.iloc[0])
                logger.info(f"Checking row {i}: {date_key}")
                
                # Skip rows with error messages or headers
                if any(keyword in date_key.lower() for keyword in ["nincs megjelenítendő", "no errors reported", "reporting period", "jegyzési nap"]):
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
                    logger.info(f"Found valid data row {i} with date: {date_key}")
                    break
            else:
                logger.error("No valid BUBOR data rows found in Excel")
                return {}
            
            # MNB Excel uses Hungarian column names
            hungarian_tenors = ["O/N", "1hét", "2hét", "1hónap", "2hónap", "3hónap", "4hónap", "5hónap", "6hónap", "7hónap", "8hónap", "9hónap", "10hónap", "11hónap", "12hónap"]
            english_tenors = ["O/N", "1W", "2W", "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M", "9M", "10M", "11M", "12M"]
            rates = {}
            
            for hungarian_tenor, english_tenor in zip(hungarian_tenors, english_tenors):
                if hungarian_tenor in last_row:
                    value = last_row[hungarian_tenor]
                    if pd.notna(value) and value != "-":
                        rates[english_tenor] = float(value)
                        logger.info(f"Added rate {english_tenor} (from {hungarian_tenor}): {value}")
            
            logger.info(f"Final rates: {rates}")
            return {date_key: rates}
            
        except Exception as e:
            logger.error(f"Failed to load BUBOR Excel data: {e}", exc_info=True)
            return {}
    
    async def get_bubor_curve(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get complete BUBOR curve from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        Returns all available tenors for the most recent date.
        """
        logger.info(f"Fetching BUBOR curve | start_date: {start_date}, end_date: {end_date}")
        
        try:
            bubor_data = await self._load_bubor_excel()
            return {
                "status": "success",
                "provider": self.provider,
                "data": {
                    "curve": bubor_data
                }
            }
        except Exception as e:
            logger.error(f"Error fetching BUBOR curve: {e}")
            return {
                "status": "error",
                "provider": self.provider,
                "error": str(e),
                "data": {
                    "curve": []
                }
            }

    async def get_bubor_rate(self, tenor: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get BUBOR rate for specific tenor from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        """
        logger.info(f"Fetching BUBOR rate | tenor: {tenor}, start_date: {start_date}, end_date: {end_date}")
        
        try:
            bubor_data = await self._load_bubor_excel()
            tenor_data = {}
            for date_str, rates in bubor_data.items():
                if tenor in rates:
                    tenor_data[date_str] = rates[tenor]
            
            return {
                "status": "success",
                "provider": self.provider,
                "tenor": tenor,
                "data": tenor_data
            }
        except Exception as e:
            logger.error(f"Error fetching BUBOR rate for {tenor}: {e}")
            return {
                "status": "error",
                "provider": self.provider,
                "tenor": tenor,
                "error": str(e),
                "data": []
            }

    async def get_latest_bubor(self) -> Dict[str, Any]:
        """
        Get the latest BUBOR fixing from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls (latest row by default).
        Returns all available tenors for the most recent date.
        """
        logger.info("Fetching latest BUBOR fixing")
        
        try:
            bubor_data = await self._load_bubor_excel()
            
            if not bubor_data:
                return {
                    "status": "error",
                    "provider": self.provider,
                    "error": "No BUBOR data available",
                    "date": None,
                    "rates": {}
                }
            
            latest_date = max(bubor_data.keys())
            latest_rates = bubor_data[latest_date]
            
            return {
                "status": "success",
                "provider": self.provider,
                "date": latest_date,
                "rates": latest_rates
            }
        except Exception as e:
            logger.error(f"Error fetching latest BUBOR: {e}")
            return {
                "status": "error",
                "provider": self.provider,
                "error": str(e),
                "date": None,
                "rates": {}
            }

    async def get_bubor_metadata(self) -> Dict[str, Any]:
        """
        Get BUBOR metadata and available tenors from MNB official Excel file.
        Source: https://www.mnb.hu/letoltes/bubor2.xls.
        """
        logger.info("Fetching BUBOR metadata (available tenors)")
        return {
            "status": "success",
            "provider": self.provider,
            "tenors": ["O/N", "1W", "2W", "1M", "2M", "3M", "4M", "5M", "6M", "7M", "8M", "9M", "10M", "11M", "12M"]
        }


__all__ = ["BuborService"]

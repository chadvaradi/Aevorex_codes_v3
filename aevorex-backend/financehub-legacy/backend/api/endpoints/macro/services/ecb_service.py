"""
ECB Service for fetching European Central Bank data using proper headers and SDMX format.

This service handles the ECB API access issues by using proper Accept headers
and following the SDMX 2.1 specification.
"""

import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import httpx
from backend.utils.cache_service import CacheService
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus

logger = logging.getLogger(__name__)

class ECBService:
    """
    Service for fetching data from European Central Bank (ECB) API.
    
    Uses proper SDMX headers to avoid blocking issues.
    """
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
        self.base_url = "https://data-api.ecb.europa.eu/service/data"
        self.timeout = 30.0
        
        # Proper headers for ECB API
        self.headers = {
            "Accept": "application/vnd.sdmx.data+json;version=1.0.0-wd",
            "User-Agent": "Aevorex-FinanceHub/1.0 (https://aevorex.com)",
            "Referer": "https://data.ecb.europa.eu/",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Cache-Control": "no-cache"
        }
        
        # ECB series configurations
        self.SERIES_CONFIG = {
            "HICP": {
                "resource_id": "ICP",
                "key": "M.U2.N.000000.4.ANR",  # Euro area HICP, monthly, annual rate
                "description": "Harmonised Index of Consumer Prices - Euro area",
                "frequency": "monthly",
                "units": "percent"
            },
            "HUR": {
                "resource_id": "LFSI", 
                "key": "M.I9.S.UNEHRT.TOTAL0.15_74.T",  # Euro area unemployment rate
                "description": "Unemployment Rate - Euro area",
                "frequency": "monthly", 
                "units": "percent"
            }
        }
    
    def _error(self, message: str, cache_status: str = "error", series_id: str = "ECB_ERROR") -> Dict[str, Any]:
        """
        Helper method for consistent error responses.
        
        Args:
            message: Error message
            cache_status: Cache status (default: "error")
            
        Returns:
            Standardized error response
        """
        return StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=message,
            error_code="ECB_API_ERROR",
            series_id=series_id
        )
    
    async def _fetch_series(self, series_key: str, start_date: str, end_date: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Common logic for fetching ECB series data.
        
        Args:
            series_key: Key from SERIES_CONFIG
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            force_refresh: Force refresh cache
            
        Returns:
            Standardized response with series data
        """
        try:
            # Get config first
            config = self.SERIES_CONFIG[series_key]
            
            # Check cache first
            cache_key = f"ecb:{series_key}:{start_date}:{end_date}"
            if not force_refresh:
                cached_data = await self.cache_service.get(cache_key)
                if cached_data:
                    logger.debug(f"Returning cached {series_key} data")
                    return StandardResponseBuilder.create_macro_success_response(
                        provider=MacroProvider.ECB,
                        data=json.loads(cached_data),
                        series_id=config.get("key", f"ECB_{series_key}"),
                        frequency=config.get("frequency", "monthly"),
                        units=config.get("units", "percent"),
                        cache_status=CacheStatus.CACHED
                    )
            
            # Fetch data from ECB
            url = f"{self.base_url}/{config['resource_id']}/{config['key']}"
            
            params = {
                "startPeriod": start_date,
                "endPeriod": end_date,
                "detail": "dataonly"
            }
            
            logger.info(f"Fetching {series_key} data from ECB: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    logger.debug(f"ECB API response status: {response.status_code}")
                    
                    # Parse SDMX JSON response
                    parsed_data = self._parse_sdmx_response(data, config)
                    
                    # Cache the result
                    await self.cache_service.set(
                        cache_key, 
                        json.dumps(parsed_data), 
                        ttl=3600  # 1 hour cache
                    )
                    
                    logger.debug(f"Successfully fetched {series_key} data: {len(parsed_data.get('observations', []))} observations")
                    
                    # Return MCP-ready response
                    return StandardResponseBuilder.create_macro_success_response(
                        provider=MacroProvider.ECB,
                        data=parsed_data,
                        series_id=config.get("key", f"ECB_{series_key}"),
                        frequency=config.get("frequency", "monthly"),
                        units=config.get("units", "percent"),
                        cache_status=CacheStatus.FRESH
                    )
                    
                elif response.status_code == 404:
                    logger.warning(f"ECB API: {series_key} series not found (404)")
                    return self._error(f"{series_key} series not found in ECB database")
                    
                elif response.status_code == 400:
                    logger.warning(f"ECB API: Bad request for {series_key} data (400)")
                    return self._error(f"Invalid request parameters for {series_key} data")
                    
                else:
                    logger.error(f"ECB API error for {series_key}: {response.status_code}")
                    return self._error(f"ECB API returned status {response.status_code}")
                    
        except httpx.TimeoutException:
            logger.error(f"Timeout fetching {series_key} data from ECB", exc_info=True)
            return self._error("Timeout connecting to ECB API")
            
        except Exception as e:
            logger.error(f"Error fetching {series_key} data: {str(e)}", exc_info=True)
            return self._error(f"Failed to fetch {series_key} data: {str(e)}")
    
    async def get_hicp_data(
        self, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch HICP (Harmonised Index of Consumer Prices) data from ECB.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format  
            force_refresh: Force refresh cache
            
        Returns:
            Dictionary with HICP data or error information
        """
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        return await self._fetch_series("HICP", start_date, end_date, force_refresh)
    
    async def get_unemployment_data(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None, 
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch unemployment rate data from ECB.
        
        Args:
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            force_refresh: Force refresh cache
            
        Returns:
            Dictionary with unemployment data or error information
        """
        # Set default date range if not provided
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        
        return await self._fetch_series("HUR", start_date, end_date, force_refresh)
    
    def _parse_sdmx_response(self, data: Dict[str, Any], config: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse SDMX JSON response from ECB API.
        
        Args:
            data: Raw SDMX JSON response
            config: Series configuration
            
        Returns:
            Parsed data in standardized format
        """
        try:
            observations = []
            
            # TODO: Replace with conditional debug flag if needed
            logger.debug(f"SDMX data structure keys: {list(data.keys())}")
            
            # Extract data from SDMX structure
            if "dataSets" in data:
                datasets = data["dataSets"]
                if datasets and len(datasets) > 0:
                    dataset = datasets[0]
                    
                    # Get observations from series
                    if "series" in dataset:
                        for series_key, series_data in dataset["series"].items():
                            if "observations" in series_data:
                                for obs_key, obs_data in series_data["observations"].items():
                                    if obs_data and len(obs_data) > 0:
                                        value = obs_data[0]
                                        if value is not None and value != ".":
                                            try:
                                                # Parse date and value
                                                date_str = self._parse_observation_key(obs_key, data)
                                                float_value = float(value)
                                                
                                                observations.append({
                                                    "date": date_str,
                                                    "value": float_value
                                                })
                                            except (ValueError, TypeError) as e:
                                                logger.warning(f"Could not parse observation {obs_key}: {e}")
                                                continue
            
            # Sort observations by date
            observations.sort(key=lambda x: x["date"])
            
            # Calculate basic statistics
            values = [obs["value"] for obs in observations]
            stats = {}
            if values:
                stats = {
                    "count": len(values),
                    "latest": values[-1] if values else None,
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values)
                }
            
            return StandardResponseBuilder.success(
                {
                    "observations": observations,
                    "statistics": stats,
                    "data_type_info": {
                        "data_type": "official_statistic",
                        "quality": "high",
                        "description": f"Official {config['description']} from ECB",
                        "frequency": config["frequency"],
                        "source": "ECB"
                    }
                },
                meta={
                    "provider": "ecb",
                    "series_id": f"{config['resource_id']}.{config['key']}",
                    "title": config["description"],
                    "frequency": config["frequency"],
                    "units": config["units"],
                    "last_updated": datetime.now().isoformat(),
                    "cache_status": "fresh"
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing SDMX response: {str(e)}", exc_info=True)
            return StandardResponseBuilder.error(
                f"Failed to parse ECB response: {str(e)}",
                meta={"provider": "ecb", "cache_status": "error"}
            )
    
    def _parse_observation_key(self, obs_key: str, data: Dict[str, Any]) -> str:
        """
        Parse observation key to extract date using structure information.

        Args:
            obs_key: Observation key from SDMX response (e.g., "0", "1", "2")
            data: Full SDMX response data

        Returns:
            Date string in YYYY-MM-DD format
        """
        try:
            obs_index = int(obs_key)
            # TODO: Replace with conditional debug flag if needed
            logger.debug(f"Parsing obs_key: {obs_key}, obs_index: {obs_index}")

            # Navigate into structure.dimensions.observation
            if "structure" in data and "dimensions" in data["structure"]:
                observation_dims = data["structure"]["dimensions"].get("observation", [])
                for dim in observation_dims:
                    if dim.get("id") == "TIME_PERIOD":
                        values = dim.get("values", [])
                        if obs_index < len(values):
                            time_period = values[obs_index]["id"]
                            # Convert YYYY-MM to YYYY-MM-01
                            if len(time_period) == 7 and "-" in time_period:
                                year, month = time_period.split("-")
                                return f"{year}-{month}-01"
                            return time_period

            # Fallback
            return obs_key

        except (ValueError, KeyError, IndexError) as e:
            logger.warning(f"Could not parse observation key {obs_key}: {e}")
            return obs_key
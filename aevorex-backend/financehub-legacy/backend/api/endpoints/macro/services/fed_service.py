


import os
import json
import logging
import asyncio
from typing import Any, Dict, Optional, List
from datetime import timedelta, datetime

import httpx
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus

FRED_API_KEY = os.getenv("FINBOT_API_KEYS__FRED")
FRED_BASE_URL = "https://api.stlouisfed.org/fred"
CACHE_EXPIRE_SECONDS = 3600  # 1 hour

logger = logging.getLogger(__name__)

# Debug: Check if API key is loaded
if not FRED_API_KEY:
    logger.warning("FRED API key not found in environment variables")
else:
    logger.info(f"FRED API key loaded: {FRED_API_KEY[:10]}...")

try:
    from backend.core.fetchers.macro import fred_client
    HAS_FRED_CLIENT = True
except ImportError:
    HAS_FRED_CLIENT = False

logger = logging.getLogger(__name__)

class FedService:
    """
    Service class to interact with the FRED API, with caching support.
    """
    
    # Current valid series mappings (no deprecated entries)
    CURRENT_SERIES_MAP = {
        # Currency pairs - only valid, current mappings
        "DEXHUUS": "DEXHUNUS",   # HUF/USD - correct ID
        "DEXCZUS": "DEXCZKUS",   # CZK/USD - correct ID
        "DEXRUS": "DEXRUBUS",    # RUB/USD - correct ID
    }
    
    # Minimal fallback chains (only for essential series)
    SERIES_FALLBACKS = {
        # Only essential fallbacks with verified availability
        "DEXHUUS": ["DEXHUNUS"],    # HUF/USD
        "DEXCZUS": ["DEXCZKUS"],    # CZK/USD
        "DEXRUS": ["DEXRUBUS"],     # RUB/USD
    }
    
    # Availability matrix for product-level transparency
    AVAILABILITY_MATRIX = {
        # AVAILABLE - Spot prices/rates (no warning needed)
        "DCOILWTICO": {"status": "available", "message": None},
        "DCOILBRENTEU": {"status": "available", "message": None},
        "DEXUSEU": {"status": "available", "message": None},
        "DEXUSUK": {"status": "available", "message": None},
        "DEXJPUS": {"status": "available", "message": None},
        "DEXCHUS": {"status": "available", "message": None},
        "DEXCAUS": {"status": "available", "message": None},
        "DEXUSAL": {"status": "available", "message": None},
        "FEDFUNDS": {"status": "available", "message": None},
        "DFEDTARU": {"status": "available", "message": None},
        "DFEDTARL": {"status": "available", "message": None},
        "IORB": {"status": "available", "message": None},
        
        # LIMITED - Indices/averages with warnings
        "IR14270": {"status": "limited", "message": "Spot GOLD not available in FRED. Returned price index instead."},
        "IR14299": {"status": "limited", "message": "Spot SILVER not available in FRED. Returned price index instead."},
        "PNGASEUUSDM": {"status": "limited", "message": "Global natural gas spot not available. Returned Europe price instead."},
        "PSUGAISAUSDM": {"status": "limited", "message": "Spot sugar not available. Returned international price instead."},
        "PCOFFOTMUSDM": {"status": "limited", "message": "General coffee spot not available. Returned specific grade price instead."},
        "CCUSMA02HUM618N": {"status": "limited", "message": "HUF/USD spot not available. Returned monthly average instead."},
        "CCUSMA02CZM618N": {"status": "limited", "message": "CZK/USD spot not available. Returned monthly average instead."},
        "DEXTRUS": {"status": "limited", "message": "TRY/USD data may have gaps. Use with caution."},
        "DEXRUBUS": {"status": "limited", "message": "RUB/USD data may have gaps. Use with caution."},
        
        # NOT AVAILABLE - Common requests that don't exist in FRED
        "PLATINUM": {"status": "not_available", "message": "Platinum spot price not available in FRED API"},
        "PALLADIUM": {"status": "not_available", "message": "Palladium spot price not available in FRED API"},
        "WHEAT": {"status": "not_available", "message": "Wheat spot price not available in FRED API"},
        "CORN": {"status": "not_available", "message": "Corn spot price not available in FRED API"},
        "SOYBEANS": {"status": "not_available", "message": "Soybeans spot price not available in FRED API"},
        "GASOLINE": {"status": "not_available", "message": "Gasoline spot price not available in FRED API"},
        "BRL": {"status": "not_available", "message": "BRL/USD not available in FRED API"},
        "INR": {"status": "not_available", "message": "INR/USD not available in FRED API"},
        "CNY": {"status": "not_available", "message": "CNY/USD not available in FRED API"},
    }
    
    def __init__(self, cache):
        """
        Initialize the FedService.

        Args:
            cache: Cache backend supporting async get/set with expiration.
        """
        self.cache = cache

    def _fix_series_id(self, series_id: str) -> str:
        """
        Fix common series ID misnaming issues.
        
        Args:
            series_id: Original series ID
        Returns:
            Corrected series ID
        """
        return self.CURRENT_SERIES_MAP.get(series_id, series_id)
    
    def _get_series_fallbacks(self, series_id: str) -> List[str]:
        """
        Get fallback series IDs for a given series.
        
        Args:
            series_id: Original series ID
        Returns:
            List of fallback series IDs to try
        """
        fallbacks = self.SERIES_FALLBACKS.get(series_id, [])
        if not fallbacks:
            return [series_id]
        return fallbacks
    
    def _get_availability_status(self, series_id: str) -> dict:
        """
        Get availability status and warning message for a series.
        
        Args:
            series_id: The series ID
        Returns:
            Dictionary with availability status and warning message
        """
        # Check if series is in availability matrix
        if series_id in self.AVAILABILITY_MATRIX:
            return self.AVAILABILITY_MATRIX[series_id]
        
        # Default to not available for unknown series
        return {"status": "not_available", "message": f"{series_id} not available in FRED API"}
    
    def _get_optimal_frequency(self, series_metadata: Dict[str, Any], requested_frequency: str = None) -> str:
        """
        Determine the optimal frequency based on series metadata and user request.
        
        Args:
            series_metadata: Series metadata from FRED API
            requested_frequency: User-requested frequency
        Returns:
            Optimal frequency to use
        """
        if not series_metadata or "seriess" not in series_metadata or not series_metadata["seriess"]:
            return requested_frequency or "lin"
        
        series_info = series_metadata["seriess"][0]
        series_frequency = series_info.get("frequency_short", "").upper()
        
        # Frequency mapping
        frequency_map = {
            "D": "d",      # Daily
            "W": "w",      # Weekly  
            "M": "m",      # Monthly
            "Q": "q",      # Quarterly
            "A": "a",      # Annual
        }
        
        # If no user request, use series default
        if not requested_frequency:
            return frequency_map.get(series_frequency, "lin")
        
        # If user requested frequency matches series frequency, use it
        if requested_frequency.lower() == frequency_map.get(series_frequency, "").lower():
            return requested_frequency
        
        # If series is monthly and user wants daily, use monthly (series default)
        if series_frequency == "M" and requested_frequency.lower() in ["d", "daily"]:
            logger.info(f"Series {series_info.get('id', 'unknown')} is monthly, using monthly instead of daily")
            return "m"
        
        # If series is quarterly and user wants daily/monthly, use quarterly
        if series_frequency == "Q" and requested_frequency.lower() in ["d", "daily", "m", "monthly"]:
            logger.info(f"Series {series_info.get('id', 'unknown')} is quarterly, using quarterly instead of {requested_frequency}")
            return "q"
        
        # Otherwise, use user requested frequency
        return requested_frequency

    # ------------------- SEARCH -------------------
    async def get_cached_search(self, query: str, limit: int, offset: int) -> Optional[Dict[str, Any]]:
        """
        Get cached search results for a query.

        Args:
            query: Search query string.
            limit: Number of results.
            offset: Offset for pagination.
        Returns:
            Cached search results or None.
        """
        cache_key = f"fed:search:{query}:{limit}:{offset}"
        data = await self.cache.get(cache_key)
        if data:
            return json.loads(data)
        return None

    async def set_cached_search(self, query: str, limit: int, offset: int, results: Dict[str, Any]):
        """
        Cache search results for a query.

        Args:
            query: Search query string.
            limit: Number of results.
            offset: Offset for pagination.
            results: Search results to cache.
        """
        cache_key = f"fed:search:{query}:{limit}:{offset}"
        await self.cache.set(cache_key, json.dumps(results), ttl=CACHE_EXPIRE_SECONDS)

    async def fetch_fred_search(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        Fetch search results from the FRED API.

        Args:
            query: Search query string.
            limit: Number of results.
            offset: Offset for pagination.
        Returns:
            Search results as a dict.
        """
        if not FRED_API_KEY:
            logger.error("FRED API key not configured")
            return StandardResponseBuilder.error(
                "FRED API key not configured",
                meta={"provider": "fred", "cache_status": "error"}
            )
        
        # Only use fred_client if it has the required method
        if HAS_FRED_CLIENT and hasattr(fred_client, "search_series"):
            logger.info(f"Using fred_client for search: {query}")
            return await fred_client.search_series(query=query, limit=limit, offset=offset)
        
        # Fallback to direct HTTPX call
        params = {
            "search_text": query,
            "limit": limit,
            "offset": offset,
            "api_key": FRED_API_KEY,
            "file_type": "json"
        }
        
        logger.info(f"Fetching FRED search results for: {query} (via HTTPX)")
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{FRED_BASE_URL}/series/search", params=params)
            resp.raise_for_status()
            return resp.json()

    # ------------------- SEARCH -------------------
    async def search_series(self, query: str, limit: int = 10, offset: int = 0) -> Dict[str, Any]:
        """
        Search FRED series by query.

        Args:
            query: Search query.
            limit: Number of results.
            offset: Offset for pagination.
        Returns:
            Search results dict.
        """
        try:
            cached = await self.get_cached_search(query, limit, offset)
            if cached:
                logger.debug(f"Using cached search results for: {query}")
                return StandardResponseBuilder.success(
                    cached,
                    meta={"provider": "fred", "cache_status": "cached", "mcp_ready": True}
                )
            
            logger.debug(f"Fetching fresh search results for: {query}")
            data = await self.fetch_fred_search(query, limit, offset)
            
            # Check if fetch_fred_search returned an error response
            if data.get("status") == "error":
                return data
            
            await self.set_cached_search(query, limit, offset, data)
            return StandardResponseBuilder.success(
                data,
                meta={"provider": "fred", "cache_status": "fresh", "mcp_ready": True}
            )
        except Exception as e:
            logger.error(f"Error searching FRED series for '{query}': {e}", exc_info=True)
            return StandardResponseBuilder.error(
                f"Failed to search FRED series: {str(e)}",
                meta={"provider": "fred", "cache_status": "error", "mcp_ready": True}
            )

    # ------------------- RELATED SERIES -------------------
    async def get_related_series(self, series_id: str) -> Dict[str, Any]:
        """
        Get related FRED series for a specific series.

        Args:
            series_id: The FRED series ID.
        Returns:
            Related series dict.
        """
        try:
            cached = await self.get_cached_related(series_id)
            if cached:
                logger.debug(f"Using cached related series for: {series_id}")
                return StandardResponseBuilder.success(
                    cached,
                    meta={"provider": "fred", "cache_status": "cached", "mcp_ready": True}
                )
            
            logger.debug(f"Fetching fresh related series for: {series_id}")
            
            # Only use fred_client if it has the required method
            if HAS_FRED_CLIENT and hasattr(fred_client, "get_related_series"):
                logger.debug(f"Using fred_client for related series: {series_id}")
                data = await fred_client.get_related_series(series_id)
            else:
                # Fallback to direct HTTPX call
                logger.debug(f"Falling back to HTTPX for {series_id} because fred_client does not implement get_related_series")
                data = await self._fetch_fred_related(series_id)
            
            await self.set_cached_related(series_id, data)
            return StandardResponseBuilder.success(
                data,
                meta={"provider": "fred", "cache_status": "fresh", "mcp_ready": True}
            )
        except Exception as e:
            logger.error(f"Error getting related FRED series for '{series_id}': {e}", exc_info=True)
            return StandardResponseBuilder.error(
                f"Failed to get related series: {str(e)}",
                meta={"provider": "fred", "cache_status": "error", "mcp_ready": True}
            )

    # ------------------- METADATA -------------------
    async def get_cached_metadata(self, series_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached metadata for a FRED series.

        Args:
            series_id: The FRED series ID.
        Returns:
            Cached metadata dict or None.
        """
        cache_key = f"fed:metadata:{series_id}"
        data = await self.cache.get(cache_key)
        if data:
            return json.loads(data)
        return None

    async def set_cached_metadata(self, series_id: str, data: Dict[str, Any]):
        """
        Cache metadata for a FRED series.

        Args:
            series_id: The FRED series ID.
            data: Metadata dict to cache.
        """
        cache_key = f"fed:metadata:{series_id}"
        await self.cache.set(cache_key, json.dumps(data), ttl=CACHE_EXPIRE_SECONDS)

    async def fetch_fred_metadata(self, series_id: str) -> Dict[str, Any]:
        """
        Fetch metadata for a FRED series from the API.

        Args:
            series_id: The FRED series ID.
        Returns:
            Metadata dict.
        """
        if not FRED_API_KEY:
            logger.error("FRED API key not configured")
            return StandardResponseBuilder.error(
                "FRED API key not configured",
                meta={"provider": "fred", "cache_status": "error"}
            )
        
        # Only use fred_client if it has the required method
        if HAS_FRED_CLIENT and hasattr(fred_client, "get_series_metadata"):
            logger.info(f"Using fred_client for {series_id}")
            return await fred_client.get_series_metadata(series_id)
        
        # Fallback to direct HTTPX call
        logger.info(f"Falling back to HTTPX for {series_id} because fred_client does not implement get_series_metadata")
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json"
        }
        
        logger.info(f"Fetching FRED metadata for series: {series_id} (via HTTPX)")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(f"{FRED_BASE_URL}/series", params=params)
            
            # Handle FRED API errors gracefully
            if resp.status_code == 400:
                logger.warning(f"FRED API returned 400 for series {series_id} - series may not exist")
                raise ValueError(f"FRED series '{series_id}' not found or invalid")
            elif resp.status_code == 404:
                logger.warning(f"FRED API returned 404 for series {series_id} - series not found")
                raise ValueError(f"FRED series '{series_id}' not found")
            
            resp.raise_for_status()
            data = resp.json()
            
            # Check if series exists in response
            if not data.get("seriess") or len(data["seriess"]) == 0:
                logger.warning(f"No series data returned for {series_id}")
                raise ValueError(f"FRED series '{series_id}' not found or no data available")
            
            logger.info(f"Successfully fetched FRED metadata for {series_id}")
            return data

    # ------------------- RELATED SERIES -------------------
    async def get_cached_related(self, series_id: str) -> Optional[Dict[str, Any]]:
        """
        Get cached related series for a FRED series.

        Args:
            series_id: The FRED series ID.
        Returns:
            Cached related series dict or None.
        """
        cache_key = f"fed:related:{series_id}"
        data = await self.cache.get(cache_key)
        if data:
            return json.loads(data)
        return None

    async def set_cached_related(self, series_id: str, data: Dict[str, Any]):
        """
        Cache related series for a FRED series.

        Args:
            series_id: The FRED series ID.
            data: Related series dict to cache.
        """
        cache_key = f"fed:related:{series_id}"
        await self.cache.set(cache_key, json.dumps(data), ttl=CACHE_EXPIRE_SECONDS)

    async def _fetch_fred_related(self, series_id: str) -> Dict[str, Any]:
        """
        Fetch related series for a FRED series from the API.
        Uses a 3-step process: get tags -> get related tags -> get series with related tags.

        Args:
            series_id: The FRED series ID.
        Returns:
            Related series dict.
        """
        if not FRED_API_KEY:
            raise ValueError("FRED API key not configured")
        
        # Only use fred_client if it has the required method
        if HAS_FRED_CLIENT and hasattr(fred_client, "get_related_series"):
            logger.info(f"Using fred_client for related series: {series_id}")
            return await fred_client.get_related_series(series_id)
        
        # Fallback to direct HTTPX call - 3-step process
        logger.info(f"Falling back to HTTPX for {series_id} because fred_client does not implement get_related_series")
        logger.info(f"Fetching FRED related series for: {series_id} (via HTTPX)")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Step 1: Get tags for the series
            tags_params = {
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json"
            }
            
            logger.info(f"Step 1: Getting tags for series {series_id}")
            tags_resp = await client.get(f"{FRED_BASE_URL}/series/tags", params=tags_params)
            tags_resp.raise_for_status()
            tags_data = tags_resp.json()
            
            if not tags_data.get("tags"):
                logger.warning(f"No tags found for series {series_id}")
                return {"seriess": []}
            
            # Step 2: Get related tags
            tag_names = ";".join([tag["name"] for tag in tags_data["tags"][:5]])  # Limit to first 5 tags
            related_tags_params = {
                "tag_names": tag_names,
                "api_key": FRED_API_KEY,
                "file_type": "json"
            }
            
            logger.info(f"Step 2: Getting related tags for: {tag_names}")
            related_tags_resp = await client.get(f"{FRED_BASE_URL}/related_tags", params=related_tags_params)
            related_tags_resp.raise_for_status()
            related_tags_data = related_tags_resp.json()
            
            if not related_tags_data.get("tags"):
                logger.warning(f"No related tags found for series {series_id}")
                return {"seriess": []}
            
            # Step 3: Get series with related tags (with popularity filtering)
            related_tag_names = ";".join([tag["name"] for tag in related_tags_data["tags"][:3]])  # Limit to first 3 related tags
            series_params = {
                "tag_names": related_tag_names,
                "api_key": FRED_API_KEY,
                "file_type": "json",
                "limit": 20  # Get more results for filtering
            }
            
            logger.info(f"Step 3: Getting series with related tags: {related_tag_names}")
            series_resp = await client.get(f"{FRED_BASE_URL}/tags/series", params=series_params)
            series_resp.raise_for_status()
            series_data = series_resp.json()
            
            # Filter by popularity and remove original series
            if "seriess" in series_data:
                original_count = len(series_data["seriess"])
                min_popularity = 0  # Default to 0 (no filtering)
                filtered_series = []
                seen_ids = {series_id}
                
                for series in series_data["seriess"]:
                    if (series["id"] not in seen_ids and 
                        series.get("popularity", 0) >= min_popularity):
                        filtered_series.append(series)
                        seen_ids.add(series["id"])
                
                # Sort by popularity (descending) and limit results
                filtered_series.sort(key=lambda x: x.get("popularity", 0), reverse=True)
                series_data["seriess"] = filtered_series[:15]  # Top 15 results
                series_data["filtered_by_popularity"] = True
                series_data["min_popularity"] = min_popularity
                series_data["original_count"] = original_count
                series_data["filtered_count"] = len(filtered_series)
            else:
                # Ensure original_count and filtered_count are always present
                series_data["original_count"] = 0
                series_data["filtered_count"] = 0
            
            return series_data

    # ------------------- SERIES METADATA -------------------
    async def get_series_metadata(self, series_id: str) -> Dict[str, Any]:
        """
        Retrieve series metadata, using cache if available.

        Args:
            series_id: The FRED series ID.
        Returns:
            Series metadata dict.
        """
        try:
            cached = await self.get_cached_metadata(series_id)
            if cached:
                logger.debug(f"Using cached metadata for {series_id}")
                return StandardResponseBuilder.success(
                    cached,
                    meta={"provider": "fred", "cache_status": "cached", "mcp_ready": True}
                )
            
            logger.debug(f"Fetching fresh metadata for {series_id}")
            data = await self.fetch_fred_metadata(series_id)
            
            # Check if fetch_fred_metadata returned an error response
            if data.get("status") == "error":
                return data
            
            await self.set_cached_metadata(series_id, data)
            return StandardResponseBuilder.success(
                data,
                meta={"provider": "fred", "cache_status": "fresh", "mcp_ready": True}
            )
        except Exception as e:
            logger.error(f"Service internal error getting series metadata for {series_id}: {e}", exc_info=True)
            return StandardResponseBuilder.error(
                f"Failed to get series metadata: {str(e)}",
                meta={"provider": "fred", "cache_status": "error", "mcp_ready": True}
            )

    # ------------------- SERIES OBSERVATIONS -------------------
    async def get_series_observations(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None,
        units: Optional[str] = None,
        limit: Optional[int] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Retrieve series observations (time series data) from FRED API, with caching.

        Args:
            series_id: The FRED series ID.
            start_date: Start date in YYYY-MM-DD format.
            end_date: End date in YYYY-MM-DD format.
            frequency: Data frequency (e.g., 'm', 'q', 'a').
            units: Data units (e.g., 'lin', 'chg').
            limit: Maximum number of observations to return.
            force_refresh: If True, bypass the cache.
        Returns:
            Series observations dict.
        """
        # Check availability status first
        availability = self._get_availability_status(series_id)
        if availability["status"] == "not_available":
            return StandardResponseBuilder.error(
                availability["message"],
                meta={"provider": "fred", "cache_status": "error", "mcp_ready": True}
            )
        
        # Fix series ID if needed
        fixed_series_id = self._fix_series_id(series_id)
        if fixed_series_id != series_id:
            logger.info(f"Fixed series ID: {series_id} -> {fixed_series_id}")
        
        # Get series metadata to determine optimal frequency
        try:
            metadata = await self.get_series_metadata(fixed_series_id)
            optimal_frequency = self._get_optimal_frequency(metadata, frequency)
            if optimal_frequency != frequency:
                logger.info(f"Using optimal frequency: {frequency} -> {optimal_frequency}")
                frequency = optimal_frequency
        except Exception as e:
            logger.warning(f"Could not get metadata for frequency optimization: {e}")
            # Continue with original frequency
        
        # Try fallback series IDs if the main one fails
        fallback_ids = self._get_series_fallbacks(series_id)
        last_error = None
        
        for attempt_id in fallback_ids:
            try:
                # Create cache key for this attempt
                attempt_cache_key = f"fed:observations:{attempt_id}:{start_date}:{end_date}:{frequency}:{units}:{limit}"
                # The _fetch_observations_for_series method now returns MCP-ready response
                return await self._fetch_observations_for_series(
                    attempt_id, start_date, end_date, frequency, units, limit, force_refresh, attempt_cache_key
                )
            except ValueError as e:
                last_error = e
                logger.warning(f"Series {attempt_id} failed: {e}")
                continue
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected error for series {attempt_id}: {e}")
                continue
        
        # If all fallbacks failed, return error response
        if last_error:
            logger.error(f"All fallback attempts failed for series {series_id}: {last_error}")
            return StandardResponseBuilder.error(
                f"No data available for series {series_id}: {str(last_error)}",
                meta={"provider": "fred", "cache_status": "error", "mcp_ready": True}
            )
        else:
            logger.error(f"No data available for series {series_id} or any fallbacks")
            return StandardResponseBuilder.error(
                f"No data available for series {series_id} or any fallbacks",
                meta={"provider": "fred", "cache_status": "error", "mcp_ready": True}
            )
    
    async def _fetch_observations_for_series(
        self,
        series_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        frequency: Optional[str] = None,
        units: Optional[str] = None,
        limit: Optional[int] = None,
        force_refresh: bool = False,
        cache_key: str = None
    ) -> Dict[str, Any]:
        """
        Fetch observations for a specific series ID (helper method for fallback logic).
        """
        if not cache_key:
            cache_key = f"fed:observations:{series_id}:{start_date}:{end_date}:{frequency}:{units}:{limit}"
        if not force_refresh:
            cached = await self.cache.get(cache_key)
            if cached:
                return json.loads(cached)
        if not FRED_API_KEY:
            logger.error("FRED API key not configured")
            return StandardResponseBuilder.error(
                "FRED API key not configured",
                meta={"provider": "fred", "cache_status": "error"}
            )
        
        # Only use fred_client if it has the required method
        if HAS_FRED_CLIENT and hasattr(fred_client, "get_series_observations"):
            logger.info(f"Using fred_client for observations: {series_id}")
            data = await fred_client.get_series_observations(
                series_id, start_date, end_date, frequency, units, limit
            )
        else:
            # Fallback to direct HTTPX call
            params = {
                "series_id": series_id,
                "api_key": FRED_API_KEY,
                "file_type": "json"
            }
            if start_date:
                params["observation_start"] = start_date
            if end_date:
                params["observation_end"] = end_date
            if frequency:
                params["frequency"] = frequency
            if units:
                params["units"] = units
            if limit:
                params["limit"] = limit
            
            logger.info(f"Fetching FRED observations for: {series_id} (via HTTPX)")
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f"{FRED_BASE_URL}/series/observations", params=params)
                
                # Handle FRED API errors gracefully
                if resp.status_code == 400:
                    data = resp.json()
                    error_msg = data.get("error_message", "Unknown error")
                    if "frequency" in error_msg.lower():
                        # Retry without frequency parameter
                        logger.info(f"FRED API error: Frequency parameter error for {series_id}, retrying without frequency")
                        params_no_freq = {k: v for k, v in params.items() if k != "frequency"}
                        resp = await client.get(f"{FRED_BASE_URL}/series/observations", params=params_no_freq)
                        resp.raise_for_status()
                        data = resp.json()
                        # Add frequency fallback info
                        data["frequency_fallback"] = {
                            "requested_freq": frequency,
                            "actual_freq": "original",
                            "fallback_occurred": True,
                            "fallback_description": f"Requested frequency '{frequency}' not supported, using original frequency"
                        }
                    else:
                        logger.warning(f"FRED API error: Series {series_id} not found or invalid (400): {error_msg}")
                        return {
                            "status": "error",
                            "series_id": series_id,
                            "message": "not found or invalid"
                        }
                elif resp.status_code == 404:
                    logger.warning(f"FRED API error: Series {series_id} not found (404)")
                    return {
                        "status": "error",
                        "series_id": series_id,
                        "message": "not found or invalid"
                    }
                else:
                    resp.raise_for_status()
                    data = resp.json()
                    if "frequency" in data.get("error_message", "").lower():
                        requested_freq = frequency if frequency else "default"
                        logger.warning(f"Frequency '{requested_freq}' not supported for {series_id}, falling back to series default frequency")
                        # Remove frequency parameter and retry
                        params_without_freq = {k: v for k, v in params.items() if k != "frequency"}
                        resp = await client.get(f"{FRED_BASE_URL}/series/observations", params=params_without_freq)
                        resp.raise_for_status()
                        data = resp.json()
                        # Add fallback information to response
                        if "observations" in data and data["observations"]:
                            # Get series frequency from first observation or metadata
                            actual_freq = data.get("frequency", "original")
                            data["frequency_fallback"] = {
                                "requested": requested_freq,
                                "actual": actual_freq,
                                "fallback_occurred": True,
                                "fallback_description": f"{requested_freq} → {actual_freq}",
                                "message": f"Series {series_id} does not support frequency '{requested_freq}', using {actual_freq} frequency"
                            }
                    else:
                        resp.raise_for_status()
                        data = resp.json()
        
        # Normalize observations data
        if "observations" in data:
            data["observations"] = self._normalize_observations(data["observations"])
        
        # Add series ID fix info to response (only if this is the main method, not fallback)
        # This will be handled in the main get_series_observations method
        
        # Add availability status and warning message
        availability = self._get_availability_status(series_id)
        if availability["status"] == "limited":
            data["status"] = "warning"
            data["message"] = availability["message"]
        elif availability["status"] == "not_available":
            data["status"] = "error"
            data["message"] = availability["message"]
        else:
            data["status"] = "success"
        
        await self.cache.set(cache_key, json.dumps(data), ttl=CACHE_EXPIRE_SECONDS)
        
        # Return MCP-ready response
        if data.get("status") == "success":
            return StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.FRED,
                data=data,
                series_id=series_id,
                cache_status=CacheStatus.FRESH if not force_refresh else CacheStatus.FRESH
            )
        else:
            return StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.FRED,
                message=data.get("message", "Unknown error"),
                error_code="FRED_API_ERROR",
                series_id=series_id
            )

    # ------------------- UTILITY FUNCTIONS -------------------
    def _normalize_fred_value(self, value: str) -> float | None:
        """
        Normalize FRED values, converting "." to None and strings to floats.
        
        Args:
            value: Raw value from FRED API
        Returns:
            Normalized float value or None for missing data
        """
        if value == "." or value == "" or value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def _normalize_observations(self, observations: list) -> list:
        """
        Normalize a list of observations with enhanced analytics.
        
        Args:
            observations: List of observation dictionaries
        Returns:
            Normalized observations with proper value types and analytics
        """
        normalized = []
        missing_count = 0
        valid_count = 0
        valid_values = []
        
        for obs in observations:
            original_value = obs.get("value")
            normalized_value = self._normalize_fred_value(original_value)
            
            # Skip observations with null/missing values BEFORE adding to list
            if normalized_value is None or normalized_value in (".", "", "N/A") or original_value in (".", "", "N/A", None):
                missing_count += 1
                continue
            
            normalized_obs = obs.copy()
            normalized_obs["value"] = normalized_value
            
            valid_count += 1
            valid_values.append(normalized_value)
                
            normalized.append(normalized_obs)
        
        # Calculate enhanced analytics
        analytics = {}
        if valid_values and len(valid_values) > 1:
            # Moving averages (5-period and 20-period)
            analytics["moving_averages"] = self._calculate_moving_averages(valid_values)
            
            # Percent changes
            analytics["percent_changes"] = self._calculate_percent_changes(valid_values)
            
            # Basic statistics
            analytics["statistics"] = {
                "mean": round(sum(valid_values) / len(valid_values), 4),
                "min": round(min(valid_values), 4),
                "max": round(max(valid_values), 4),
                "volatility": round(self._calculate_volatility(valid_values), 4)
            }
        
        # Add normalization statistics with analytics
        if observations:
            normalization_stats = {
                "total_observations": len(observations),
                "valid_values": valid_count,
                "missing_values": missing_count,
                "missing_percentage": round((missing_count / len(observations)) * 100, 2) if observations else 0,
                "analytics": analytics
            }
            # Add stats to the first observation for easy access
            if normalized:
                normalized[0]["_normalization_stats"] = normalization_stats
        
        return normalized
    
    def _calculate_moving_averages(self, values: list) -> dict:
        """Calculate 5-period and 20-period moving averages."""
        if len(values) < 5:
            return {"ma5": None, "ma20": None}
        
        ma5 = round(sum(values[-5:]) / 5, 4) if len(values) >= 5 else None
        ma20 = round(sum(values[-20:]) / 20, 4) if len(values) >= 20 else None
        
        return {"ma5": ma5, "ma20": ma20}
    
    def _calculate_percent_changes(self, values: list) -> dict:
        """Calculate period-over-period and year-over-year percent changes."""
        if len(values) < 2:
            return {"period_change": None, "yoy_change": None}
        
        # Period-over-period change (last vs previous)
        period_change = round(((values[-1] - values[-2]) / values[-2]) * 100, 2) if values[-2] != 0 else None
        
        # Year-over-year change (if we have enough data)
        yoy_change = None
        if len(values) >= 12:  # Assuming monthly data
            yoy_change = round(((values[-1] - values[-12]) / values[-12]) * 100, 2) if values[-12] != 0 else None
        
        return {"period_change": period_change, "yoy_change": yoy_change}
    
    def _calculate_volatility(self, values: list) -> float:
        """Calculate standard deviation as volatility measure."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    # ------------------- CATEGORIES -------------------
    async def get_categories(self, category_id: int = 0) -> Dict[str, Any]:
        """
        Retrieve FRED categories, using cache if available.

        Args:
            category_id: Category ID to browse (0 for root categories)
        Returns:
            Categories dict.
        """
        cache_key = f"fed:categories:{category_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return StandardResponseBuilder.success(
                json.loads(cached),
                meta={"provider": "fred", "cache_status": "cached", "mcp_ready": True}
            )
        if not FRED_API_KEY:
            logger.error("FRED API key not configured")
            return StandardResponseBuilder.error(
                "FRED API key not configured",
                meta={"provider": "fred", "cache_status": "error", "mcp_ready": True}
            )
        
        # Only use fred_client if it has the required method
        if HAS_FRED_CLIENT and hasattr(fred_client, "get_categories"):
            logger.info(f"Using fred_client for categories: {category_id}")
            data = await fred_client.get_categories(category_id)
        else:
            # Fallback to direct HTTPX call
            params = {
                "category_id": category_id,
                "api_key": FRED_API_KEY,
                "file_type": "json"
            }
            
            logger.info(f"Fetching FRED categories for category_id={category_id} (via HTTPX)")
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.get(f"{FRED_BASE_URL}/category", params=params)
                resp.raise_for_status()
                data = resp.json()
                
                # Enhance with additional metadata if categories exist
                if "categories" in data and data["categories"]:
                    enhanced_categories = []
                    for category in data["categories"]:
                        enhanced_category = category.copy()
                        
                        # Get series count for this category
                        try:
                            series_params = {
                                "category_id": category["id"],
                                "api_key": FRED_API_KEY,
                                "file_type": "json",
                                "limit": 1  # Just to get count
                            }
                            series_resp = await client.get(f"{FRED_BASE_URL}/category/series", params=series_params)
                            if series_resp.status_code == 200:
                                series_data = series_resp.json()
                                enhanced_category["series_count"] = series_data.get("count", 0)
                            else:
                                enhanced_category["series_count"] = 0
                        except Exception as e:
                            logger.warning(f"Service internal error: Could not fetch series count for category {category['id']}: {e}")
                            enhanced_category["series_count"] = 0
                        
                        # Get child categories
                        try:
                            children_params = {
                                "category_id": category["id"],
                                "api_key": FRED_API_KEY,
                                "file_type": "json"
                            }
                            children_resp = await client.get(f"{FRED_BASE_URL}/category/children", params=children_params)
                            if children_resp.status_code == 200:
                                children_data = children_resp.json()
                                enhanced_category["children"] = children_data.get("categories", [])
                            else:
                                enhanced_category["children"] = []
                        except Exception as e:
                            logger.warning(f"Service internal error: Could not fetch children for category {category['id']}: {e}")
                            enhanced_category["children"] = []
                        
                        enhanced_categories.append(enhanced_category)
                    
                    data["categories"] = enhanced_categories
        await self.cache.set(cache_key, json.dumps(data), ttl=CACHE_EXPIRE_SECONDS)
        return StandardResponseBuilder.success(
            data,
            meta={"provider": "fred", "cache_status": "fresh", "mcp_ready": True}
        )
"""
Euribor Service

Provides methods to fetch and cache Euribor data from ECB/DBnomics sources.
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime

from backend.utils.cache_service import CacheService
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus
from backend.core.fetchers.macro.ecb_client.specials.euribor_client import (
    fetch_official_euribor_rates,
    get_latest_euribor_rates,
)

logger = logging.getLogger(__name__)


class EuriborService:
    """
    Service class for handling Euribor data retrieval and caching.
    """

    def __init__(self, cache: Optional[CacheService] = None):
        self.cache = cache or CacheService()
        self.provider = "euribor"

    def _error(self, message: str, error_code: str, meta_extra: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Helper method for consistent MCP-ready error responses.
        """
        meta = {
            "provider": self.provider,
            "mcp_ready": True,
            "cache_status": "error",
            "data_source": "euribor_live",
            "last_updated": datetime.utcnow().isoformat() + "Z",
            "error_code": error_code,
            "cache_fallback_available": True,
            **(meta_extra or {})
        }
        return StandardResponseBuilder.error(message, meta=meta)

    def _generate_cache_key(self, method: str, **params) -> str:
        sorted_params = sorted(params.items()) if params else []
        param_str = ":".join([f"{k}={v}" for k, v in sorted_params if v is not None])
        return f"{self.provider}:{method}:{param_str}" if param_str else f"{self.provider}:{method}"

    def _normalize_rate_value(self, value: Any) -> Any:
        if isinstance(value, (float, int)):
            return value
        if isinstance(value, str):
            try:
                cleaned = value.strip().rstrip('%').strip().replace(',', '.')
                return float(cleaned)
            except Exception:
                logger.warning(f"Failed to normalize rate value: {value}")
                return value
        return value

    async def get_euribor_rate(self, tenor: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get a single Euribor rate for the specified tenor.
        """
        logger.info(f"Fetching Euribor rate | tenor={tenor}, force_refresh={force_refresh}")
        
        # Special handling for "curve" tenor
        if tenor == "curve":
            return await self.get_euribor_curve(force_refresh=force_refresh)
        
        cache_key = self._generate_cache_key("rate", tenor=tenor)

        try:
            # Cache lookup
            if not force_refresh:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    meta = cached_result.get("meta", {})
                    meta.update({
                        "mcp_ready": True,
                        "cache_status": "cached",
                        "data_source": "euribor_cache",
                        "last_updated": datetime.utcnow().isoformat() + "Z"
                    })
                    cached_result["meta"] = meta
                    return cached_result

            # Fresh fetch
            rate_data = await get_latest_euribor_rates(tenors=[tenor])
            normalized = {k: self._normalize_rate_value(v) for k, v in (rate_data or {}).items()}

            result = StandardResponseBuilder.success(
                normalized,
                meta={
                    "provider": self.provider,
                    "mcp_ready": True,
                    "cache_status": "fresh",
                    "data_source": "euribor_live",
                    "symbol": f"EURIBOR_{tenor}",
                    "data_type": "euribor_rate",
                    "series_id": f"euribor_rate_{tenor}",
                    "title": f"Euribor {tenor} Rate",
                    "last_updated": datetime.utcnow().isoformat() + "Z",
                    "cache_fallback_available": True,
                }
            )
            await self.cache.set(cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"Error fetching Euribor rate for {tenor}: {e}", exc_info=True)
            return self._error(
                f"Failed to fetch Euribor rate for {tenor}: {str(e)}",
                error_code="ECB_FETCH_ERROR",
                meta_extra={"tenor": tenor, "input_snapshot": {"tenor": tenor, "force_refresh": force_refresh, "cache_key": cache_key}}
            )

    async def get_euribor_curve(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        """
        Get Euribor curve for a date range.
        """
        logger.info(f"Fetching Euribor curve | start_date={start_date}, end_date={end_date}, force_refresh={force_refresh}")
        cache_key = self._generate_cache_key("curve", start_date=start_date, end_date=end_date)

        try:
            # Cache lookup
            if not force_refresh:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    meta = cached_result.get("meta", {})
                    meta.update({
                        "mcp_ready": True,
                        "cache_status": "cached",
                        "data_source": "euribor_cache",
                        "last_updated": datetime.utcnow().isoformat() + "Z"
                    })
                    cached_result["meta"] = meta
                    return cached_result

            # Fresh fetch - use the working get_latest_euribor_rates function
            from backend.core.fetchers.macro.ecb_client.specials.euribor_client import get_latest_euribor_rates
            
            # Get all available tenors
            all_tenors = ["1W", "1M", "3M", "6M", "12M"]
            logger.info(f"Fetching Euribor rates for tenors: {all_tenors}")
            
            try:
                latest_rates = await get_latest_euribor_rates(tenors=all_tenors)
                logger.info(f"get_latest_euribor_rates returned: {latest_rates}")
            except Exception as e:
                logger.error(f"get_latest_euribor_rates failed: {e}")
                raise
            
            if latest_rates:
                # Normalize the rates
                normalized_rates = {}
                for tenor, rate in latest_rates.items():
                    normalized_rates[tenor] = self._normalize_rate_value(rate)
                
                curve_data = {
                    "curve": normalized_rates,
                    "source": "web_scraping",
                    "last_updated": datetime.now().isoformat()
                }
                logger.info(f"Successfully fetched Euribor curve with {len(normalized_rates)} rates: {list(normalized_rates.keys())}")
            else:
                raise Exception("No data returned from get_latest_euribor_rates")

            result = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.EMMI,
                data=curve_data,
                series_id=f"euribor_curve:{start_date or 'default'}-{end_date or 'default'}",
                frequency="daily",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
            await self.cache.set(cache_key, result, ttl=3600)
            return result

        except Exception as e:
            logger.error(f"Error fetching Euribor curve: {e}", exc_info=True)
            return self._error(
                f"Failed to fetch Euribor curve: {str(e)}",
                error_code="SCRAPER_FAILED",
                meta_extra={"start_date": start_date, "end_date": end_date,
                            "input_snapshot": {"start_date": start_date, "end_date": end_date,
                                               "force_refresh": force_refresh, "cache_key": cache_key}}
            )
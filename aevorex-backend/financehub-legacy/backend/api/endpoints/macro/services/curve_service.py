"""
Curve Service

Yield curve logic and calculations.
Handles yield curve data processing, analytics, and comparisons.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx
import csv
import io
from backend.utils.logger_config import get_logger
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus

logger = get_logger(__name__)


class CurveService:
    """Service for yield curve logic and calculations."""

    def __init__(self, cache=None):
        self.cache = cache
        self.provider = "ecb_curve"

    @staticmethod
    async def get_curve_data(provider: str, days: int = 30, api_key: str = "free", macro_service=None) -> Dict[str, Any]:
        """
        Get yield curve data for the specified provider.
        
        Args:
            provider: Curve provider ("ust", "ecb", etc.)
            days: Number of days for historical data
            api_key: API key for data fetching
            macro_service: Macro service instance
            
        Returns:
            Dictionary with curve data and metadata
        """
        if provider.lower() == "ust":
            return await CurveService._fetch_ust_yield_curve()
        else:
            logger.error(f"get_curve_data not implemented for provider: {provider}")
            raise NotImplementedError(f"Real API integration not implemented for {provider} yield curve data")

    @staticmethod
    async def _fetch_ust_yield_curve() -> Dict[str, Any]:
        """
        Fetch UST yield curve data from Treasury CSV endpoint.
        
        Returns:
            Dictionary with UST curve data and metadata
        """
        logger.info("Fetching UST yield curve data from Treasury CSV endpoint")
        
        # Treasury CSV endpoint
        treasury_url = "https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2025/all?field_tdr_date_value=2025&type=daily_treasury_yield_curve&page&_format=csv"
        
        # Maturity mapping from Treasury column names to simplified labels
        maturity_map = {
            "1 Mo": "1M", "1.5 Month": "1.5M", "2 Mo": "2M", "3 Mo": "3M", "4 Mo": "4M", "6 Mo": "6M",
            "1 Yr": "1Y", "2 Yr": "2Y", "3 Yr": "3Y", "5 Yr": "5Y", "7 Yr": "7Y", 
            "10 Yr": "10Y", "20 Yr": "20Y", "30 Yr": "30Y"
        }
        
        curve = {}
        last_updated = None
        
        try:
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
                response = await client.get(treasury_url)
                
                if response.status_code == 200:
                    csv_content = response.text
                    
                    # Parse CSV data
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    
                    # Get the latest row (first data row after header)
                    latest_row = None
                    for row in csv_reader:
                        if row.get('Date') and row.get('Date') != 'Date':  # Skip header
                            latest_row = row
                            break
                    
                    if latest_row:
                        # Parse date
                        try:
                            date_str = latest_row['Date']
                            # Handle MM/DD/YYYY format
                            last_updated = datetime.strptime(date_str, '%m/%d/%Y').date()
                        except Exception as e:
                            logger.warning(f"Failed to parse date '{date_str}': {e}")
                            last_updated = datetime.now().date()
                        
                        # Extract yield data for each maturity
                        for treasury_col, label in maturity_map.items():
                            if treasury_col in latest_row:
                                try:
                                    value = float(latest_row[treasury_col])
                                    curve[label] = value
                                    logger.debug(f"UST: Successfully parsed {label}: {value}%")
                                except (ValueError, TypeError) as e:
                                    logger.warning(f"UST: Failed to parse {label} from {treasury_col}: {e}")
                                    continue
                    
                    metadata = {
                        "url": treasury_url,
                        "description": "US Treasury yield curve - daily treasury rates",
                        "currency": "USD",
                        "data_type": "treasury_yields",
                        "source": "US Treasury CSV API",
                        "last_updated": last_updated.isoformat() if last_updated else datetime.now().isoformat()
                    }
                    
                    if curve:
                        logger.info(f"UST: Successfully fetched yield curve data with {len(curve)} maturities: {list(curve.keys())}")
                        return {
                            "status": "success",
                            "data": {
                                "curve": curve,
                                "metadata": metadata
                            }
                        }
                    else:
                        raise RuntimeError("UST CSV endpoint did not return any yield curve data")
                        
                else:
                    logger.error(f"UST: Failed to fetch data: Status={response.status_code}, Body={response.text[:200]}")
                    raise RuntimeError(f"UST CSV endpoint returned status {response.status_code}")
                    
        except Exception as e:
            logger.error(f"UST: Error fetching yield curve data: {e}")
            raise RuntimeError(f"UST CSV fetch failed: {e}")

    def _error(self, message: str, meta_extra: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Helper method for consistent error responses.
        
        Args:
            message: Error message
            meta_extra: Additional meta fields
            
        Returns:
            Standardized error response
        """
        meta = {
            "provider": self.provider,
            "cache_status": "error",
            "last_updated": datetime.now().isoformat(),
            **(meta_extra or {})
        }
        if "series_id" not in meta:
            meta["series_id"] = "error"
        if "title" not in meta:
            meta["title"] = "Error Response"
        return StandardResponseBuilder.error(message, meta=meta)

    def _generate_cache_key(self, method: str, **params) -> str:
        """
        Generate deterministic cache key for method and parameters.
        
        Args:
            method: Method name (e.g., 'spot_rates', 'forward_rates')
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

    async def calculate_spot_rates(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate spot rates from yield curve data.
        Expects: curve_data = {'maturities': [...], 'yields': [...]}
        Returns: Standardized response with normalized spot rates sorted by maturity.
        """
        logger.info("Calculating spot rates from curve data")
        
        # Generate deterministic cache key
        cache_key = self._generate_cache_key("spot_rates", curve_data=str(curve_data))
        
        try:
            # Check cache first
            if self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"Cache HIT for spot rates: {cache_key}")
                    cached_result["meta"]["cache_status"] = "cached"
                    return cached_result
                else:
                    logger.info(f"Cache MISS for spot rates: {cache_key}")
            else:
                logger.info("No cache available - calculating fresh spot rates...")
            
            maturities = curve_data.get("maturities")
            yields = curve_data.get("yields")
            if maturities is None or yields is None or len(maturities) != len(yields):
                logger.warning(f"Invalid curve data for spot rate calculation - maturities: {maturities}, yields: {yields}")
                return self._error("Invalid curve data for spot rate calculation", {
                    "series_id": "spot_rates",
                    "title": "Spot Rates Calculation Error",
                    "input_snapshot": {
                        "maturities_count": len(maturities) if maturities else 0,
                        "yields_count": len(yields) if yields else 0,
                        "has_maturities": maturities is not None,
                        "has_yields": yields is not None
                    }
                })
            
            # Pair and sort by maturity
            pairs = sorted(zip(maturities, yields), key=lambda x: x[0])
            normalized = [{"maturity": float(m), "spot_rate": float(y)} for m, y in pairs]
            
            result = StandardResponseBuilder.success(
                {"spot_rates": normalized},
                meta={
                    "provider": self.provider,
                    "cache_status": "fresh",
                    "date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "series_id": "spot_rates",
                    "title": "Yield Curve Spot Rates",
                    "curve_points": len(normalized)
                }
            )
            
            # Cache the result for 1 hour (3600 seconds)
            if self.cache:
                await self.cache.set(cache_key, result, ttl=3600)
                logger.info(f"Cached spot rates result: {cache_key}")
            
            logger.info(f"Spot rates calculated for {len(normalized)} maturities")
            return result
            
        except Exception as e:
            logger.error(f"Error in spot rate calculation: {e} | Input: {curve_data}", exc_info=True)
            return self._error(f"Failed to calculate spot rates: {str(e)}", {
                "series_id": "spot_rates",
                "title": "Spot Rates Calculation Error",
                "input_snapshot": {
                    "curve_data_keys": list(curve_data.keys()) if isinstance(curve_data, dict) else "not_dict",
                    "curve_data_type": type(curve_data).__name__
                }
            })

    async def calculate_forward_rates(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate simple forward rates between consecutive maturities.
        Expects: curve_data = {'maturities': [...], 'yields': [...]}
        Returns: Standardized response with forward rates.
        """
        logger.info("Calculating forward rates from curve data")
        
        # Generate deterministic cache key
        cache_key = self._generate_cache_key("forward_rates", curve_data=str(curve_data))
        
        try:
            # Check cache first
            if self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"Cache HIT for forward rates: {cache_key}")
                    cached_result["meta"]["cache_status"] = "cached"
                    return cached_result
                else:
                    logger.info(f"Cache MISS for forward rates: {cache_key}")
            else:
                logger.info("No cache available - calculating fresh forward rates...")
            
            maturities = curve_data.get("maturities")
            yields = curve_data.get("yields")
            if maturities is None or yields is None or len(maturities) != len(yields):
                logger.warning(f"Invalid curve data for forward rate calculation - maturities: {maturities}, yields: {yields}")
                return self._error("Invalid curve data for forward rate calculation", {
                    "series_id": "forward_rates",
                    "title": "Forward Rates Calculation Error",
                    "input_snapshot": {
                        "maturities_count": len(maturities) if maturities else 0,
                        "yields_count": len(yields) if yields else 0,
                        "has_maturities": maturities is not None,
                        "has_yields": yields is not None
                    }
                })
            
            pairs = sorted(zip(maturities, yields), key=lambda x: x[0])
            forward_rates = []
            for i in range(len(pairs) - 1):
                m1, y1 = float(pairs[i][0]), float(pairs[i][1])
                m2, y2 = float(pairs[i+1][0]), float(pairs[i+1][1])
                if m2 == m1:
                    logger.warning(f"Duplicate maturity {m1} encountered in forward rate calculation")
                    continue
                # Simple forward rate approximation (not compounding)
                forward_rate = (y2 * m2 - y1 * m1) / (m2 - m1)
                forward_rates.append({
                    "start_maturity": m1,
                    "end_maturity": m2,
                    "forward_rate": forward_rate
                })
            
            result = StandardResponseBuilder.success(
                {"forward_rates": forward_rates},
                meta={
                    "provider": self.provider,
                    "cache_status": "fresh",
                    "date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "series_id": "forward_rates",
                    "title": "Yield Curve Forward Rates",
                    "curve_points": len(forward_rates)
                }
            )
            
            # Cache the result for 1 hour (3600 seconds)
            if self.cache:
                await self.cache.set(cache_key, result, ttl=3600)
                logger.info(f"Cached forward rates result: {cache_key}")
            
            logger.info(f"Forward rates calculated for {len(forward_rates)} intervals")
            return result
            
        except Exception as e:
            logger.error(f"Error in forward rate calculation: {e} | Input: {curve_data}", exc_info=True)
            return self._error(f"Failed to calculate forward rates: {str(e)}", {
                "series_id": "forward_rates",
                "title": "Forward Rates Calculation Error",
                "input_snapshot": {
                    "curve_data_keys": list(curve_data.keys()) if isinstance(curve_data, dict) else "not_dict",
                    "curve_data_type": type(curve_data).__name__
                }
            })

    async def compare_curves(self, curve1: Dict[str, Any], curve2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare two yield curves for shared maturities.
        Returns maturity, yield1, yield2, and difference for each shared maturity.
        """
        logger.info("Comparing two yield curves")
        
        # Generate deterministic cache key
        cache_key = self._generate_cache_key("compare_curves", curve1=str(curve1), curve2=str(curve2))
        
        try:
            # Check cache first
            if self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"Cache HIT for curve comparison: {cache_key}")
                    cached_result["meta"]["cache_status"] = "cached"
                    return cached_result
                else:
                    logger.info(f"Cache MISS for curve comparison: {cache_key}")
            else:
                logger.info("No cache available - performing fresh curve comparison...")
            
            m1 = curve1.get("maturities")
            y1 = curve1.get("yields")
            m2 = curve2.get("maturities")
            y2 = curve2.get("yields")
            if not (m1 and y1 and m2 and y2):
                logger.warning(f"Missing maturities or yields in curves - curve1: maturities={len(m1) if m1 else 0}, yields={len(y1) if y1 else 0}, curve2: maturities={len(m2) if m2 else 0}, yields={len(y2) if y2 else 0}")
                return self._error("Invalid curve input for comparison", {
                    "series_id": "curve_comparison",
                    "title": "Curve Comparison Error",
                    "input_snapshot": {
                        "curve1_maturities_count": len(m1) if m1 else 0,
                        "curve1_yields_count": len(y1) if y1 else 0,
                        "curve2_maturities_count": len(m2) if m2 else 0,
                        "curve2_yields_count": len(y2) if y2 else 0,
                        "curve1_has_data": bool(m1 and y1),
                        "curve2_has_data": bool(m2 and y2)
                    }
                })
            
            curve1_dict = {float(m): float(y) for m, y in zip(m1, y1)}
            curve2_dict = {float(m): float(y) for m, y in zip(m2, y2)}
            shared_maturities = sorted(set(curve1_dict.keys()) & set(curve2_dict.keys()))
            comparison = []
            for m in shared_maturities:
                v1 = curve1_dict[m]
                v2 = curve2_dict[m]
                comparison.append({
                    "maturity": m,
                    "yield1": v1,
                    "yield2": v2,
                    "difference": v2 - v1
                })
            
            result = StandardResponseBuilder.success(
                {"comparison": comparison},
                meta={
                    "provider": self.provider,
                    "cache_status": "fresh",
                    "date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "series_id": "curve_comparison",
                    "title": "Yield Curve Comparison",
                    "curve_points": len(comparison)
                }
            )
            
            # Cache the result for 1 hour (3600 seconds)
            if self.cache:
                await self.cache.set(cache_key, result, ttl=3600)
                logger.info(f"Cached curve comparison result: {cache_key}")
            
            logger.info(f"Compared curves at {len(comparison)} shared maturities")
            return result
            
        except Exception as e:
            logger.error(f"Error comparing yield curves: {e} | Input: curve1={curve1}, curve2={curve2}", exc_info=True)
            return self._error(f"Failed to compare yield curves: {str(e)}", {
                "series_id": "curve_comparison",
                "title": "Curve Comparison Error",
                "input_snapshot": {
                    "curve1_keys": list(curve1.keys()) if isinstance(curve1, dict) else "not_dict",
                    "curve2_keys": list(curve2.keys()) if isinstance(curve2, dict) else "not_dict",
                    "curve1_type": type(curve1).__name__,
                    "curve2_type": type(curve2).__name__
                }
            })

    async def get_curve_analytics(self, curve_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compute slope, average, max, min, and curvature of the yield curve.
        Slope: 10Y - 2Y. Curvature: 10Y + 2Y - 2*5Y.
        """
        logger.info("Calculating curve analytics")
        
        # Generate deterministic cache key
        cache_key = self._generate_cache_key("curve_analytics", curve_data=str(curve_data))
        
        try:
            # Check cache first
            if self.cache:
                cached_result = await self.cache.get(cache_key)
                if cached_result:
                    logger.info(f"Cache HIT for curve analytics: {cache_key}")
                    cached_result["meta"]["cache_status"] = "cached"
                    return cached_result
                else:
                    logger.info(f"Cache MISS for curve analytics: {cache_key}")
            else:
                logger.info("No cache available - calculating fresh curve analytics...")
            
            maturities = curve_data.get("maturities")
            yields = curve_data.get("yields")
            if maturities is None or yields is None or len(maturities) != len(yields):
                logger.warning(f"Invalid curve data for analytics - maturities: {maturities}, yields: {yields}")
                return self._error("Invalid curve data for analytics", {
                    "series_id": "curve_analytics",
                    "title": "Curve Analytics Error",
                    "input_snapshot": {
                        "maturities_count": len(maturities) if maturities else 0,
                        "yields_count": len(yields) if yields else 0,
                        "has_maturities": maturities is not None,
                        "has_yields": yields is not None
                    }
                })
            
            m_dict = {float(m): float(y) for m, y in zip(maturities, yields)}
            y_values = list(m_dict.values())
            analytics = {
                "average_yield": sum(y_values) / len(y_values) if y_values else None,
                "max_yield": max(y_values) if y_values else None,
                "min_yield": min(y_values) if y_values else None
            }
            # Slope (10Y - 2Y)
            slope = None
            curvature = None
            m_2 = min(m_dict.keys(), key=lambda x: abs(x - 2.0)) if m_dict else None
            m_5 = min(m_dict.keys(), key=lambda x: abs(x - 5.0)) if m_dict else None
            m_10 = min(m_dict.keys(), key=lambda x: abs(x - 10.0)) if m_dict else None
            if m_2 is not None and m_10 is not None:
                slope = m_dict[m_10] - m_dict[m_2]
            if m_2 is not None and m_5 is not None and m_10 is not None:
                curvature = m_dict[m_10] + m_dict[m_2] - 2 * m_dict[m_5]
            analytics["slope_10y_2y"] = slope
            analytics["curvature_10y_5y_2y"] = curvature
            
            result = StandardResponseBuilder.success(
                analytics,
                meta={
                    "provider": self.provider,
                    "cache_status": "fresh",
                    "date": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "series_id": "curve_analytics",
                    "title": "Yield Curve Analytics",
                    "curve_points": len(y_values),
                    "calculation_mode": "approx_nearest",
                    "calculation_details": {
                        "slope_method": "10Y - 2Y (nearest available maturities)",
                        "curvature_method": "10Y + 2Y - 2*5Y (nearest available maturities)",
                        "available_maturities": sorted(m_dict.keys()) if m_dict else []
                    }
                }
            )
            
            # Cache the result for 1 hour (3600 seconds)
            if self.cache:
                await self.cache.set(cache_key, result, ttl=3600)
                logger.info(f"Cached curve analytics result: {cache_key}")
            
            logger.info(f"Curve analytics calculated: {analytics}")
            return result
            
        except Exception as e:
            logger.error(f"Error in curve analytics calculation: {e} | Input: {curve_data}", exc_info=True)
            return self._error(f"Failed to calculate curve analytics: {str(e)}", {
                "series_id": "curve_analytics",
                "title": "Curve Analytics Error",
                "input_snapshot": {
                    "curve_data_keys": list(curve_data.keys()) if isinstance(curve_data, dict) else "not_dict",
                    "curve_data_type": type(curve_data).__name__
                }
            })


__all__ = ["CurveService"]

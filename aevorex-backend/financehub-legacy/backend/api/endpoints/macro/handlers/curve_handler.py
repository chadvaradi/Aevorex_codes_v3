"""
Yield Curve Handler

Provides yield curve data endpoints for US Treasury curves and curve comparison.
ECB yield curve endpoints are available under /ecb/yield-curve/*.

Available endpoints:
- /curve/ust - US Treasury yield curve data
- /curve/compare - Compare ECB vs UST yield curves with mathematical analysis
"""

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import JSONResponse
import logging
from backend.core.services.macro.macro_service import MacroDataService, get_macro_service
from backend.api.endpoints.macro.services.curve_service import CurveService
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus
from backend.utils.cache_service import CacheService
from .ecb_handler import get_ecb_yield_curve

router = APIRouter(
    tags=["Macro"]
)

logger = logging.getLogger(__name__)



@router.get("/ust", summary="US Treasury Yield Curve")
async def get_ust_yield_curve(
    start_date: str = Query(None, description="Start date (ISO format)"),
    end_date: str = Query(None, description="End date (ISO format)"),
    macro_service: MacroDataService = Depends(get_macro_service)
) -> dict:
    """
    Get US Treasury yield curve data.
    Returns the US Treasury yield curve data for the specified date range.
    """
    logger.info(f"Fetching UST yield curve | start_date: {start_date}, end_date: {end_date}")
    
    try:
        # Calculate days from start_date to end_date, default to 30 days
        from datetime import datetime, timedelta
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            days = (end_dt - start_dt).days
        else:
            days = 30  # Default to 30 days
        
        result = await CurveService.get_curve_data("ust", days, "free", macro_service)
        logger.debug(f"UST yield curve data fetched, status: {result.get('status')}")
        
        # Determine cache status based on result metadata
        cache_status = CacheStatus.CACHED if result.get("cached", False) else CacheStatus.FRESH

        # Ensure response follows MCP format
        if result.get("status") == "success":
            mcp_response = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.UST,
                data=result.get("data", result),
                series_id="UST_YIELD_CURVE",
                frequency="daily",
                units="percent",
                cache_status=cache_status
            )
            return JSONResponse(content=mcp_response, status_code=status.HTTP_200_OK)
        else:
            # Service returned error, convert to MCP format
            error_message = result.get("message", "Failed to fetch UST yield curve data")
            if start_date and end_date:
                error_message += f" for period {start_date} to {end_date}"
            mcp_error = StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.UST,
                message=error_message,
                error_code="UST_API_ERROR",
                series_id="UST_YIELD_CURVE"
            )
            return JSONResponse(content=mcp_error, status_code=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error fetching UST yield curve: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.UST,
            message=f"Failed to fetch UST yield curve: {str(e)}",
            error_code="UST_FETCH_ERROR",
            series_id="UST_YIELD_CURVE"
        )
        return JSONResponse(content=error_response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/compare", summary="Compare ECB and UST Yield Curves with Mathematical Analysis")
@router.post("/compare", summary="Compare ECB and UST Yield Curves with Mathematical Analysis")
async def compare_yield_curves(
    curve1: str = Query("ecb", description="First curve to compare"),
    curve2: str = Query("ust", description="Second curve to compare"),
    start_date: str = Query(None, description="Start date (ISO format)"),
    end_date: str = Query(None, description="End date (ISO format)"),
    macro_service: MacroDataService = Depends(get_macro_service)
) -> dict:
    """
    Compare ECB and US Treasury yield curves with mathematical analysis.
    Uses real ECB data from official website and real UST data from FRED API.
    Returns comparison data with yield spreads, curve steepness, and statistical analysis.
    """
    logger.info(f"Comparing yield curves | curve1: {curve1}, curve2: {curve2}, start_date: {start_date}, end_date: {end_date}")
    
    try:
        from datetime import datetime, timedelta

        # Fetch curve1 data
        if curve1 == "ecb":
            try:
                ecb_response = await get_ecb_yield_curve()
                logger.debug("ECB yield curve data fetched from official website")
                # Extract the curve data from the ECB handler response
                if hasattr(ecb_response, 'body'):
                    import json
                    ecb_data = json.loads(ecb_response.body.decode())
                else:
                    ecb_data = ecb_response
                curve1_data = {
                    "status": "success",
                    "source": "ecb_official_website",
                    "curve": ecb_data.get("data", {}).get("curve", {}),
                    "date": ecb_data.get("data", {}).get("metadata", {}).get("last_updated", "unknown"),
                    "cached": ecb_data.get("meta", {}).get("cache_status") == "cached"
                }
            except Exception as e:
                error_response = StandardResponseBuilder.create_macro_error_response(
                    provider=MacroProvider.ECB,
                    message=f"Failed to fetch ECB yield curve data: {str(e)}",
                    error_code="ECB_CURVE_FETCH_ERROR",
                    series_id="CURVE_COMPARISON"
                )
                return JSONResponse(content=error_response, status_code=status.HTTP_400_BAD_REQUEST)
        else:
            if start_date and end_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                days = (end_dt - start_dt).days
            else:
                days = 30
            try:
                curve1_data = await CurveService.get_curve_data(curve1, days, "free", macro_service)
                logger.debug(f"{curve1} yield curve data fetched successfully")
                if curve1_data.get("status") != "success":
                    error_message = curve1_data.get("message", f"Failed to fetch {curve1} yield curve data")
                    error_response = StandardResponseBuilder.create_macro_error_response(
                        provider=MacroProvider.UST,
                        message=error_message,
                        error_code="CURVE_FETCH_ERROR",
                        series_id="CURVE_COMPARISON"
                    )
                    return JSONResponse(content=error_response, status_code=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                error_response = StandardResponseBuilder.create_macro_error_response(
                    provider=MacroProvider.UST,
                    message=f"Failed to fetch {curve1} yield curve data: {str(e)}",
                    error_code="CURVE_FETCH_ERROR",
                    series_id="CURVE_COMPARISON"
                )
                return JSONResponse(content=error_response, status_code=status.HTTP_400_BAD_REQUEST)

        # Fetch curve2 data
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            days = (end_dt - start_dt).days
        else:
            days = 30
        try:
            curve2_data = await CurveService.get_curve_data(curve2, days, "free", macro_service)
            logger.debug(f"{curve2} yield curve data fetched successfully")
            if curve2_data.get("status") != "success":
                error_message = curve2_data.get("message", f"Failed to fetch {curve2} yield curve data")
                error_provider = MacroProvider.ECB if curve2 == "ecb" else MacroProvider.UST
                error_response = StandardResponseBuilder.create_macro_error_response(
                    provider=error_provider,
                    message=error_message,
                    error_code="CURVE_FETCH_ERROR",
                    series_id="CURVE_COMPARISON"
                )
                return JSONResponse(content=error_response, status_code=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_provider = MacroProvider.ECB if curve2 == "ecb" else MacroProvider.UST
            error_message = f"Failed to fetch {curve2.upper()} yield curve data: {str(e)}"
            error_response = StandardResponseBuilder.create_macro_error_response(
                provider=error_provider,
                message=error_message,
                error_code="CURVE_FETCH_ERROR",
                series_id="CURVE_COMPARISON"
            )
            return JSONResponse(content=error_response, status_code=status.HTTP_400_BAD_REQUEST)

        # Extract curve data from MCP-ready format for curve2
        if curve2_data.get("status") == "success" and "data" in curve2_data:
            curve2_extracted = {
                "status": "success",
                "source": "curve_service",
                "curve": curve2_data.get("data", {}).get("curve", {}),
                "date": curve2_data.get("data", {}).get("metadata", {}).get("last_updated", "unknown"),
                "cached": curve2_data.get("meta", {}).get("cache_status") == "cached"
            }
        else:
            curve2_extracted = curve2_data

        # Both curves must have valid data
        if not (curve1_data.get("status") == "success" and curve2_extracted.get("status") == "success" and curve1_data.get("curve") and curve2_extracted.get("curve")):
            error_response = StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.ECB if curve1 == "ecb" else MacroProvider.UST,
                message="One or both yield curves are missing or invalid for comparison.",
                error_code="CURVE_DATA_MISSING",
                series_id="CURVE_COMPARISON"
            )
            return JSONResponse(content=error_response, status_code=status.HTTP_400_BAD_REQUEST)

        # Perform mathematical analysis
        analysis = _calculate_yield_curve_analysis(
            curve1_data["curve"],
            curve2_extracted["curve"],
            curve1_data.get("date", "unknown"),
            curve2_extracted.get("date", "unknown")
        )

        # Determine primary provider based on curve types
        primary_provider = MacroProvider.ECB if curve1 == "ecb" else MacroProvider.UST

        # Determine cache status based on data sources
        curve1_cached = curve1_data.get("cached", False) if curve1_data.get("status") == "success" else False
        curve2_cached = curve2_extracted.get("cached", False) if curve2_extracted.get("status") == "success" else False
        comparison_cache_status = CacheStatus.CACHED if (curve1_cached and curve2_cached) else CacheStatus.FRESH

        result = StandardResponseBuilder.create_macro_success_response(
            provider=primary_provider,
            data={
                "data_sources": {
                    "curve1": {
                        "provider": "ECB_OFFICIAL_WEBSITE" if curve1 == "ecb" else "FRED_API",
                        "series_id": "ECB_YIELD_CURVE" if curve1 == "ecb" else "UST_YIELD_CURVE",
                        "frequency": "daily",
                        "units": "percent",
                        "cache_status": CacheStatus.CACHED.value if curve1_cached else CacheStatus.FRESH.value
                    },
                    "curve2": {
                        "provider": "FRED_API" if curve2 == "ust" else "API_DATA",
                        "series_id": "UST_YIELD_CURVE" if curve2 == "ust" else f"{curve2.upper()}_YIELD_CURVE",
                        "frequency": "daily",
                        "units": "percent",
                        "cache_status": CacheStatus.CACHED.value if curve2_cached else CacheStatus.FRESH.value
                    }
                },
                "curve1": curve1_data,
                "curve2": curve2_data,
                "analysis": analysis,
                "comparison_date": datetime.now().isoformat(),
                "disclaimer": "ECB data sourced from official ECB website" if curve1 == "ecb" else None
            },
            series_id="CURVE_COMPARISON",
            frequency="comparison",
            units="percent",
            cache_status=comparison_cache_status
        )

        return JSONResponse(content=result, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error comparing yield curves: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=f"Failed to compare yield curves: {str(e)}",
            error_code="CURVE_COMPARISON_ERROR",
            series_id="CURVE_COMPARISON"
        )
        return JSONResponse(content=error_response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/spot", summary="Calculate Spot Rates from Yield Curve Data")
async def calculate_spot_rates(
    curve_data: dict
) -> dict:
    """
    Calculate spot rates from yield curve data.
    Expects: curve_data = {'maturities': [...], 'yields': [...]}
    """
    logger.info(f"Calculating spot rates for curve data: {list(curve_data.keys())}")
    
    try:
        cache = await CacheService.create()
        service = CurveService(cache=cache)
        result = await service.calculate_spot_rates(curve_data)
        
        if result.get("status") == "success":
            # Calculation results are always fresh (not cached)
            mcp_response = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.UST,
                data=result.get("data", result),
                series_id="SPOT_RATES_CALCULATION",
                frequency="derived",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
            return JSONResponse(content=mcp_response, status_code=status.HTTP_200_OK)
        else:
            error_message = result.get("message", "Failed to calculate spot rates from yield curve data")
            if curve_data and "maturities" in curve_data:
                error_message += f" for {len(curve_data['maturities'])} maturities"
            mcp_error = StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.UST,
                message=error_message,
                error_code="SPOT_RATES_ERROR",
                series_id="SPOT_RATES_CALCULATION"
            )
            return JSONResponse(content=mcp_error, status_code=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error calculating spot rates: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.UST,
            message=f"Failed to calculate spot rates: {str(e)}",
            error_code="SPOT_RATES_CALCULATION_ERROR",
            series_id="SPOT_RATES_CALCULATION"
        )
        return JSONResponse(content=error_response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/forward", summary="Calculate Forward Rates from Yield Curve Data")
async def calculate_forward_rates(
    curve_data: dict
) -> dict:
    """
    Calculate forward rates from yield curve data.
    Expects: curve_data = {'maturities': [...], 'yields': [...]}
    """
    logger.info(f"Calculating forward rates for curve data: {list(curve_data.keys())}")
    
    try:
        cache = await CacheService.create()
        service = CurveService(cache=cache)
        result = await service.calculate_forward_rates(curve_data)
        
        if result.get("status") == "success":
            mcp_response = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.UST,
                data=result.get("data", result),
                series_id="FORWARD_RATES_CALCULATION",
                frequency="derived",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
            return JSONResponse(content=mcp_response, status_code=status.HTTP_200_OK)
        else:
            error_message = result.get("message", "Failed to calculate forward rates from yield curve data")
            if curve_data and "maturities" in curve_data:
                error_message += f" for {len(curve_data['maturities'])} maturities"
            mcp_error = StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.UST,
                message=error_message,
                error_code="FORWARD_RATES_ERROR",
                series_id="FORWARD_RATES_CALCULATION"
            )
            return JSONResponse(content=mcp_error, status_code=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error calculating forward rates: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.UST,
            message=f"Failed to calculate forward rates: {str(e)}",
            error_code="FORWARD_RATES_CALCULATION_ERROR",
            series_id="FORWARD_RATES_CALCULATION"
        )
        return JSONResponse(content=error_response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post("/analytics", summary="Calculate Yield Curve Analytics")
async def calculate_curve_analytics(
    curve_data: dict
) -> dict:
    """
    Calculate yield curve analytics (slope, curvature, etc.).
    Expects: curve_data = {'maturities': [...], 'yields': [...]}
    """
    logger.info(f"Calculating curve analytics for curve data: {list(curve_data.keys())}")
    
    try:
        cache = await CacheService.create()
        service = CurveService(cache=cache)
        result = await service.get_curve_analytics(curve_data)
        
        if result.get("status") == "success":
            mcp_response = StandardResponseBuilder.create_macro_success_response(
                provider=MacroProvider.UST,
                data=result.get("data", result),
                series_id="CURVE_ANALYTICS_CALCULATION",
                frequency="analytics",
                units="percent",
                cache_status=CacheStatus.FRESH
            )
            return JSONResponse(content=mcp_response, status_code=status.HTTP_200_OK)
        else:
            error_message = result.get("message", "Failed to calculate yield curve analytics")
            if curve_data and "maturities" in curve_data:
                error_message += f" for {len(curve_data['maturities'])} maturities"
            mcp_error = StandardResponseBuilder.create_macro_error_response(
                provider=MacroProvider.UST,
                message=error_message,
                error_code="CURVE_ANALYTICS_ERROR",
                series_id="CURVE_ANALYTICS_CALCULATION"
            )
            return JSONResponse(content=mcp_error, status_code=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        logger.error(f"Error calculating curve analytics: {e}", exc_info=True)
        error_response = StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.UST,
            message=f"Failed to calculate curve analytics: {str(e)}",
            error_code="CURVE_ANALYTICS_CALCULATION_ERROR",
            series_id="CURVE_ANALYTICS_CALCULATION"
        )
        return JSONResponse(content=error_response, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _calculate_yield_curve_analysis(curve1: dict, curve2: dict, date1: str, date2: str) -> dict:
    """
    Calculate mathematical analysis between two yield curves.
    """
    import statistics
    import math
    
    # Common maturities for comparison
    common_maturities = ["1Y", "2Y", "5Y", "10Y", "30Y"]
    
    # Calculate spreads
    spreads = {}
    for maturity in common_maturities:
        if maturity in curve1 and maturity in curve2:
            spreads[maturity] = round(curve2[maturity] - curve1[maturity], 4)
    
    # Calculate curve steepness (10Y - 2Y)
    steepness = {}
    for curve_name, curve_data in [("curve1", curve1), ("curve2", curve2)]:
        if "2Y" in curve_data and "10Y" in curve_data:
            steepness[curve_name] = round(curve_data["10Y"] - curve_data["2Y"], 4)
    
    # Calculate average yields
    avg_yields = {}
    for curve_name, curve_data in [("curve1", curve1), ("curve2", curve2)]:
        values = [v for v in curve_data.values() if isinstance(v, (int, float))]
        if values:
            avg_yields[curve_name] = round(statistics.mean(values), 4)
    
    # Calculate yield volatility (standard deviation)
    volatility = {}
    for curve_name, curve_data in [("curve1", curve1), ("curve2", curve2)]:
        values = [v for v in curve_data.values() if isinstance(v, (int, float))]
        if len(values) > 1:
            volatility[curve_name] = round(statistics.stdev(values), 4)
    
    # Calculate correlation coefficient
    correlation = 0.0
    if len(spreads) > 1:
        curve1_values = [curve1.get(m, 0) for m in common_maturities if m in curve1]
        curve2_values = [curve2.get(m, 0) for m in common_maturities if m in curve2]
        if len(curve1_values) == len(curve2_values) and len(curve1_values) > 1:
            try:
                correlation = round(statistics.correlation(curve1_values, curve2_values), 4)
            except:
                correlation = 0.0
    
    # Market interpretation
    interpretation = _interpret_yield_analysis(spreads, steepness, avg_yields)
    
    return {
        "spreads": spreads,
        "steepness": steepness,
        "average_yields": avg_yields,
        "volatility": volatility,
        "correlation": correlation,
        "interpretation": interpretation,
        "data_dates": {
            "curve1": date1,
            "curve2": date2
        }
    }


def _interpret_yield_analysis(spreads: dict, steepness: dict, avg_yields: dict) -> dict:
    """
    Provide market interpretation of yield curve analysis.
    Analyzes ECB vs US Treasury yield curve differences with specific market insights.
    """
    interpretation = {
        "market_sentiment": "neutral",
        "key_insights": [],
        "risk_assessment": "moderate",
        "currency_implications": [],
        "monetary_policy_signals": []
    }
    
    # Analyze spreads (UST - ECB)
    if spreads:
        avg_spread = sum(spreads.values()) / len(spreads)
        if avg_spread > 0.5:
            interpretation["key_insights"].append(f"US Treasury yields {avg_spread:.2f}% higher than ECB yields on average")
            interpretation["currency_implications"].append("USD strength expected due to higher US yields")
            interpretation["monetary_policy_signals"].append("Fed policy more restrictive than ECB")
        elif avg_spread < -0.5:
            interpretation["key_insights"].append(f"ECB yields {abs(avg_spread):.2f}% higher than US Treasury yields on average")
            interpretation["currency_implications"].append("EUR strength expected due to higher ECB yields")
            interpretation["monetary_policy_signals"].append("ECB policy more restrictive than Fed")
        else:
            interpretation["key_insights"].append("Yield spreads within normal range - balanced monetary policies")
    
    # Analyze steepness differences
    if "curve1" in steepness and "curve2" in steepness:
        steep_diff = steepness["curve2"] - steepness["curve1"]
        if steep_diff > 0.5:
            interpretation["key_insights"].append("US yield curve significantly steeper than ECB curve")
            interpretation["market_sentiment"] = "bullish_steepening"
            interpretation["monetary_policy_signals"].append("US market expects stronger economic growth than Eurozone")
        elif steep_diff < -0.5:
            interpretation["key_insights"].append("ECB yield curve significantly steeper than US curve")
            interpretation["market_sentiment"] = "bearish_flattening"
            interpretation["monetary_policy_signals"].append("Eurozone market expects stronger economic growth than US")
        else:
            interpretation["key_insights"].append("Similar curve steepness - comparable growth expectations")
    
    # Analyze average yield levels
    if "curve1" in avg_yields and "curve2" in avg_yields:
        yield_diff = avg_yields["curve2"] - avg_yields["curve1"]
        if yield_diff > 1.0:
            interpretation["risk_assessment"] = "high"
            interpretation["key_insights"].append(f"Significant {yield_diff:.2f}% yield differential indicates high risk premium for US assets")
            interpretation["currency_implications"].append("Strong USD carry trade opportunity")
        elif yield_diff < -1.0:
            interpretation["risk_assessment"] = "low"
            interpretation["key_insights"].append(f"Negative {abs(yield_diff):.2f}% yield differential suggests flight to quality in US assets")
            interpretation["currency_implications"].append("EUR carry trade opportunity")
        else:
            interpretation["key_insights"].append("Moderate yield differential - balanced risk assessment")
    
    return interpretation






__all__ = ["router"]

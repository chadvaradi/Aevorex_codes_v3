"""
Yield Curve Handler

Provides yield curve data endpoints for US Treasury curves and curve comparison.
ECB yield curve endpoints are available under /ecb/yield-curve/*.

Available endpoints:
- /curve/ust - US Treasury yield curve data
- /curve/compare - Compare ECB vs UST yield curves with mathematical analysis
"""

from fastapi import APIRouter, Depends, Query
from backend.core.services.macro.macro_service import MacroDataService, get_macro_service
from backend.core.services.macro.curve_service import CurveService
from .ecb_handler import get_ecb_yield_curve

router = APIRouter(
    tags=["Macro"]
)



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
    # Calculate days from start_date to end_date, default to 30 days
    from datetime import datetime, timedelta
    if start_date and end_date:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        days = (end_dt - start_dt).days
    else:
        days = 30  # Default to 30 days
    
    return await CurveService.get_curve_data("ust", days, "free", macro_service)


@router.get("/compare", summary="Compare ECB and UST Yield Curves with Mathematical Analysis")
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
    from datetime import datetime, timedelta
    
    # Use real ECB data from ECB handler
    if curve1 == "ecb":
        try:
            ecb_response = await get_ecb_yield_curve()
            # Extract the curve data from the ECB handler response
            if hasattr(ecb_response, 'body'):
                import json
                ecb_data = json.loads(ecb_response.body.decode())
            else:
                ecb_data = ecb_response
            
            # Transform to the expected format
            curve1_data = {
                "status": "success",
                "source": "ecb_official_website",
                "curve": ecb_data.get("curve", {}),
                "date": ecb_data.get("date", "unknown")
            }
        except Exception as e:
            curve1_data = {"status": "error", "message": f"Failed to fetch ECB data: {str(e)}"}
    else:
        # For non-ECB curves, use the original logic
        if start_date and end_date:
            start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            days = (end_dt - start_dt).days
        else:
            days = 30
        
        try:
            curve1_data = await CurveService.get_curve_data(curve1, days, "free", macro_service)
        except Exception as e:
            curve1_data = {"status": "error", "message": str(e)}
    
    # Get UST data (or other curve2)
    if start_date and end_date:
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        days = (end_dt - start_dt).days
    else:
        days = 30
    
    try:
        curve2_data = await CurveService.get_curve_data(curve2, days, "free", macro_service)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to fetch {curve2} data: {str(e)}",
            "curve1": curve1_data,
            "analysis": {}
        }
    
    # Perform mathematical analysis if both curves have data
    analysis = {}
    if (curve1_data.get("status") == "success" and 
        curve2_data.get("status") == "success" and 
        curve1_data.get("curve") and curve2_data.get("curve")):
        
        analysis = _calculate_yield_curve_analysis(
            curve1_data["curve"], 
            curve2_data["curve"],
            curve1_data.get("date", "unknown"),
            curve2_data.get("date", "unknown")
        )
    
    return {
        "status": "success",
        "data_sources": {
            "curve1": "real_data_from_official_website" if curve1 == "ecb" else "api_data",
            "curve2": "real_data_from_fred_api" if curve2 == "ust" else "api_data"
        },
        "curve1": curve1_data,
        "curve2": curve2_data,
        "analysis": analysis,
        "comparison_date": datetime.now().isoformat(),
        "disclaimer": "ECB data sourced from official ECB website" if curve1 == "ecb" else None
    }


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

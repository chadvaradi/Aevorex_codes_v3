"""
ECB Handler

Provides European Central Bank data endpoints.
Handles ECB yield curve data from official ECB sources.

Available endpoints:
- /ecb/yield-curve - Complete ECB yield curve data
- /ecb/yield-curve/latest - Latest ECB yield curve data
- /ecb/yield-curve/{maturity} - Specific maturity yield

Source: Official ECB website with real-time data.
"""

from fastapi import APIRouter, Query, Path
from datetime import date, datetime
from typing import Optional
import httpx
import logging
import asyncio
import xml.etree.ElementTree as ET
import csv
import io
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus

router = APIRouter()

# In-memory cache for ECB yield curve data
_ecb_cache = {
    "curve": {},
    "metadata": {
        "url": "https://sdw-wsrest.ecb.europa.eu/service/data/YC/YC.B.U2.EUR.4F.G_N_A.SV_C_YM.*",
        "description": "Euro area yield curves - zero coupon yield curves for the euro area",
        "currency": "EUR",
        "data_type": "government_bond_yields",
        "source": "ECB SDMX API",
        "last_updated": None
    },
    "last_success": None
}
logger = logging.getLogger(__name__)

SERIES_KEYS = ["SR_3M", "SR_4M", "SR_5M", "SR_6M", "SR_7M", "SR_8M", "SR_9M", "SR_10M", "SR_11M", "SR_1Y", "SR_2Y", "SR_3Y", "SR_4Y", "SR_5Y", "SR_6Y", "SR_7Y", "SR_8Y", "SR_9Y", "SR_10Y", "SR_15Y", "SR_20Y", "SR_25Y", "SR_30Y"]
SERIES_PREFIX = "YC.B.U2.EUR.4F.G_N_A.SV_C_YM."

# CSV fallback endpoint
ECB_CSV_URL = "https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A+G_N_C.SV_C_YM.?lastNObservations=1&format=csvdata"


async def _fetch_ecb_yield_curve_csv():
    """
    Fetch ECB yield curve data from CSV endpoint as fallback.
    Parses CSV data and extracts spot rates for different maturities.
    """
    logger.info("Fetching ECB yield curve data from CSV endpoint (fallback)")
    
    # Map CSV maturity keys to simplified labels
    maturity_map = {
        "SR_3M": "3M", "SR_4M": "4M", "SR_5M": "5M", "SR_6M": "6M", "SR_7M": "7M", "SR_8M": "8M", "SR_9M": "9M", "SR_10M": "10M", "SR_11M": "11M",
        "SR_1Y": "1Y", "SR_2Y": "2Y", "SR_3Y": "3Y", "SR_4Y": "4Y", "SR_5Y": "5Y", "SR_6Y": "6Y", "SR_7Y": "7Y", "SR_8Y": "8Y", "SR_9Y": "9Y", 
        "SR_10Y": "10Y", "SR_15Y": "15Y", "SR_20Y": "20Y", "SR_25Y": "25Y", "SR_30Y": "30Y"
    }
    
    curve = {}
    last_updated = None
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(ECB_CSV_URL)
            
            if response.status_code == 200:
                csv_content = response.text
                
                # Parse CSV data
                csv_reader = csv.DictReader(io.StringIO(csv_content))
                
                for row in csv_reader:
                    key = row.get('KEY', '')
                    obs_value = row.get('OBS_VALUE', '')
                    time_period = row.get('TIME_PERIOD', '')
                    
                    # Look for spot rate (SR_) entries in the key
                    if '.SV_C_YM.SR_' in key and obs_value and time_period:
                        # Extract maturity from key (e.g., YC.B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y -> SR_10Y)
                        maturity_key = key.split('.SV_C_YM.')[-1]
                        
                        if maturity_key in maturity_map:
                            label = maturity_map[maturity_key]
                            
                            try:
                                value = float(obs_value)
                                curve[label] = value
                                
                                # Parse date
                                obs_date = datetime.fromisoformat(time_period).date()
                                last_updated = max(last_updated, obs_date) if last_updated else obs_date
                                
                                logger.debug(f"CSV: Successfully parsed {label}: {value}% (from {maturity_key})")
                                
                            except (ValueError, TypeError) as e:
                                logger.warning(f"CSV: Failed to parse {label} from {maturity_key}: {e}")
                                continue
                
                metadata = {
                    "url": ECB_CSV_URL,
                    "description": "Euro area yield curves - zero coupon yield curves for the euro area (CSV fallback)",
                    "currency": "EUR",
                    "data_type": "government_bond_yields",
                    "source": "ECB CSV API",
                    "last_updated": last_updated.isoformat() if last_updated else datetime.now().isoformat()
                }
                
                if curve:
                    logger.info(f"CSV: Successfully fetched ECB yield curve data with {len(curve)} maturities: {list(curve.keys())}")
                    return {"curve": curve, "metadata": metadata}
                else:
                    raise RuntimeError("CSV endpoint did not return any yield curve data")
                    
            else:
                logger.error(f"CSV: Failed to fetch data: Status={response.status_code}, Body={response.text[:200]}")
                raise RuntimeError(f"CSV endpoint returned status {response.status_code}")
                
    except Exception as e:
        logger.error(f"CSV: Error fetching yield curve data: {e}")
        raise RuntimeError(f"CSV fallback failed: {e}")


async def _fetch_ecb_yield_curve():
    """
    Fetch ECB yield curve data from the official SDMX API.
    Fetches each maturity individually to avoid 400 Bad Request errors.
    Returns the latest yield curve data from ECB.
    """
    logger.info("Fetching ECB yield curve data from SDMX API (individual maturity requests)")
    
    # Map full maturity keys to simplified labels
    maturity_map = {
        "SR_3M": "3M", "SR_4M": "4M", "SR_5M": "5M", "SR_6M": "6M", "SR_7M": "7M", "SR_8M": "8M", "SR_9M": "9M", "SR_10M": "10M", "SR_11M": "11M",
        "SR_1Y": "1Y", "SR_2Y": "2Y", "SR_3Y": "3Y", "SR_4Y": "4Y", "SR_5Y": "5Y", "SR_6Y": "6Y", "SR_7Y": "7Y", "SR_8Y": "8Y", "SR_9Y": "9Y", 
        "SR_10Y": "10Y", "SR_15Y": "15Y", "SR_20Y": "20Y", "SR_25Y": "25Y", "SR_30Y": "30Y"
    }
    
    curve = {}
    last_updated = None
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            headers = {"Accept": "application/vnd.sdmx.data+json;version=1.0.0-wd"}
            
            # Fetch each maturity individually with lastNObservations=1
            for key, label in maturity_map.items():
                url = f"https://sdw-wsrest.ecb.europa.eu/service/data/YC/{SERIES_PREFIX}{key}?lastNObservations=1"
                
                # Rate limiting protection for ECB API
                await asyncio.sleep(1)
                
                try:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Extract the latest value from this single series
                        if "data" in data and "dataSets" in data["data"]:
                            datasets = data["data"]["dataSets"]
                            if datasets and len(datasets) > 0:
                                dataset = datasets[0]
                                
                                if "series" in dataset:
                                    series_data = dataset["series"]
                                    for series_key, series_info in series_data.items():
                                        if "observations" in series_info:
                                            observations = series_info["observations"]
                                            
                                            if observations:
                                                # Get the most recent observation (should be only one with lastNObservations=1)
                                                latest_obs_key = max(observations.keys(), key=lambda x: int(x) if x.isdigit() else 0)
                                                obs_data = observations[latest_obs_key]
                                                
                                                if obs_data and len(obs_data) > 0:
                                                    value = float(obs_data[0])
                                                    curve[label] = value
                                                    
                                                    # Extract observation date
                                                    time_dim = data["data"]["structure"]["dimensions"]["observation"]
                                                    if time_dim and len(time_dim) > 0:
                                                        time_values = time_dim[0].get("values", [])
                                                        if time_values and len(time_values) > int(latest_obs_key):
                                                            time_str = time_values[int(latest_obs_key)].get("id")
                                                            try:
                                                                obs_date = datetime.fromisoformat(time_str).date()
                                                                last_updated = max(last_updated, obs_date) if last_updated else obs_date
                                                            except Exception:
                                                                pass
                                                
                                                break  # Found the data, move to next maturity
                        
                        logger.debug(f"Successfully fetched {label}: {curve.get(label, 'N/A')}")
                        
                    else:
                        logger.error(f"Failed fetching {label}: Status={response.status_code}, Body={response.text[:200]}")
                        
                except Exception as e:
                    logger.error(f"Error fetching {label}: {e}")
                    continue
            
            metadata = {
                "url": "https://sdw-wsrest.ecb.europa.eu/service/data/YC/YC.B.U2.EUR.4F.G_N_A.SV_C_YM.*",
                "description": "Euro area yield curves - zero coupon yield curves for the euro area",
                "currency": "EUR",
                "data_type": "government_bond_yields",
                "source": "ECB SDMX API",
                "last_updated": last_updated.isoformat() if last_updated else datetime.now().isoformat()
            }
    
            # If no curve data was fetched, try CSV fallback
            if not curve:
                logger.warning("SDMX API failed, trying CSV fallback")
                return await _fetch_ecb_yield_curve_csv()
            
            # Update cache with successful data
            _ecb_cache["curve"] = curve
            _ecb_cache["metadata"] = metadata
            _ecb_cache["last_success"] = datetime.utcnow().isoformat()
            
            logger.info(f"Successfully fetched ECB yield curve data with {len(curve)} maturities: {list(curve.keys())}")
            logger.debug(f"ECB curve cache updated at {_ecb_cache['last_success']}")
            return {"curve": curve, "metadata": metadata}
        
    except Exception as e:
        logger.error(f"Failed to fetch ECB yield curve data: {e}")
        logger.warning("SDMX API failed, trying CSV fallback")
        return await _fetch_ecb_yield_curve_csv()


@router.get("/yield-curve", summary="ECB Yield Curve")
async def get_ecb_yield_curve(
    start_date: Optional[date] = Query(None, description="Start date for ECB yield curve (ISO format)"),
    end_date: Optional[date] = Query(None, description="End date for ECB yield curve (ISO format)"),
):
    try:
        data = await _fetch_ecb_yield_curve()
        logger.debug(f"ECB yield curve response built with cache_status={CacheStatus.FRESH}")
        return StandardResponseBuilder.create_macro_success_response(
            provider=MacroProvider.ECB,
            data=data,
            cache_status=CacheStatus.FRESH,
            series_id="ECB_YIELD_CURVE",
            frequency="daily",
            units="percent"
        )
    except Exception as e:
        logger.error(f"Error in get_ecb_yield_curve: {e}")
        return StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=f"Failed to fetch ECB yield curve data: {str(e)}",
            error_code="ECB_API_ERROR",
            series_id="ECB_YIELD_CURVE"
        )


@router.get("/yield-curve/latest", summary="Latest ECB Yield Curve")
async def get_latest_ecb_yield_curve():
    try:
        data = await _fetch_ecb_yield_curve()
        logger.debug(f"ECB yield curve latest response built with cache_status={CacheStatus.FRESH}")
        return StandardResponseBuilder.create_macro_success_response(
            provider=MacroProvider.ECB,
            data=data,
            cache_status=CacheStatus.FRESH,
            series_id="ECB_YIELD_CURVE_LATEST",
            frequency="daily",
            units="percent"
        )
    except Exception as e:
        logger.error(f"Error in get_ecb_yield_curve: {e}")
        return StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=f"Failed to fetch ECB yield curve data: {str(e)}",
            error_code="ECB_API_ERROR",
            series_id="ECB_YIELD_CURVE"
        )


@router.get("/yield-curve/{maturity}", summary="ECB Yield Curve by Maturity")
async def get_ecb_yield_curve_maturity(
    maturity: str = Path(..., description="Maturity period (e.g. 3M, 4M, 5M, 6M, 7M, 8M, 9M, 10M, 11M, 1Y, 2Y, 3Y, 4Y, 5Y, 6Y, 7Y, 8Y, 9Y, 10Y, 15Y, 20Y, 25Y, 30Y)"),
):
    try:
        data = await _fetch_ecb_yield_curve()
        curve = data.get("curve", {})
    except Exception as e:
        logger.error(f"Error in get_ecb_yield_curve_maturity: {e}")
        return StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=f"Failed to fetch ECB yield curve data: {str(e)}",
            error_code="ECB_API_ERROR",
            series_id="ECB_YIELD_CURVE"
        )

    if maturity not in curve:
        return StandardResponseBuilder.create_macro_error_response(
            provider=MacroProvider.ECB,
            message=f"Maturity {maturity} not found. Available maturities: {list(curve.keys())}",
            error_code="MATURITY_NOT_FOUND",
            series_id=f"ECB_YIELD_CURVE_{maturity}"
        )

    result = {
        "yield": curve[maturity],
        "maturity": maturity,
        "metadata": {
            "url": "https://sdw-wsrest.ecb.europa.eu/service/data/YC/YC.B.U2.EUR.4F.G_N_A.SV_C_YM.*",
            "description": f"Euro area government bond yield for {maturity} maturity",
            "currency": "EUR",
            "data_type": "government_bond_yield"
        }
    }

    return StandardResponseBuilder.create_macro_success_response(
        provider=MacroProvider.ECB,
        data=result,
        cache_status=CacheStatus.FRESH,
        series_id=f"ECB_YIELD_CURVE_{maturity}",
        frequency="daily",
        units="percent"
    )


__all__ = ["router"]

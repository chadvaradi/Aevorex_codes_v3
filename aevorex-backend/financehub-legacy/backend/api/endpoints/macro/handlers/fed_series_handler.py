"""
Federal Reserve Series Handler - Complete FRED API Integration

Provides comprehensive FRED (Federal Reserve Economic Data) time series endpoints.
Handles economic indicators, observations, historical data, search, and related series.

**Complete FRED API Coverage:**
- Series Metadata: Get detailed information about any FRED series
- Time Series Data: Retrieve historical observations with date ranges
- Search: Find series by keywords with popularity ranking
- Related Series: Discover connected series using tag-based relationships
- Categories: Browse FRED's hierarchical category structure
- Observations Alias: Alternative nested path for observations

**Key Economic Data Available:**
- Monetary Policy: FEDFUNDS, DFEDTARU, DFEDTARL, IORB, EFFR
- Inflation: CPI, PCE, inflation expectations, TIPS yields
- Employment: Unemployment rates, payroll data, labor force participation
- GDP: Real GDP, GDP deflator, components and contributions
- Financial Markets: Treasury yields, corporate bonds, stock market indices
- International: Exchange rates, trade data, global economic indicators

**Data Source:** Federal Reserve Economic Data (FRED) API
**Update Frequency:** Real-time to monthly depending on series
**Cache:** 1 hour TTL for optimal performance
**Authentication:** Public endpoints (no JWT required)
"""

import logging
from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional

# Assume these exist and are implemented elsewhere
from backend.utils.cache_service import CacheService
from backend.api.endpoints.macro.services.fed_service import FedService

def get_cache_service() -> CacheService:
    """Get a cache service instance."""
    return CacheService()

router = APIRouter()
logger = logging.getLogger("fed_series_handler")

@router.get("/fred/series/{series_id}", summary="FRED Series Metadata - Complete Economic Data Information")
async def get_fred_series(
    series_id: str,
    cache_service=Depends(get_cache_service),
):
    """
    Get comprehensive FRED time series metadata by series ID.
    
    **Returns detailed information including:**
    - Series title, description, and notes
    - Data frequency (Daily, Weekly, Monthly, Quarterly, Annual)
    - Units and seasonal adjustment information
    - Observation start/end dates
    - Popularity ranking and last updated timestamp
    - Source information and methodology notes
    
    **Popular Series Examples:**
    - FEDFUNDS: Federal Funds Effective Rate (primary policy rate)
    - IORB: Interest on Reserve Balances
    - DFEDTARU/DFEDTARL: Fed Target Range Upper/Lower bounds
    - CPI: Consumer Price Index
    - UNRATE: Unemployment Rate
    - GDP: Gross Domestic Product
    
    **Data Source:** Federal Reserve Economic Data (FRED) API
    **Cache:** 1 hour TTL
    """
    try:
        fed_service = FedService(cache_service)
        metadata = await fed_service.get_series_metadata(series_id)
        if not metadata:
            logger.warning(f"Series {series_id} not found in FRED.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FRED series '{series_id}' not found.",
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "meta": {
                    "series_id": series_id,
                    "cached": True,  # Metadata is always cached
                },
                "data": metadata,
            },
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Handle series not found errors
        logger.warning(f"FRED series not found: {series_id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error fetching FRED series {series_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching FRED series.",
        )


@router.get("/fred/observations/{series_id}", summary="FRED Time Series Data - Complete Historical Economic Observations with Advanced Features")
async def get_fred_observations(
    series_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD format)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD format)"),
    frequency: Optional[str] = Query(None, description="Data frequency transformation: 'd'=daily, 'w'=weekly, 'bw'=biweekly, 'm'=monthly, 'q'=quarterly, 'sa'=semiannual, 'a'=annual"),
    units: Optional[str] = Query(None, description="Units transformation: 'lin'=levels, 'chg'=change, 'ch1'=change from year ago, 'pch'=percent change, 'pc1'=percent change from year ago, 'pca'=compounded annual rate of change, 'cch'=continuously compounded rate of change, 'cca'=continuously compounded annual rate of change, 'log'=natural log"),
    force_refresh: Optional[bool] = Query(False, description="Force cache refresh (bypass 1-hour TTL)"),
    cache_service=Depends(get_cache_service),
):
    """
    Get comprehensive FRED time series observations with advanced data processing capabilities.
    
    **🔍 COMPLETE DATA FEATURES:**
    
    **📊 Core Time Series Data:**
    - Historical observations with precise dates and values
    - Real-time and vintage data support (realtime_start, realtime_end)
    - Configurable date ranges with automatic boundary handling
    - High-frequency data support (daily, weekly, monthly, quarterly, annual)
    
    **⚙️ Advanced Data Processing:**
    - **Frequency Transformation**: Automatic frequency conversion (e.g., daily→monthly, quarterly→annual)
    - **Unit Transformations**: 8+ transformation types (levels, changes, percent changes, log, compounded rates)
    - **Missing Value Handling**: Intelligent "." to null conversion with statistics
    - **Data Quality Indicators**: Missing value counts, percentages, and quality metrics
    - **Automatic Fallback**: Graceful frequency fallback (e.g., Q→M if quarterly not supported)
    
    **📈 Data Normalization & Statistics:**
    - Value normalization (converts FRED "." to null for missing data)
    - Normalization statistics in first observation: total_observations, valid_values, missing_values, missing_percentage
    - Data quality assessment and completeness indicators
    - Frequency fallback information (requested vs actual frequency)
    
    **🎯 USAGE EXAMPLES:**
    
    **Monetary Policy Analysis:**
    - Fed Funds Rate: `/fred/observations/FEDFUNDS?start_date=2025-08-01&end_date=2025-09-01`
    - Interest on Reserves: `/fred/observations/IORB?frequency=d&units=lin`
    - Target Range: `/fred/observations/DFEDTARU?start_date=2024-01-01`
    
    **Inflation & Price Data:**
    - Monthly CPI: `/fred/observations/CPIAUCSL?frequency=m&units=pch` (percent change)
    - Core PCE: `/fred/observations/PCEPILFE?frequency=m&units=pc1` (percent change from year ago)
    - Inflation Expectations: `/fred/observations/T10YIE?frequency=m`
    
    **Economic Growth:**
    - GDP Quarterly: `/fred/observations/GDP?frequency=q&units=chg` (quarterly change)
    - GDP Annual: `/fred/observations/GDP?frequency=a&units=pch` (annual percent change)
    - Real GDP: `/fred/observations/GDPC1?frequency=q`
    
    **Labor Market:**
    - Unemployment Rate: `/fred/observations/UNRATE?frequency=m&units=lin`
    - Nonfarm Payrolls: `/fred/observations/PAYEMS?frequency=m&units=chg`
    - Labor Force Participation: `/fred/observations/CIVPART?frequency=m`
    
    **Financial Markets:**
    - 10-Year Treasury: `/fred/observations/DGS10?frequency=d&units=lin`
    - 2-Year Treasury: `/fred/observations/DGS2?frequency=d&units=lin`
    - Yield Curve Spread: `/fred/observations/T10Y2Y?frequency=d`
    - VIX Volatility: `/fred/observations/VIXCLS?frequency=d&units=lin`
    
    **🏦 FREQUENCY PARAMETERS:**
    - `d` = Daily (business days for most series)
    - `w` = Weekly (ending Friday)
    - `bw` = Biweekly (every other week)
    - `m` = Monthly (end of month)
    - `q` = Quarterly (end of quarter)
    - `sa` = Semiannual (twice per year)
    - `a` = Annual (end of year)
    
    **📊 UNITS TRANSFORMATIONS:**
    - `lin` = Levels (original units)
    - `chg` = Change (period-over-period change)
    - `ch1` = Change from Year Ago (year-over-year change)
    - `pch` = Percent Change (period-over-period percent change)
    - `pc1` = Percent Change from Year Ago (year-over-year percent change)
    - `pca` = Compounded Annual Rate of Change
    - `cch` = Continuously Compounded Rate of Change
    - `cca` = Continuously Compounded Annual Rate of Change
    - `log` = Natural Log (logarithmic transformation)
    
    **📋 RESPONSE STRUCTURE:**
    ```json
    {
      "status": "success",
      "meta": {
        "series_id": "FEDFUNDS",
        "start_date": "2025-08-01",
        "end_date": "2025-09-01",
        "frequency": "m",
        "units": "lin"
      },
      "data": {
        "realtime_start": "2025-09-15",
        "realtime_end": "2025-09-15",
        "observation_start": "1954-07-01",
        "observation_end": "2025-08-01",
        "units": "Percent",
        "output_type": 1,
        "file_type": "json",
        "order_by": "observation_date",
        "sort_order": "asc",
        "count": 1,
        "offset": 0,
        "limit": 100000,
        "observations": [
          {
            "realtime_start": "2025-09-15",
            "realtime_end": "2025-09-15",
            "date": "2025-08-01",
            "value": 4.33,
            "_normalization_stats": {
              "total_observations": 1,
              "valid_values": 1,
              "missing_values": 0,
              "missing_percentage": 0.0
            }
          }
        ],
        "frequency_fallback": {
          "requested": "q",
          "actual": "series_default",
          "message": "Series FEDFUNDS does not support frequency 'q', using default frequency"
        }
      }
    }
    ```
    
    **🔧 TECHNICAL SPECIFICATIONS:**
    - **Data Source**: Federal Reserve Economic Data (FRED) API
    - **Update Frequency**: Real-time to monthly depending on series
    - **Cache**: 1 hour TTL with intelligent cache key generation
    - **Rate Limiting**: FRED API limits (120 requests/minute)
    - **Error Handling**: Graceful fallbacks for unsupported parameters
    - **Data Quality**: Automatic missing value detection and statistics
    
    **🎯 MCP AGENT INTEGRATION:**
    This endpoint provides comprehensive economic time series data with advanced processing capabilities,
    making it ideal for financial analysis, research, and decision support systems.
    """
    try:
        fed_service = FedService(cache_service)
        observations = await fed_service.get_series_observations(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            units=units,
            force_refresh=force_refresh,
        )
        
        # Check if the response indicates an error
        if observations and observations.get("status") == "error":
            logger.warning(f"FRED API error for series {series_id}: {observations.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FRED series '{series_id}' not found or invalid: {observations.get('message')}",
            )
        
        if not observations:
            logger.warning(f"No observations found for series {series_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No observations found for FRED series '{series_id}'.",
            )
        
        # Extract frequency fallback information if present
        frequency_fallback = None
        if "frequency_fallback" in observations:
            frequency_fallback = observations["frequency_fallback"]
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "meta": {
                    "series_id": series_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "frequency": frequency,
                    "units": units,
                    "cached": bool(not force_refresh),
                    "frequency_fallback": frequency_fallback,
                },
                "data": observations,
            },
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Handle series not found errors
        logger.warning(f"FRED series not found: {series_id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error fetching observations for {series_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching FRED observations.",
        )


@router.get("/fred/series/{series_id}/observations")
async def get_series_observations_alias(
    series_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    frequency: Optional[str] = Query(None, description="Data frequency (e.g., 'm', 'q', 'a')"),
    units: Optional[str] = Query(None, description="Units transformation (e.g., 'lin', 'chg')"),
    force_refresh: Optional[bool] = Query(False, description="Force cache refresh"),
    cache_service=Depends(get_cache_service),
):
    """
    Get FRED observations for a specific series (alias for /fred/observations/{series_id}).
    """
    try:
        fed_service = FedService(cache_service)
        observations = await fed_service.get_series_observations(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            units=units,
            force_refresh=force_refresh,
        )
        
        # Check if the response indicates an error
        if observations and observations.get("status") == "error":
            logger.warning(f"FRED API error for series {series_id}: {observations.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FRED series '{series_id}' not found or invalid: {observations.get('message')}",
            )
        
        if not observations:
            logger.warning(f"No observations found for series {series_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No observations found for FRED series '{series_id}'.",
            )
        
        # Extract frequency fallback information if present
        frequency_fallback = None
        if "frequency_fallback" in observations:
            frequency_fallback = observations["frequency_fallback"]
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "meta": {
                    "series_id": series_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "frequency": frequency,
                    "units": units,
                    "cached": bool(not force_refresh),
                    "frequency_fallback": frequency_fallback,
                },
                "data": observations,
            },
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Handle series not found errors
        logger.warning(f"FRED series not found: {series_id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error fetching observations for {series_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching FRED observations.",
        )


@router.get("/fred/series/{series_id}/related", summary="FRED Related Series - Discover Connected Economic Indicators")
async def get_fred_related_series(
    series_id: str,
    cache_service=Depends(get_cache_service),
):
    """
    Get related FRED time series for a specific series using intelligent tag-based relationships.
    
    **Discovery method:**
    - Analyzes series tags and metadata
    - Finds related tags using FRED's classification system
    - Returns series with similar economic themes and relationships
    - Uses 3-step process: tags → related tags → connected series
    
    **Use cases:**
    - Discover complementary economic indicators
    - Find alternative data sources for similar concepts
    - Explore related monetary policy instruments
    - Identify sector-specific economic data
    
    **Examples:**
    - FEDFUNDS → Federal tax receipts, commercial paper rates, bank reserves
    - CPI → PCE, inflation expectations, wage data, commodity prices
    - GDP → GDP components, productivity, employment, consumption
    
    **Data Source:** Federal Reserve Economic Data (FRED) API
    **Cache:** 1 hour TTL
    **Algorithm:** Tag-based relationship discovery
    """
    try:
        fed_service = FedService(cache_service)
        related = await fed_service.get_related_series(series_id)
        if not related:
            logger.warning(f"No related series found for: {series_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No related series found for FRED series '{series_id}'.",
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "meta": {
                    "series_id": series_id,
                    "cached": True,  # Related series are always cached
                },
                "data": related,
            },
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Handle series not found errors
        logger.warning(f"FRED series not found: {series_id} - {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error fetching related series for {series_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching related FRED series.",
        )


@router.get("/fred/presets", summary="FRED Default Presets - Pre-configured Economic Data Series")
async def get_fred_presets(
    cache_service=Depends(get_cache_service),
):
    """
    Get pre-configured FRED series for common economic indicators.
    
    **Default presets include:**
    - **Monetary Policy**: FEDFUNDS, IORB, DFEDTARU, DFEDTARL
    - **Inflation**: CPIAUCSL, PCEPI, CPILFESL
    - **Employment**: UNRATE, PAYEMS, JOLTS
    - **GDP & National Accounts**: GDP, GDPC1, GPDI
    - **Financial Markets**: DGS10, DGS2, DGS30, DGS3MO
    - **Housing**: CSUSHPINSA, MSPUS, HOUST
    
    **Returns:**
    - Series metadata for each preset
    - Latest observations
    - Ready-to-use for frontend dashboards
    
    **Data Source:** Federal Reserve Economic Data (FRED) API
    **Cache:** 1 hour TTL
    **Use Case:** Quick access to key economic indicators
    """
    try:
        fed_service = FedService(cache_service)
        
        # Define comprehensive preset series for fintech/portfolio management
        preset_series = {
            "monetary_policy": ["FEDFUNDS", "IORB", "DFEDTARU", "DFEDTARL", "DFEDTAR", "EFFR"],
            "inflation": ["CPIAUCSL", "PCEPI", "CPILFESL", "T10YIE", "T5YIE", "T1YIE"],
            "employment": ["UNRATE", "PAYEMS", "JOLTS", "CIVPART", "EMRATIO", "LNS14000006"],
            "gdp": ["GDP", "GDPC1", "GPDI", "GDPPOT", "GDPDEF", "GNP"],
            "financial_markets": ["DGS10", "DGS2", "DGS30", "DGS3MO", "DGS5", "DGS7", "T10Y2Y", "T10Y3M"],
            "housing": ["CSUSHPINSA", "MSPUS", "HOUST", "PERMIT", "HSN1F", "EXHOSLUSM495S"],
            "portfolio_management": ["VIXCLS", "SP500", "DJIA", "NASDAQCOM", "BAMLH0A0HYM2", "BAMLCC0A0CMTRIV"],
            "credit_markets": ["BAMLH0A0HYM2", "BAMLCC0A0CMTRIV", "BAMLHE00EHYIOAS", "BAMLHE00EHYIOAS"],
            "commodities": ["DCOILWTICO", "DCOILBRENTEU", "GOLDAMGBD228NLBM", "SILVER"],
            "international": ["DEXUSEU", "DEXJPUS", "DEXCHUS", "DEXUSUK", "DEXCAUS"],
            "banking": ["TOTRESNS", "TOTBORNS", "TOTCI", "TOTLL", "TOTBKCR"],
            "yield_curve": ["DGS1MO", "DGS3MO", "DGS6MO", "DGS1", "DGS2", "DGS3", "DGS5", "DGS7", "DGS10", "DGS20", "DGS30"]
        }
        
        presets_data = {}
        
        for category, series_list in preset_series.items():
            category_data = []
            for series_id in series_list:
                try:
                    # Get metadata
                    metadata = await fed_service.get_series_metadata(series_id)
                    if metadata and "seriess" in metadata and metadata["seriess"]:
                        series_info = metadata["seriess"][0]
                        
                        # Get latest observation
                        observations = await fed_service.get_series_observations(
                            series_id=series_id,
                            start_date="2024-01-01"  # Get recent data
                        )
                        
                        latest_value = None
                        if observations and "observations" in observations and observations["observations"]:
                            # Get the most recent non-null value
                            for obs in reversed(observations["observations"]):
                                if obs.get("value") is not None:
                                    latest_value = obs["value"]
                                    break
                        
                        category_data.append({
                            "id": series_id,
                            "title": series_info.get("title", series_id),
                            "frequency": series_info.get("frequency", "Unknown"),
                            "units": series_info.get("units", "Unknown"),
                            "popularity": series_info.get("popularity", 0),
                            "latest_value": latest_value,
                            "observation_end": series_info.get("observation_end", "Unknown")
                        })
                except Exception as e:
                    logger.warning(f"Failed to fetch preset series {series_id}: {e}")
                    continue
            
            presets_data[category] = category_data
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "meta": {
                    "description": "Pre-configured FRED series for common economic indicators",
                    "categories": list(preset_series.keys()),
                    "total_series": sum(len(series_list) for series_list in preset_series.values())
                },
                "data": presets_data,
            },
        )
    except Exception as e:
        logger.error(f"Error fetching FRED presets: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching FRED presets.",
        )


@router.get("/fred/search", summary="FRED Series Search - Discover Economic Data by Keywords")
async def get_fred_search(
    query: str = Query(..., description="Search query for FRED series"),
    limit: int = Query(10, description="Maximum number of results"),
    offset: int = Query(0, description="Offset for pagination"),
    cache_service=Depends(get_cache_service),
):
    """
    Search FRED time series by keywords to discover relevant economic data.
    
    **Search capabilities:**
    - Keyword-based discovery of economic indicators
    - Results ranked by popularity and relevance
    - Pagination support for large result sets
    - Cached results for improved performance
    
    **Popular Search Examples:**
    - "inflation" → CPI, PCE, inflation expectations, TIPS yields
    - "unemployment" → Unemployment rates, labor force participation
    - "interest rate" → Fed funds, Treasury yields, mortgage rates
    - "gdp" → GDP, components, contributions, deflators
    - "housing" → Home prices, construction, mortgage data
    - "employment" → Payroll data, job openings, labor statistics
    
    **Data Source:** Federal Reserve Economic Data (FRED) API
    **Cache:** 1 hour TTL
    **Results:** Ranked by popularity and relevance
    """
    try:
        fed_service = FedService(cache_service)
        results = await fed_service.search_series(query=query, limit=limit, offset=offset)
        if not results:
            logger.warning(f"No results found for query: {query}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No FRED series found for query '{query}'.",
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "meta": {
                    "query": query,
                    "limit": limit,
                    "offset": offset,
                    "cached": True,  # Search results are always cached
                },
                "data": results,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching FRED series for query '{query}': {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error searching FRED series.",
        )


@router.get("/fred/categories", summary="FRED Categories - Browse Economic Data Classification System")
async def get_fred_categories(
    category_id: int = Query(0, description="Category ID to browse (0 for root categories)"),
    cache_service=Depends(get_cache_service),
):
    """
    Get FRED data categories for browsing the hierarchical classification system.
    
    **Category system:**
    - Hierarchical organization of economic data
    - Root categories and subcategories for systematic browsing
    - Category-based discovery of related economic indicators
    - Structured navigation through FRED's data universe
    
    **Category types include:**
    - Monetary Policy: Federal Reserve operations, interest rates
    - Prices: Inflation measures, price indices, deflators
    - Employment: Labor market data, unemployment, payrolls
    - National Accounts: GDP, consumption, investment, trade
    - Financial Markets: Treasury yields, corporate bonds, stock indices
    - International: Exchange rates, trade data, global indicators
    
    **Usage:**
    - Start with root categories to explore data themes
    - Use category IDs to find series within specific economic areas
    - Navigate hierarchical structure for comprehensive data discovery
    
    **Data Source:** Federal Reserve Economic Data (FRED) API
    **Cache:** 1 hour TTL
    **Structure:** Hierarchical category tree
    """
    try:
        fed_service = FedService(cache_service)
        categories = await fed_service.get_categories(category_id)
        if not categories:
            logger.warning("No FRED categories found.")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No FRED categories found.",
            )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "success",
                "meta": {
                    "category_id": category_id,
                    "cached": True,  # Categories are always cached
                },
                "data": categories,
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching FRED categories: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error fetching FRED categories.",
        )

__all__ = ["router"]

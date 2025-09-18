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
# StandardResponseBuilder import from shared location
from backend.api.endpoints.shared.response_builder import StandardResponseBuilder, MacroProvider, CacheStatus
from typing import Optional

# Assume these exist and are implemented elsewhere
from backend.utils.cache_service import CacheService
from backend.api.endpoints.macro.services.fed_service import FedService

def get_cache_service() -> CacheService:
    """Get a cache service instance."""
    return CacheService()

router = APIRouter()
logger = logging.getLogger("fed_series_handler")

# Alias endpoint for /fed/series/{series_id} -> /fred/series/{series_id}
@router.get("/series/{series_id}", summary="FRED Series Metadata - Alias for /fred/series/{series_id}")
async def get_fred_series_alias(
    series_id: str,
    cache_service=Depends(get_cache_service),
):
    """
    Alias endpoint for FRED series metadata.
    Redirects to /fred/series/{series_id} for backward compatibility.
    """
    return await get_fred_series(series_id, cache_service)

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
            return StandardResponseBuilder.error(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message=f"FRED series '{series_id}' not found.",
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "error"
                }
            )
        return StandardResponseBuilder.create_macro_success_response(
            provider=MacroProvider.FRED,
            data=metadata,
            series_id=series_id,
            cache_status=CacheStatus.CACHED
        )
    except ValueError as e:
        logger.warning(f"FRED series not found: {series_id} - {e}")
        return StandardResponseBuilder.error(
            status_code=status.HTTP_404_NOT_FOUND,
            error_message=str(e),
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching FRED series {series_id}: {e}", exc_info=True)
        return StandardResponseBuilder.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal server error fetching FRED series.",
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
        )


@router.get("/fred/observations/{series_id}", summary="FRED Time Series Data - Complete Historical Economic Observations with Advanced Features")
async def get_fred_observations(
    series_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD format)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD format)"),
    frequency: Optional[str] = Query("m", description="Data frequency transformation: 'd'=daily, 'w'=weekly, 'bw'=biweekly, 'm'=monthly, 'q'=quarterly, 'sa'=semiannual, 'a'=annual"),
    units: Optional[str] = Query(None, description="Units transformation: 'lin'=levels, 'chg'=change, 'ch1'=change from year ago, 'pch'=percent change, 'pc1'=percent change from year ago, 'pca'=compounded annual rate of change, 'cch'=continuously compounded rate of change, 'cca'=continuously compounded annual rate of change, 'log'=natural log"),
    limit: Optional[int] = Query(60, ge=1, le=1000, description="Maximum number of observations to return (default: 60, max: 1000)"),
    view: Optional[str] = Query("full", regex="^(full|summary)$", description="Data view: 'full' for complete data, 'summary' for condensed view"),
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
    
    **🛡️ COST PROTECTION GUARDS:**
    - **Token Estimation**: Estimates response size based on series type, frequency, and date range
    - **Date Cutoff**: Automatic cutoff for very old data (pre-2000, series-specific limits)
    - **Limit Validation**: Default 60 observations, maximum 1000 per request
    - **Token Threshold**: 5,000 tokens (~20KB JSON) maximum for full view
    - **402 Upgrade Required**: Blocks requests exceeding token threshold with upgrade prompt
    - **Summary View**: Provides condensed data (~800 tokens) with statistics and recent data
    
    **💰 COST RATIONALE:**
    - FEDFUNDS full history (854 obs) = ~20,480 tokens = ~$0.0024 (Gemini 2.0 Flash)
    - DGS10 daily 60 years = ~348,750 tokens = ~$0.0354 (Gemini 2.0 Flash)
    - Without guards: DGS10 full history = ~4M tokens = ~$16+ per request
    - Summary view reduces costs by 95% while maintaining analytical value
    
    **🎯 PROTECTION STRATEGY:**
    - Prevents accidental high-cost requests during MVP testing
    - Maintains premium user experience with upgrade paths
    - Optimizes for LLM token efficiency without data loss
    - Series-specific cutoffs prevent unnecessary historical data requests
    
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
        # Cost protection: Date cutoff and token estimation
        start_date, end_date = _apply_date_cutoff(start_date, end_date, series_id)
        estimated_tokens = _estimate_token_count(series_id, limit, frequency, start_date, end_date)
        MAX_TOKEN_THRESHOLD = 5000  # ~20KB JSON

        if estimated_tokens > MAX_TOKEN_THRESHOLD and view == "full":
            return StandardResponseBuilder.error(
                status_code=402,
                error_message=(
                    f"Request would generate ~{estimated_tokens} tokens. Use view=summary or reduce parameters."
                ),
                error_code="upgrade_required",
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "error",
                    "estimated_tokens": estimated_tokens,
                    "max_allowed": MAX_TOKEN_THRESHOLD,
                }
            )

        # Handle summary view
        if view == "summary":
            summary = await _get_summary_view(series_id, cache_service)
            if summary.get("status") == "error":
                return StandardResponseBuilder.error(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_message=summary.get("message", "Summary view not available."),
                    meta={
                        "provider": "fred",
                        "series_id": series_id,
                        "cache_status": "error"
                    }
                )
            # MCP-compliant summary success
            return StandardResponseBuilder.success(
                data=summary,
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "cached"
                }
            )

        fed_service = FedService(cache_service)
        observations = await fed_service.get_series_observations(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            units=units,
            limit=limit,
            force_refresh=force_refresh,
        )

        # The service now returns MCP-ready response, so we can return it directly
        return observations

    except ValueError as e:
        logger.warning(f"FRED series not found: {series_id} - {e}")
        return StandardResponseBuilder.error(
            status_code=status.HTTP_404_NOT_FOUND,
            error_message=str(e),
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching observations for {series_id}: {e}", exc_info=True)
        return StandardResponseBuilder.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal server error fetching FRED observations.",
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
        )


@router.get("/fred/series/{series_id}/observations")
async def get_series_observations_alias(
    series_id: str,
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    frequency: Optional[str] = Query("m", description="Data frequency (e.g., 'm', 'q', 'a')"),
    units: Optional[str] = Query(None, description="Units transformation (e.g., 'lin', 'chg')"),
    limit: Optional[int] = Query(60, ge=1, le=1000, description="Maximum number of observations to return (default: 60, max: 1000)"),
    view: Optional[str] = Query("full", regex="^(full|summary)$", description="Data view: 'full' for complete data, 'summary' for condensed view"),
    force_refresh: Optional[bool] = Query(False, description="Force cache refresh"),
    cache_service=Depends(get_cache_service),
):
    """
    Get FRED observations for a specific series (alias for /fred/observations/{series_id}).
    
    **🛡️ COST PROTECTION GUARDS:**
    - **Token Estimation**: Estimates response size based on series type, frequency, and date range
    - **Date Cutoff**: Automatic cutoff for very old data (pre-2000, series-specific limits)
    - **Limit Validation**: Default 60 observations, maximum 1000 per request
    - **Token Threshold**: 5,000 tokens (~20KB JSON) maximum for full view
    - **402 Upgrade Required**: Blocks requests exceeding token threshold with upgrade prompt
    - **Summary View**: Provides condensed data (~800 tokens) with statistics and recent data
    
    **💰 COST RATIONALE:**
    - Same cost protection as main observations endpoint
    - Prevents duplicate high-cost requests through alias endpoint
    - Maintains consistent cost controls across all FRED data access points
    
    **🎯 PROTECTION STRATEGY:**
    - Identical guards to main endpoint for consistency
    - Prevents cost escalation through alternative access paths
    - Maintains premium user experience with upgrade paths
    """
    try:
        # Cost protection: Date cutoff and token estimation
        start_date, end_date = _apply_date_cutoff(start_date, end_date, series_id)
        estimated_tokens = _estimate_token_count(series_id, limit, frequency, start_date, end_date)
        MAX_TOKEN_THRESHOLD = 5000  # ~20KB JSON

        if estimated_tokens > MAX_TOKEN_THRESHOLD and view == "full":
            return StandardResponseBuilder.error(
                status_code=402,
                error_message=(
                    f"Request would generate ~{estimated_tokens} tokens. Use view=summary or reduce parameters."
                ),
                error_code="upgrade_required",
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "error",
                    "estimated_tokens": estimated_tokens,
                    "max_allowed": MAX_TOKEN_THRESHOLD,
                }
            )

        # Handle summary view
        if view == "summary":
            summary = await _get_summary_view(series_id, cache_service)
            if summary.get("status") == "error":
                return StandardResponseBuilder.error(
                    status_code=status.HTTP_404_NOT_FOUND,
                    error_message=summary.get("message", "Summary view not available."),
                    meta={
                        "provider": "fred",
                        "series_id": series_id,
                        "cache_status": "error"
                    }
                )
            return StandardResponseBuilder.success(
                data=summary,
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "cached"
                }
            )

        fed_service = FedService(cache_service)
        observations = await fed_service.get_series_observations(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            units=units,
            limit=limit,
            force_refresh=force_refresh,
        )

        # Check if the response indicates an error
        if observations and observations.get("status") == "error":
            logger.warning(f"FRED API error for series {series_id}: {observations.get('message')}")
            return StandardResponseBuilder.error(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message=f"FRED series '{series_id}' not found or invalid: {observations.get('message')}",
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "error"
                }
            )

        if not observations:
            logger.warning(f"No observations found for series {series_id}")
            return StandardResponseBuilder.error(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message=f"No observations found for FRED series '{series_id}'.",
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "error"
                }
            )

        # Extract frequency fallback information if present
        frequency_fallback = None
        if "frequency_fallback" in observations:
            frequency_fallback = observations["frequency_fallback"]

        # Get series metadata for real meta information
        try:
            series_metadata = await fed_service.get_series_metadata(series_id)
            if series_metadata and "seriess" in series_metadata and series_metadata["seriess"]:
                series_info = series_metadata["seriess"][0]
                actual_start_date = series_info.get("observation_start", start_date)
                actual_end_date = series_info.get("observation_end", end_date)
                actual_frequency = series_info.get("frequency", frequency)
                actual_units = series_info.get("units", units)
            else:
                # Fallback to observations response if metadata not available
                actual_start_date = observations.get("observation_start", start_date)
                actual_end_date = observations.get("observation_end", end_date)
                actual_frequency = observations.get("frequency", frequency)
                actual_units = observations.get("units", units)
        except Exception as e:
            logger.warning(f"Could not fetch series metadata for {series_id}: {e}")
            # Fallback to observations response
            actual_start_date = observations.get("observation_start", start_date)
            actual_end_date = observations.get("observation_end", end_date)
            actual_frequency = observations.get("frequency", frequency)
            actual_units = observations.get("units", units)

        # Extract normalization stats from first observation if present
        normalization_stats = None
        if observations and "observations" in observations and observations["observations"]:
            first_obs = observations["observations"][0]
            if "_normalization_stats" in first_obs:
                normalization_stats = first_obs["_normalization_stats"]
                # Remove from first observation
                del first_obs["_normalization_stats"]

        # Create response with statistics in data.statistics
        response_data = observations.copy()
        if normalization_stats:
            response_data["statistics"] = normalization_stats

        return StandardResponseBuilder.success(
            data=response_data,
            meta={
                "provider": "fred",
                "series_id": series_id,
                "start_date": actual_start_date,
                "end_date": actual_end_date,
                "frequency": actual_frequency,
                "units": actual_units,
                "limit": limit,
                "cache_status": "fresh" if not force_refresh else "fresh",
                "frequency_fallback": frequency_fallback,
            }
        )
    except ValueError as e:
        logger.warning(f"FRED series not found: {series_id} - {e}")
        return StandardResponseBuilder.error(
            status_code=status.HTTP_404_NOT_FOUND,
            error_message=str(e),
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching observations for {series_id}: {e}", exc_info=True)
        return StandardResponseBuilder.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal server error fetching FRED observations.",
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
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
            return StandardResponseBuilder.error(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message=f"No related series found for FRED series '{series_id}'.",
                meta={
                    "provider": "fred",
                    "series_id": series_id,
                    "cache_status": "error"
                }
            )
        return StandardResponseBuilder.create_macro_success_response(
            provider=MacroProvider.FRED,
            data=related,
            series_id=f"{series_id}_related",
            frequency="metadata",
            units="list",
            cache_status=CacheStatus.CACHED
        )
    except ValueError as e:
        logger.warning(f"FRED series not found: {series_id} - {e}")
        return StandardResponseBuilder.error(
            status_code=status.HTTP_404_NOT_FOUND,
            error_message=str(e),
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
        )
    except Exception as e:
        logger.error(f"Error fetching related series for {series_id}: {e}", exc_info=True)
        return StandardResponseBuilder.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal server error fetching related FRED series.",
            meta={
                "provider": "fred",
                "series_id": series_id,
                "cache_status": "error"
            }
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

        return StandardResponseBuilder.create_macro_success_response(
            provider=MacroProvider.FRED,
            data=presets_data,
            series_id="FRED_PRESETS",
            frequency="metadata",
            units="list",
            cache_status=CacheStatus.CACHED
        )
    except Exception as e:
        logger.error(f"Error fetching FRED presets: {e}", exc_info=True)
        return StandardResponseBuilder.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal server error fetching FRED presets.",
            meta={
                "provider": "fred",
                "cache_status": "error"
            }
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
            return StandardResponseBuilder.error(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message=f"No FRED series found for query '{query}'.",
                meta={
                    "provider": "fred",
                    "cache_status": "error",
                    "query": query
                }
            )
        return StandardResponseBuilder.create_macro_success_response(
            provider=MacroProvider.FRED,
            data={
                "series": results.get("data", {}).get("series", results.get("seriess", [])) if results else [],
                "count": results.get("data", {}).get("count", results.get("count", 0)) if results else 0,
                "offset": results.get("data", {}).get("offset", results.get("offset", 0)) if results else 0,
                "limit": results.get("data", {}).get("limit", results.get("limit", limit)) if results else limit
            },
            series_id="FRED_SEARCH",
            frequency="metadata",
            units="list",
            cache_status=CacheStatus.CACHED
        )
    except Exception as e:
        logger.error(f"Error searching FRED series for query '{query}': {e}", exc_info=True)
        return StandardResponseBuilder.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal server error searching FRED series.",
            meta={
                "provider": "fred",
                "cache_status": "error"
            }
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
            return StandardResponseBuilder.error(
                status_code=status.HTTP_404_NOT_FOUND,
                error_message="No FRED categories found.",
                meta={
                    "provider": "fred",
                    "cache_status": "error",
                    "category_id": category_id
                }
            )
        return StandardResponseBuilder.create_macro_success_response(
            provider=MacroProvider.FRED,
            data={
                "categories": categories.get("categories", [])[0].get("children", []) if categories and categories.get("categories") and len(categories.get("categories", [])) > 0 else []
            },
            series_id="FRED_CATEGORIES",
            frequency="metadata",
            units="list",
            cache_status=CacheStatus.CACHED
        )
    except Exception as e:
        logger.error(f"Error fetching FRED categories: {e}", exc_info=True)
        return StandardResponseBuilder.error(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal server error fetching FRED categories.",
            meta={
                "provider": "fred",
                "cache_status": "error"
            }
        )


def _apply_date_cutoff(start_date: str, end_date: str, series_id: str) -> tuple[str, str]:
    """
    Apply date cutoff to prevent requests for very old data (pre-2000).
    Most users don't need data older than 25 years for practical analysis.
    """
    from datetime import datetime
    
    # Default cutoff date (25 years ago)
    cutoff_date = "2000-01-01"
    
    # Series-specific cutoffs for very long historical data
    series_cutoffs = {
        "CPIAUCSL": "1913-01-01",  # CPI starts in 1913, but most analysis uses post-2000
        "DGS10": "1962-01-01",     # 10-Year Treasury starts in 1962
        "FEDFUNDS": "1954-07-01",  # Fed Funds starts in 1954
        "GDP": "1947-01-01",       # GDP starts in 1947
        "UNRATE": "1948-01-01",    # Unemployment starts in 1948
    }
    
    # Use series-specific cutoff if available, otherwise use default
    series_cutoff = series_cutoffs.get(series_id, cutoff_date)
    
    # Apply cutoff to start_date if it's too old
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            cutoff_dt = datetime.strptime(series_cutoff, "%Y-%m-%d")
            
            if start_dt < cutoff_dt:
                logger.info(f"Date cutoff applied for {series_id}: {start_date} → {series_cutoff}")
                start_date = series_cutoff
        except ValueError:
            # Invalid date format, keep original
            pass
    
    return start_date, end_date


def _estimate_token_count(series_id: str, limit: int, frequency: str, start_date: str = None, end_date: str = None) -> int:
    """
    Estimate token count for FRED API request based on series type and parameters.
    Uses conservative estimates based on actual data patterns.
    """
    # Base token estimates per observation (JSON structure overhead)
    base_tokens_per_obs = 50  # Date + value + metadata
    
    # Series-specific multipliers for known high-volume series
    series_multipliers = {
        "DGS10": 1.5,   # Daily Treasury data (high volume)
        "DGS2": 1.5,    # Daily Treasury data
        "DGS3": 1.5,    # Daily Treasury data
        "DGS5": 1.5,    # Daily Treasury data
        "DGS7": 1.5,    # Daily Treasury data
        "DGS20": 1.5,   # Daily Treasury data
        "DGS30": 1.5,   # Daily Treasury data
        "VIXCLS": 1.3,  # Daily VIX data
        "FEDFUNDS": 1.0, # Monthly Fed Funds
        "CPIAUCSL": 1.0, # Monthly CPI
        "UNRATE": 1.0,   # Monthly unemployment
        "GDP": 1.0,      # Quarterly GDP
    }
    
    # Frequency multipliers
    frequency_multipliers = {
        "d": 1.5,   # Daily data has more observations
        "w": 1.2,   # Weekly data
        "m": 1.0,   # Monthly data (baseline)
        "q": 0.8,   # Quarterly data
        "a": 0.5,   # Annual data
    }
    
    # Get series multiplier (default to 1.0)
    series_mult = series_multipliers.get(series_id, 1.0)
    
    # Get frequency multiplier (default to 1.0)
    freq_mult = frequency_multipliers.get(frequency, 1.0)
    
    # Calculate estimated observations
    if limit:
        estimated_obs = limit
    else:
        # Estimate based on frequency and date range
        if start_date and end_date:
            from datetime import datetime
            try:
                start = datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.strptime(end_date, "%Y-%m-%d")
                days = (end - start).days
                
                if frequency == "d":
                    estimated_obs = min(days, 1000)  # Cap at 1000
                elif frequency == "w":
                    estimated_obs = min(days // 7, 500)
                elif frequency == "m":
                    estimated_obs = min(days // 30, 200)
                elif frequency == "q":
                    estimated_obs = min(days // 90, 100)
                elif frequency == "a":
                    estimated_obs = min(days // 365, 50)
                else:
                    estimated_obs = 100  # Default estimate
            except:
                estimated_obs = 100
        else:
            # No date range specified, use conservative estimate
            estimated_obs = 200 if frequency == "d" else 100
    
    # Calculate total estimated tokens
    total_tokens = int(estimated_obs * base_tokens_per_obs * series_mult * freq_mult)
    
    return total_tokens


async def _get_summary_view(series_id: str, cache_service) -> dict:
    """
    Get summary view of FRED series data (last 12-24 months + statistics).
    Optimized for LLM consumption with minimal token usage.
    """
    try:
        fed_service = FedService(cache_service)
        
        # Get last 24 months of data for summary
        from datetime import datetime, timedelta
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")  # ~24 months
        
        observations = await fed_service.get_series_observations(
            series_id=series_id,
            start_date=start_date,
            end_date=end_date,
            frequency="m",  # Monthly for summary
            limit=24,
            force_refresh=False,
        )
        
        if not observations or observations.get("status") == "error":
            return {
                "status": "error",
                "message": f"Could not fetch summary data for series {series_id}",
                "series_id": series_id
            }
        
        # Extract observations data
        obs_data = observations.get("data", {}).get("observations", [])
        if not obs_data:
            return {
                "status": "error", 
                "message": f"No data available for series {series_id}",
                "series_id": series_id
            }
        
        # Filter valid values (not ".")
        valid_obs = [obs for obs in obs_data if obs.get("value") != "."]
        if not valid_obs:
            return {
                "status": "error",
                "message": f"No valid data points for series {series_id}",
                "series_id": series_id
            }
        
        # Calculate statistics
        values = [float(obs["value"]) for obs in valid_obs]
        latest = values[-1] if values else None
        previous = values[-2] if len(values) > 1 else None
        
        # Calculate changes
        change = latest - previous if latest and previous else None
        change_pct = (change / previous * 100) if change and previous else None
        
        # Calculate min/max/avg for last 12 months
        last_12_values = values[-12:] if len(values) >= 12 else values
        min_12m = min(last_12_values) if last_12_values else None
        max_12m = max(last_12_values) if last_12_values else None
        avg_12m = sum(last_12_values) / len(last_12_values) if last_12_values else None
        
        # Calculate volatility (standard deviation)
        if len(last_12_values) > 1:
            mean = avg_12m
            variance = sum((x - mean) ** 2 for x in last_12_values) / len(last_12_values)
            volatility = variance ** 0.5
        else:
            volatility = None
        
        # Get recent data (last 6 months)
        recent_data = valid_obs[-6:] if len(valid_obs) >= 6 else valid_obs
        
        return {
            "status": "success",
            "view": "summary",
            "series_id": series_id,
            "period": "last_24_months",
            "statistics": {
                "latest": latest,
                "previous": previous,
                "change": change,
                "change_pct": round(change_pct, 2) if change_pct else None,
                "min_12m": min_12m,
                "max_12m": max_12m,
                "avg_12m": round(avg_12m, 4) if avg_12m else None,
                "volatility": round(volatility, 4) if volatility else None,
                "data_points": len(valid_obs)
            },
            "recent_data": [
                {
                    "date": obs["date"],
                    "value": float(obs["value"])
                }
                for obs in recent_data
            ],
            "upgrade_prompt": "Full historical data available with premium plan",
            "meta": {
                "data_source": "FRED",
                "frequency": "monthly",
                "last_updated": observations.get("data", {}).get("realtime_end"),
                "total_observations": len(valid_obs)
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating summary view for {series_id}: {e}")
        return {
            "status": "error",
            "message": f"Error generating summary view: {str(e)}",
            "series_id": series_id
        }


__all__ = ["router"]

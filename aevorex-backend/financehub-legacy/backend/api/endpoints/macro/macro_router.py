"""
Central Macro API Router - Complete Economic Data Integration

This is the central router for all macroeconomic data endpoints.
It aggregates all subrouters including ECB, BUBOR, yield curves,
fixing rates, Federal Reserve data, inflation, and unemployment.

**Complete Endpoint Coverage:**
- **ECB**: /ecb/yield-curve/* (unified, real data)
- **BUBOR**: /bubor/* (unified, real MNB data)
- **Curves**: /curve/ust, /curve/compare (consolidated)
- **Fixings**: /fixing/estr, /fixing/euribor/*
- **Fed Policy**: /fed-policy/rates (complete monetary policy key rates with multi-series support)
- **Fed Series**: /fed-series/fred/* (complete FRED API integration)

**Complete FRED API Integration:**
- **Series Metadata**: /fed-series/fred/series/{id} - Comprehensive series information
- **Time Series Data**: /fed-series/fred/observations/{id} - Historical economic data with advanced features
- **Series Search**: /fed-series/fred/search - Discover data by keywords
- **Related Series**: /fed-series/fred/series/{id}/related - Intelligent tag-based relationship discovery
- **Categories**: /fed-series/fred/categories - Browse hierarchical data classification
- **Observations Alias**: /fed-series/fred/series/{id}/observations - Nested path support
- **Presets**: /fed-series/fred/presets - Pre-configured economic data collections

**Monetary Policy Key Rates Available:**
- FEDFUNDS: Fed Funds Effective Rate (primary policy rate)
- DFEDTARU: Target Range Upper Bound (Fed's target rate ceiling)
- DFEDTARL: Target Range Lower Bound (Fed's target rate floor)
- IORB: Interest on Reserve Balances (rate paid on bank reserves)
- EFFR: Effective Federal Funds Rate (alternative symbol)

**Enhanced Features:**
- **Multi-Series Support**: Combine multiple monetary policy rates in single requests
- **Intelligent Related Series**: Advanced tag-based relationship discovery for economic connections
- **Robust Error Handling**: Graceful fallback mechanisms for all FRED API endpoints
- **Advanced Data Processing**: Frequency transformations, unit conversions, normalization statistics
- **Comprehensive Caching**: 1-hour TTL for optimal performance across all endpoints

**Economic Data Categories (800,000+ FRED Series):**
- Monetary Policy: Fed funds, target ranges, reserve balances, discount rates
- Inflation: CPI, PCE, inflation expectations, TIPS yields, commodity prices
- Employment: Unemployment rates, payroll data, labor force participation
- GDP & National Accounts: Real GDP, GDP deflator, consumption, investment
- Financial Markets: Treasury yields, corporate bonds, stock indices
- International: Exchange rates, trade data, global economic indicators
- Banking: Bank reserves, lending rates, credit conditions
- Housing: Home prices, construction, mortgage data
- Energy: Oil prices, natural gas, energy consumption
- Regional: State and metropolitan area economic data

**Data Sources:**
- FRED API (Federal Reserve Economic Data) - 800,000+ time series
- ECB SDMX API (European Central Bank)
- MNB Excel (Hungarian National Bank)
- EMMI API (Euribor rates)
- US Treasury (yield curve data)

**MCP Agent Integration:**
This API provides comprehensive economic data access for MCP agents,
enabling sophisticated financial analysis, research, and decision support
with real-time and historical data from official sources.
"""

from fastapi import APIRouter

# Create main macro router WITHOUT prefix (will be added in __init__.py)
router = APIRouter(tags=["Macro"])


from .handlers.bubor_handler import router as bubor_handler
from .handlers.curve_handler import router as curve_handler
from .handlers.fixing_handler import router as fixing_handler
from .handlers.fed_policy_handler import router as fed_policy_handler
from .handlers.fed_series_handler import router as fed_series_handler
from .handlers.fed_search_handler import router as fed_search_handler
from .handlers.ecb_handler import router as ecb_handler
from .handlers.inflation_handler import router as inflation_handler
from .handlers.unemployment_handler import router as unemployment_handler

router.include_router(bubor_handler, prefix="/bubor")
router.include_router(curve_handler, prefix="/curve")
router.include_router(fixing_handler, prefix="/fixing")
router.include_router(fed_policy_handler, prefix="/fed-policy")
router.include_router(fed_series_handler, prefix="/fed-series")
router.include_router(fed_search_handler, prefix="/fed-search")
# Add alias for /fed/series -> /fed-series/fred/series
router.include_router(fed_series_handler, prefix="/fed")
router.include_router(ecb_handler, prefix="/ecb")
router.include_router(inflation_handler, prefix="/inflation")
router.include_router(unemployment_handler, prefix="/unemployment")

__all__ = ["router"]
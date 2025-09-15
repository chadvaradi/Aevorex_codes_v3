# Macro API Endpoints - Complete Documentation

## Overview

The Macro API provides comprehensive access to macroeconomic data from major central banks and financial institutions. This API is designed for MCP (Model Context Protocol) agents and provides real-time, historical, and analytical data for equity research and financial analysis.

## ⚠️ **Important: Data Type Transparency**

All FRED series responses now include `data_type_info` to clarify the nature and quality of the data:

```json
{
  "data_type_info": {
    "data_type": "spot_exchange_rate",
    "quality": "high",
    "description": "Real-time spot exchange rate",
    "frequency": "daily",
    "source": "FRED"
  }
}
```

**Data Types:**
- `spot_exchange_rate`: Real-time spot exchange rates (high quality)
- `exchange_rate_average`: Monthly average exchange rates (medium quality)
- `spot_commodity_price`: Real-time spot commodity prices (high quality)
- `commodity_price_index`: Commodity price indices (medium quality, not spot prices)
- `policy_rate`: Central bank policy rates (high quality)

**Quality Levels:**
- `high`: Real-time, reliable data
- `medium`: Monthly averages or indices (not real-time spot prices)
- `unknown`: Unknown data type

**Critical Note:** Some commodities (like GOLD, SILVER) are only available as price indices, not real-time spot prices. Always check the `data_type_info` to understand what data you're receiving.

## 🚨 **Product-Level Transparency**

The API now provides clear status indicators and warning messages:

### **Response Status Types**
- `"status": "success"` - Exact data requested (spot price, spot rate)
- `"status": "warning"` - Alternative data provided with clear explanation
- `"status": "error"` - No suitable data available

### **Warning Messages**
When alternative data is provided, you'll receive clear warnings:

```json
{
  "status": "warning",
  "message": "Spot GOLD not available in FRED. Returned price index instead.",
  "data": { ... }
}
```

### **Availability Matrix**
- **✅ AVAILABLE**: Oil (WTI, Brent), Major FX (EUR/USD, GBP/USD, etc.), Fed Policy Rates
- **⚠️ LIMITED**: Gold/Silver (indices only), Emerging FX (monthly averages)
- **❌ NOT AVAILABLE**: Platinum, Palladium, Wheat, Corn, Soybeans, BRL/USD, INR/USD

### **User Trust Principles**
1. **No Misleading Data**: Never return EUR/USD when user asks for HUF/USD
2. **Clear Warnings**: Always explain when providing alternative data
3. **Explicit Limitations**: Clear "not available" messages for unsupported requests

## Available Data Sources

- **FRED API**: Federal Reserve Economic Data (US)
- **ECB SDMX API**: European Central Bank (EU)
- **MNB Excel**: Hungarian National Bank (HU)
- **EMMI API**: Euribor rates (EU)
- **US Treasury**: Official yield curve data (US)

## Complete Endpoint Coverage

### 1. Federal Reserve Policy Rates
**Endpoint:** `GET /api/v1/macro/fed-policy/rates`

**Supported Monetary Policy Key Rates:**
- **FEDFUNDS**: Fed Funds Effective Rate (primary policy rate)
- **DFEDTARU**: Target Range Upper Bound (Fed's target rate ceiling)
- **DFEDTARL**: Target Range Lower Bound (Fed's target rate floor)
- **IORB**: Interest on Reserve Balances (rate paid on bank reserves)
- **EFFR**: Effective Federal Funds Rate (alternative symbol)

**Usage Examples:**
```bash
# Single rate
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=FEDFUNDS"

# Multiple rates (use separate series parameters)
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=FEDFUNDS&series=DFEDTARU&series=DFEDTARL"

# Target range only
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=DFEDTARU&series=DFEDTARL"

# Interest on Reserve Balances
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=IORB"

# Date range with multiple rates
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=FEDFUNDS&series=DFEDTARU&series=DFEDTARL&start_date=2025-09-01&end_date=2025-09-15"

# All key rates together
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=FEDFUNDS&series=DFEDTARU&series=DFEDTARL&series=IORB"
```

**Important:** For multiple series, use separate `series` parameters (not comma-separated). The API supports combining any number of monetary policy rates in a single request.

### 2. ECB Yield Curve Data
**Endpoints:**
- `GET /api/v1/macro/ecb/yield-curve` - Complete yield curve
- `GET /api/v1/macro/ecb/yield-curve/latest` - Latest data
- `GET /api/v1/macro/ecb/yield-curve/{maturity}` - Specific maturity

**Data Source:** ECB SDMX API
**Maturities:** 3M, 6M, 9M, 1Y, 2Y, 3Y, 4Y, 5Y, 6Y, 7Y, 8Y, 9Y, 10Y, 11Y, 12Y, 13Y, 14Y, 15Y, 16Y, 17Y, 18Y, 19Y, 20Y, 21Y, 22Y, 23Y, 24Y, 25Y, 26Y, 27Y, 28Y, 29Y, 30Y

### 3. BUBOR (Hungarian Interbank Rates)
**Endpoints:**
- `GET /api/v1/macro/bubor/` - Complete BUBOR curve
- `GET /api/v1/macro/bubor/latest` - Latest fixing
- `GET /api/v1/macro/bubor/{tenor}` - Specific tenor

**Data Source:** MNB Excel (bubor2.xls)
**Tenors:** O/N, 1W, 2W, 1M, 2M, 3M, 4M, 5M, 6M, 7M, 8M, 9M, 10M, 11M, 12M

### 4. US Treasury Yield Curve
**Endpoint:** `GET /api/v1/macro/curve/ust`

**Data Source:** US Treasury official website
**Maturities:** 1M, 1.5M, 2M, 3M, 4M, 6M, 1Y, 2Y, 3Y, 5Y, 7Y, 10Y, 20Y, 30Y

### 5. Yield Curve Comparison
**Endpoint:** `GET /api/v1/macro/curve/compare`

**Features:**
- ECB vs US Treasury comparison
- Mathematical analysis (spreads, steepness, volatility)
- Real-time data integration
- Statistical analysis

### 6. Fixing Rates
**Endpoints:**
- `GET /api/v1/macro/fixing/estr` - ECB €STR (Euro Short-Term Rate)
- `GET /api/v1/macro/fixing/euribor/{tenor}` - Euribor rates

**Data Sources:**
- €STR: ECB SDMX API
- Euribor: EMMI API (euribor-rates.eu)

### 7. Federal Reserve Data - Complete FRED API Integration
**Base Endpoint:** `/api/v1/macro/fed-series/fred/`

**Complete FRED Endpoint Coverage:**

#### Series Metadata
- **Endpoint**: `/api/v1/macro/fed-series/fred/series/{series_id}`
- **Purpose**: Get comprehensive series information
- **Returns**: Title, description, frequency, units, observation dates, popularity, notes
- **Examples**: FEDFUNDS, IORB, CPI, GDP, UNRATE

#### Time Series Data - COMPLETE ECONOMIC DATA WITH ADVANCED FEATURES
- **Endpoint**: `/api/v1/macro/fed-series/fred/observations/{series_id}`
- **Purpose**: Get comprehensive historical economic data with advanced processing capabilities
- **Parameters**: 
  - `start_date` (YYYY-MM-DD): Start date for data range
  - `end_date` (YYYY-MM-DD): End date for data range
  - `frequency` (d/w/bw/m/q/sa/a): Data frequency transformation
  - `units` (lin/chg/ch1/pch/pc1/pca/cch/cca/log): Unit transformations
  - `force_refresh` (bool): Bypass cache and force fresh data
- **Returns**: Complete time series with advanced features:
  - Historical observations with precise dates and values
  - Real-time and vintage data support
  - Automatic frequency fallback (e.g., Q→M if quarterly not supported)
  - Value normalization (converts "." to null for missing data)
  - Normalization statistics (missing value counts and percentages)
  - Data quality indicators and completeness metrics
- **Advanced Features**:
  - **Frequency Transformation**: 7 frequency types (daily, weekly, monthly, quarterly, annual, etc.)
  - **Unit Transformations**: 9 transformation types (levels, changes, percent changes, log, compounded rates)
  - **Missing Value Handling**: Intelligent "." to null conversion with statistics
  - **Data Quality Assessment**: Missing value counts, percentages, and quality metrics
  - **Automatic Fallback**: Graceful handling of unsupported parameters
- **Usage Examples**:
  - **Monetary Policy**: `/fred/observations/FEDFUNDS?start_date=2025-08-01&end_date=2025-09-01`
  - **Inflation Analysis**: `/fred/observations/CPIAUCSL?frequency=m&units=pch` (percent change)
  - **Economic Growth**: `/fred/observations/GDP?frequency=q&units=chg` (quarterly change)
  - **Labor Market**: `/fred/observations/UNRATE?frequency=m&units=lin`
  - **Financial Markets**: `/fred/observations/DGS10?frequency=d&units=lin` (10-Year Treasury)
  - **Yield Curve**: `/fred/observations/T10Y2Y?frequency=d` (10Y-2Y spread)

#### Series Search
- **Endpoint**: `/api/v1/macro/fed-series/fred/search`
- **Purpose**: Discover economic data by keywords
- **Parameters**: query, limit, offset
- **Returns**: Ranked search results by popularity
- **Examples**: "inflation" → CPI, PCE, TIPS yields; "unemployment" → labor data

#### Related Series Discovery - INTELLIGENT ECONOMIC CONNECTIONS
- **Endpoint**: `/api/v1/macro/fed-series/fred/series/{series_id}/related`
- **Purpose**: Find connected economic indicators using intelligent tag-based relationships
- **Method**: Advanced 3-step discovery process:
  1. **Tag Analysis**: Extract tags from the source series
  2. **Related Tag Discovery**: Find semantically related tags using FRED's classification
  3. **Series Matching**: Return series with similar economic themes and relationships
- **Returns**: Related series with popularity filtering and relevance scoring
- **Features**:
  - **Intelligent Filtering**: Removes original series and filters by relevance
  - **Popularity Ranking**: Sorts results by economic importance
  - **Comprehensive Coverage**: Discovers 5+ related series per request
  - **Economic Context**: Maintains thematic relationships (monetary policy, inflation, etc.)
- **Usage Examples**:
  - **Monetary Policy**: `/fred/series/FEDFUNDS/related` → Commercial paper, tax receipts, bank reserves
  - **Inflation Analysis**: `/fred/series/CPIAUCSL/related` → PCE, wage data, commodity prices
  - **Economic Growth**: `/fred/series/GDP/related` → GDP components, productivity, employment
  - **Labor Market**: `/fred/series/UNRATE/related` → Employment data, wage indicators
- **Cache**: 1 hour TTL for optimal performance

#### Categories Browser
- **Endpoint**: `/api/v1/macro/fed-series/fred/categories`
- **Purpose**: Browse hierarchical data classification
- **Returns**: Category structure for systematic data discovery
- **Usage**: Navigate economic data themes and sectors

#### Observations Alias
- **Endpoint**: `/api/v1/macro/fed-series/fred/series/{series_id}/observations`
- **Purpose**: Alternative nested path for observations
- **Functionality**: Same as time series data but with nested URL structure

**Key Economic Data Categories Available:**
- **Monetary Policy**: Fed funds, target ranges, reserve balances, discount rates
- **Inflation**: CPI, PCE, inflation expectations, TIPS yields, commodity prices
- **Employment**: Unemployment rates, payroll data, labor force participation, job openings
- **GDP & National Accounts**: Real GDP, GDP deflator, consumption, investment, trade
- **Financial Markets**: Treasury yields, corporate bonds, stock indices, mortgage rates
- **International**: Exchange rates, trade data, global economic indicators
- **Banking**: Bank reserves, lending rates, credit conditions, financial stress
- **Housing**: Home prices, construction, mortgage data, housing starts
- **Energy**: Oil prices, natural gas, energy consumption, production
- **Regional**: State and metropolitan area economic data

**Data Source:** Federal Reserve Economic Data (FRED) API
**Coverage:** 800,000+ time series
**Update Frequency:** Real-time to monthly depending on series
**Cache:** 1 hour TTL

#### **ADVANCED DATA PROCESSING FEATURES**

**🔧 Frequency Transformations:**
- `d` = Daily (business days for most series)
- `w` = Weekly (ending Friday)
- `bw` = Biweekly (every other week)
- `m` = Monthly (end of month)
- `q` = Quarterly (end of quarter)
- `sa` = Semiannual (twice per year)
- `a` = Annual (end of year)

**📊 Unit Transformations:**
- `lin` = Levels (original units)
- `chg` = Change (period-over-period change)
- `ch1` = Change from Year Ago (year-over-year change)
- `pch` = Percent Change (period-over-period percent change)
- `pc1` = Percent Change from Year Ago (year-over-year percent change)
- `pca` = Compounded Annual Rate of Change
- `cch` = Continuously Compounded Rate of Change
- `cca` = Continuously Compounded Annual Rate of Change
- `log` = Natural Log (logarithmic transformation)

**📈 Data Quality & Normalization:**
- **Missing Value Handling**: Automatic "." to null conversion
- **Normalization Statistics**: Missing value counts, percentages, and quality metrics
- **Frequency Fallback**: Graceful handling when requested frequency not supported
- **Data Quality Indicators**: Completeness assessment and quality metrics
- **Real-time vs Vintage Data**: Support for both current and historical data revisions

**🎯 Response Structure Enhancement:**
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
    "observations": [
      {
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

### 8. Fed Policy Key Rates
**Endpoint**: `/api/v1/macro/fed-policy/rates`

**Supported Monetary Policy Rates:**
- FEDFUNDS: Fed Funds Effective Rate (primary policy rate)
- DFEDTARU: Target Range Upper Bound (Fed's target rate ceiling)
- DFEDTARL: Target Range Lower Bound (Fed's target rate floor)
- IORB: Interest on Reserve Balances (rate paid on bank reserves)
- EFFR: Effective Federal Funds Rate (alternative symbol)

**Data Source:** FRED API
**Update Frequency:** Daily
**Cache:** 1 hour TTL

## Technical Specifications

### Authentication
- **Public Endpoints**: No JWT required for macro data
- **Rate Limiting**: 1 hour cache TTL for most endpoints
- **Data Freshness**: Daily updates from official sources

### Response Format
All endpoints return consistent JSON responses with:
- `status`: "success" or "error"
- `source`: Data provider (FRED, ECB, MNB, etc.)
- `data`: Actual data payload
- `date_range`: Time period covered
- `last_updated`: Timestamp of last data fetch
- `cached`: Boolean indicating if data is cached

### Error Handling
- Graceful degradation for API failures
- Structured error messages
- Fallback mechanisms where available
- No mock data - only real sources

## MCP Agent Integration

This API is specifically designed for MCP agents to provide:
1. **Real-time monetary policy data** for Fed, ECB, and other central banks
2. **Historical analysis** with configurable date ranges
3. **Cross-currency comparisons** (EUR, USD, HUF)
4. **Yield curve analysis** with mathematical insights
5. **Fixing rate data** for overnight and term rates

## Data Quality & Reliability

- **Official Sources Only**: All data comes from official central bank APIs
- **No Mock Data**: Real-time data from authoritative sources
- **Cache Strategy**: 1-hour TTL for performance with real-time capability
- **Error Recovery**: Graceful handling of API failures
- **Data Validation**: Structured responses with metadata

## Usage for Equity Research

This API provides the foundation for:
- **Monetary Policy Analysis**: Fed, ECB, and other central bank rates
- **Yield Curve Analysis**: Term structure analysis and comparisons
- **Currency Analysis**: Cross-currency rate comparisons
- **Risk Assessment**: Policy rate changes and market implications
- **Historical Context**: Long-term trend analysis

## Support

For technical support or data questions, refer to the individual endpoint documentation in the OpenAPI specification at `/docs`.

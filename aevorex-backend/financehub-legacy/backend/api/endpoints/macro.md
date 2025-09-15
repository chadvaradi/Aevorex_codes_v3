# Macro Data Endpoints

**Category:** Macro Data  
**Total Endpoints:** 18  
**Authentication:** JWT required for all endpoints  
**Caching:** 1 hour (unless specified otherwise)

This category provides access to central bank rates, yield curves, and economic indicators from major financial institutions including the ECB, Federal Reserve, and Hungarian National Bank.

---

## BUBOR (Budapest Interbank Offered Rate)

### 1. GET /api/v1/macro/bubor/

**Description:** Returns complete BUBOR curve data for all available tenors.

**Parameters:**
- **Query:**
  - `start_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `end_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)

**Response:**
```json
{
  "status": "success",
  "provider": "mnb_bubor",
  "data": {
    "curve": {
      "2025-09-12": {
        "O/N": 6.5,
        "1W": 6.5,
        "2W": 6.5,
        "1M": 6.5,
        "2M": 6.5,
        "3M": 6.5,
        "6M": 6.47,
        "9M": 6.47,
        "12M": 6.46
      }
    }
  }
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/bubor/?start_date=2025-09-01&end_date=2025-09-12"
```

---

### 2. GET /api/v1/macro/bubor/latest

**Description:** Returns the latest BUBOR fixing (most recent day's data).

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "provider": "mnb_bubor",
  "date": "2025-09-12",
  "rates": {
    "O/N": 6.5,
    "1W": 6.5,
    "2W": 6.5,
    "1M": 6.5,
    "2M": 6.5,
    "3M": 6.5,
    "6M": 6.47,
    "9M": 6.47,
    "12M": 6.46
  }
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/bubor/latest"
```

---

### 3. GET /api/v1/macro/bubor/{tenor}

**Description:** Returns BUBOR rate for a specific tenor.

**Parameters:**
- **Path:**
  - `tenor` (string, required): Tenor code (O/N, 1W, 2W, 1M, 2M, 3M, 4M, 5M, 6M, 7M, 8M, 9M, 10M, 11M, 12M)

**Response:**
```json
{
  "status": "success",
  "provider": "mnb_bubor",
  "tenor": "1M",
  "data": {
    "2025-08-15": 6.5,
    "2025-08-18": 6.5,
    "2025-08-19": 6.5,
    "2025-09-12": 6.5
  }
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/bubor/1M"
```

---

## Yield Curves


### 4. GET /api/v1/macro/curve/ust

**Description:** Returns US Treasury yield curve data.

**Parameters:**
- **Query:**
  - `start_date` (string, optional): Start date in ISO 8601 format
  - `end_date` (string, optional): End date in ISO 8601 format

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "yields": {
        "1M": 5.25,
        "3M": 5.28,
        "6M": 5.31,
        "1Y": 5.35,
        "2Y": 5.42,
        "5Y": 5.58,
        "10Y": 5.72,
        "30Y": 5.85
      }
    }
  ],
  "metadata": {
    "source": "FRED",
    "last_updated": "2024-01-15T09:00:00Z"
  }
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/curve/ust?start_date=2024-01-01&end_date=2024-01-31"
```

---

### 5. GET /api/v1/macro/curve/compare

**Description:** Compares yield curves from different central banks.

**Parameters:**
- **Query:**
  - `curve1` (string, optional, default: "ecb"): First curve identifier
  - `curve2` (string, optional, default: "ust"): Second curve identifier
  - `start_date` (string, optional): Start date in ISO 8601 format
  - `end_date` (string, optional): End date in ISO 8601 format

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "curves": {
        "ecb": {
          "1Y": 2.85,
          "2Y": 3.12,
          "10Y": 3.78
        },
        "ust": {
          "1Y": 5.35,
          "2Y": 5.42,
          "10Y": 5.72
        }
      },
      "spreads": {
        "1Y": 2.50,
        "2Y": 2.30,
        "10Y": 1.94
      }
    }
  ]
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/curve/compare?curve1=ecb&curve2=ust"
```

---

## Fixing Rates

### 6. GET /api/v1/macro/fixing/estr

**Description:** Returns ECB €STR (Euro Short-Term Rate) overnight rate data.

**Parameters:**
- **Query:**
  - `date` (string, optional): Specific date in ISO 8601 format

**Response:**
```json
{
  "rate": 3.75,
  "date": "2024-01-15",
  "currency": "EUR",
  "change": 0.0,
  "change_percent": 0.0
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/fixing/estr?date=2024-01-15"
```

---

### 7. GET /api/v1/macro/fixing/euribor/{tenor}

**Description:** Returns Euribor fixing rate for specific tenor.

**Parameters:**
- **Path:**
  - `tenor` (string, required): Tenor code (1M, 3M, 6M, 12M)

**Response:**
```json
{
  "tenor": "3M",
  "rate": 3.85,
  "date": "2024-01-15",
  "currency": "EUR",
  "change": 0.05,
  "change_percent": 1.32
}
```

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/macro/fixing/euribor/3M
```

---


---

## Federal Reserve Data

### 8. GET /api/v1/macro/fed-policy/rates

**Description:** Returns US Federal Reserve monetary policy key rates from FRED API with complete historical data.

**Supported Monetary Policy Rates:**
- **FEDFUNDS**: Fed Funds Effective Rate (primary policy rate)
- **DFEDTARU**: Target Range Upper Bound (Fed's target rate ceiling)  
- **DFEDTARL**: Target Range Lower Bound (Fed's target rate floor)
- **IORB**: Interest on Reserve Balances (rate paid on bank reserves)
- **EFFR**: Effective Federal Funds Rate (alternative symbol for FEDFUNDS)

**Parameters:**
- **Query:**
  - `series` (array, optional, default: ["EFFR"]): Array of FRED series symbols to retrieve
  - `start_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `end_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)
  - `force_refresh` (boolean, optional, default: false): Force data refresh from FRED

**Response:**
```json
{
  "source": "FRED",
  "symbols": ["FEDFUNDS"],
  "date_range": {
    "start": "2025-08-16",
    "end": "2025-09-15"
  },
  "data": {
    "status": "success",
    "source": "FRED",
    "series": {
      "FEDFUNDS": {
        "title": "FEDFUNDS",
        "units": "lin",
        "frequency": "Daily",
        "observations": [
          {
            "date": "2025-09-15",
            "value": 4.33
          }
        ]
      }
    },
    "date_range": {
      "start": "2025-08-16",
      "end": "2025-09-15"
    },
    "last_updated": "2025-09-15T15:10:45.771465"
  },
  "cached": false
}
```

**Usage Examples:**
```bash
# Single rate
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=FEDFUNDS"

# Target range (upper and lower bounds)
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=DFEDTARU"
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=DFEDTARL"

# Interest on Reserve Balances
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=IORB"

# Date range
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=FEDFUNDS&start_date=2025-09-01&end_date=2025-09-15"

# Force refresh
curl "http://localhost:8084/api/v1/macro/fed-policy/rates?series=FEDFUNDS&force_refresh=true"
```

**Data Source:** Federal Reserve Economic Data (FRED) API  
**Update Frequency:** Daily  
**Cache:** 1 hour TTL  
**Note:** Multiple series must be requested separately (comma-separated lists return 400 error)

---

## FRED (Federal Reserve Economic Data)

### 9. GET /api/v1/macro/fed-series/fred/series/{series_id}

**Description:** Returns FRED series information.

**Parameters:**
- **Path:**
  - `series_id` (string, required): FRED series identifier

**Response:**
```json
{
  "id": "FEDFUNDS",
  "title": "Federal Funds Effective Rate",
  "units": "Percent",
  "frequency": "Monthly",
  "seasonal_adjustment": "Not Seasonally Adjusted",
  "last_updated": "2024-01-15T09:00:00Z"
}
```

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/macro/fed-series/fred/series/FEDFUNDS
```

---

### 10. GET /api/v1/macro/fed-series/fred/observations/{series_id}

**Description:** Returns time series observations for a FRED series.

**Parameters:**
- **Path:**
  - `series_id` (string, required): FRED series identifier
- **Query:**
  - `start_date` (string, optional): Start date in ISO 8601 format
  - `end_date` (string, optional): End date in ISO 8601 format

**Response:**
```json
{
  "observations": [
    {
      "date": "2024-01-01",
      "value": 5.25
    },
    {
      "date": "2024-01-02", 
      "value": 5.25
    }
  ],
  "metadata": {
    "series_id": "FEDFUNDS",
    "units": "Percent",
    "count": 2
  }
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/fed-series/fred/observations/FEDFUNDS?start_date=2024-01-01&end_date=2024-01-31"
```

---

### 11. GET /api/v1/macro/fed-series/fred/categories

**Description:** Returns list of FRED categories.

**Parameters:** None

**Response:**
```json
{
  "categories": [
    {
      "id": 1,
      "name": "Money, Banking, & Finance",
      "parent_id": null
    },
    {
      "id": 2,
      "name": "Interest Rates",
      "parent_id": 1
    }
  ]
}
```

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/macro/fed-series/fred/categories
```

---

## FRED Search

### 12. GET /api/v1/macro/fed-search/series

**Description:** Search FRED series by keyword.

**Parameters:**
- **Query:**
  - `query` (string, required): Search keyword

**Response:**
```json
{
  "series": [
    {
      "id": "FEDFUNDS",
      "title": "Federal Funds Effective Rate",
      "units": "Percent",
      "frequency": "Monthly"
    }
  ],
  "count": 1
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/fed-search/series?query=federal%20funds"
```

---

### 13. GET /api/v1/macro/fed-search/metadata/{series_id}

**Description:** Returns detailed metadata for a FRED series.

**Parameters:**
- **Path:**
  - `series_id` (string, required): FRED series identifier

**Response:**
```json
{
  "id": "FEDFUNDS",
  "title": "Federal Funds Effective Rate",
  "units": "Percent",
  "frequency": "Monthly",
  "seasonal_adjustment": "Not Seasonally Adjusted",
  "last_updated": "2024-01-15T09:00:00Z",
  "notes": "Averages of daily figures.",
  "source": "Board of Governors of the Federal Reserve System"
}
```

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/macro/fed-search/metadata/FEDFUNDS
```

---

### 14. GET /api/v1/macro/fed-search/related/{series_id}

**Description:** Returns related FRED series for a given series.

**Parameters:**
- **Path:**
  - `series_id` (string, required): FRED series identifier

**Response:**
```json
{
  "related_series": [
    {
      "id": "DFF",
      "title": "Federal Funds Rate",
      "correlation": 0.95
    }
  ],
  "count": 1
}
```

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/macro/fed-search/related/FEDFUNDS
```

---

## ECB Yield Curve Data

### 15. GET /api/v1/macro/ecb/yield-curve

**Description:** Returns the latest ECB (European Central Bank) yield curve data for all available maturities.

**Parameters:** None

**Response:**
```json
{
  "status": "success",
  "provider": "ecb_official",
  "date": "2025-09-11",
  "curve": {
    "3M": 1.944638,
    "6M": 1.933502,
    "9M": 1.92722,
    "1Y": 1.925315,
    "2Y": 1.953217,
    "3Y": 2.02185,
    "4Y": 2.114911,
    "5Y": 2.220959,
    "6Y": 2.332068,
    "7Y": 2.442849,
    "8Y": 2.549733,
    "9Y": 2.650451,
    "10Y": 2.743653,
    "11Y": 2.828637,
    "12Y": 2.905146,
    "13Y": 2.973229,
    "14Y": 3.033135,
    "15Y": 3.085241,
    "16Y": 3.130003,
    "17Y": 3.167913,
    "18Y": 3.19948,
    "19Y": 3.225211,
    "20Y": 3.245598,
    "21Y": 3.261113,
    "22Y": 3.272201,
    "23Y": 3.279281,
    "24Y": 3.282742,
    "25Y": 3.282947,
    "26Y": 3.280229,
    "27Y": 3.274895,
    "28Y": 3.267227,
    "29Y": 3.257484,
    "30Y": 3.245901
  },
  "metadata": {
    "source": "ECB Official Website",
    "url": "https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_area_yield_curves/html/index.en.html",
    "last_updated": "2025-09-11T12:00:00Z",
    "description": "Euro area yield curves - zero coupon yield curves for the euro area",
    "currency": "EUR",
    "data_type": "government_bond_yields"
  }
}
```

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" "https://api.aevorex.com/api/v1/macro/ecb/yield-curve"
```

---

### 16. GET /api/v1/macro/ecb/yield-curve/{maturity}

**Description:** Returns ECB yield curve data for a specific maturity period.

**Parameters:**
- **Path:**
  - `maturity` (string, required): Maturity period (3M, 6M, 9M, 1Y, 2Y, 3Y, 4Y, 5Y, 6Y, 7Y, 8Y, 9Y, 10Y, 11Y, 12Y, 13Y, 14Y, 15Y, 16Y, 17Y, 18Y, 19Y, 20Y, 21Y, 22Y, 23Y, 24Y, 25Y, 26Y, 27Y, 28Y, 29Y, 30Y)

**Response:**
```json
{
  "status": "success",
  "provider": "ecb_official",
  "maturity": "10Y",
  "date": "2025-09-11",
  "yield": 2.743653,
  "metadata": {
    "source": "ECB Official Website",
    "url": "https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_area_yield_curves/html/index.en.html",
    "last_updated": "2025-09-11T12:00:00Z",
    "description": "Euro area government bond yield for 10Y maturity",
    "currency": "EUR",
    "data_type": "government_bond_yield"
  }
}
```

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" "https://api.aevorex.com/api/v1/macro/ecb/yield-curve/10Y"
```

---

## ECB Data

### 17. GET /api/v1/macro/ecb/overview

**Description:** Returns ECB overview data including key economic indicators.

**Parameters:** None

**Response:**
```json
{
  "data": {
    "gdp_growth": 0.3,
    "inflation_rate": 2.9,
    "unemployment_rate": 6.5,
    "policy_rate": 4.25,
    "date": "2024-01-15"
  },
  "metadata": {
    "source": "ECB",
    "last_updated": "2024-01-15T09:00:00Z"
  }
}
```

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/macro/ecb/overview
```

---

### 18. GET /api/v1/macro/inflation/

**Description:** Returns Eurozone Harmonized Index of Consumer Prices (HICP) inflation data.

**Parameters:**
- **Query:**
  - `start_date` (string, optional): Start date in ISO 8601 format
  - `end_date` (string, optional): End date in ISO 8601 format

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "inflation_rate": 2.9,
      "monthly_change": 0.1,
      "yearly_change": -0.5
    }
  ],
  "metadata": {
    "source": "ECB",
    "last_updated": "2024-01-15T09:00:00Z"
  }
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/inflation/?start_date=2024-01-01&end_date=2024-01-31"
```

---

### 19. GET /api/v1/macro/unemployment/

**Description:** Returns Eurozone unemployment rate (HUR) data.

**Parameters:**
- **Query:**
  - `start_date` (string, optional): Start date in ISO 8601 format
  - `end_date` (string, optional): End date in ISO 8601 format

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-15",
      "unemployment_rate": 6.5,
      "monthly_change": 0.0,
      "yearly_change": -0.2
    }
  ],
  "metadata": {
    "source": "ECB",
    "last_updated": "2024-01-15T09:00:00Z"
  }
}
```

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/macro/unemployment/?start_date=2024-01-01&end_date=2024-01-31"
```

---

## Data Sources

- **MNB**: Hungarian National Bank
- **ECB**: European Central Bank  
- **FRED**: Federal Reserve Economic Data
- **Federal Reserve**: Board of Governors

---

**Total Macro Endpoints: 18** ✅

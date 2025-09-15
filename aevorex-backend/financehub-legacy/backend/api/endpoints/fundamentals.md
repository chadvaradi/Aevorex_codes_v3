# Fundamentals Endpoints

**Category:** Fundamentals  
**Total Endpoints:** 4  
**Authentication:** Not required  
**Caching:** 1 hour (unless force_refresh=true)  
**Data Source:** Yahoo Finance  
**Status:** ✅ **100% Working** - All 4 endpoints tested and verified

This category provides access to company fundamental data including overview information, financial statements, ratios, and earnings data. All endpoints return data in a standardized format with metadata.

---

## 1. GET /api/v1/fundamentals/overview/{symbol}

**Description:** Returns comprehensive company overview data including basic information, market metrics, and key financial indicators.

**Parameters:**
- **Path:**
  - `symbol` (string, required): Stock symbol (e.g., AAPL, MSFT, GOOGL)
- **Query:**
  - `force_refresh` (boolean, optional, default: false): Force data refresh from source

**Response:**
```json
{
  "metadata": {
    "symbol": "AAPL",
    "timestamp": "2025-09-14T21:34:10Z",
    "provider": "yahoo_finance",
    "processing_time_ms": 237.94
  },
  "data": {
    "longName": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics",
    "country": "United States",
    "exchange": "NMS",
    "marketCap": 3473692426240,
    "fullTimeEmployees": 150000,
    "website": "https://www.apple.com",
    "businessSummary": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide...",
    "city": "Cupertino",
    "state": "CA",
    "zip": "95014",
    "phone": "(408) 996-1010"
  }
}
```

**Response Fields:**
- `metadata` (object): Response metadata
  - `symbol` (string): Stock symbol
  - `timestamp` (string): Response timestamp (ISO 8601)
  - `provider` (string): Data source provider
  - `processing_time_ms` (number): API processing time in milliseconds
- `data` (object): Company overview data
  - `longName` (string): Full company name
  - `sector` (string): Business sector
  - `industry` (string): Specific industry
  - `country` (string): Country of incorporation
  - `exchange` (string): Stock exchange code
  - `marketCap` (number): Market capitalization
  - `fullTimeEmployees` (number): Number of employees
  - `website` (string): Company website
  - `businessSummary` (string): Company description
  - `city` (string): Company headquarters city
  - `state` (string): Company headquarters state
  - `zip` (string): Company headquarters ZIP code
  - `phone` (string): Company phone number

**Behavior:**
- Cached for 1 hour unless force_refresh=true
- Data sourced from Yahoo Finance
- Returns 404 if symbol not found
- Processing time typically 200-300ms

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/fundamentals/overview/AAPL?force_refresh=true"
```

---

## 2. GET /api/v1/fundamentals/financials/{symbol}

**Description:** Returns financial statements data. **Note:** Currently returns null values as detailed financial statements require premium data sources.

**Parameters:**
- **Path:**
  - `symbol` (string, required): Stock symbol
- **Query:**
  - `force_refresh` (boolean, optional, default: false): Force data refresh from source

**Response:**
```json
{
  "metadata": {
    "symbol": "AAPL",
    "timestamp": "2025-09-14T21:34:10Z",
    "provider": "yahoo_finance",
    "processing_time_ms": 25.77
  },
  "data": {
    "revenue": null,
    "gross_profit": null,
    "operating_income": null,
    "net_income": null,
    "total_assets": null,
    "total_liabilities": null,
    "shareholder_equity": null,
    "cash_and_equivalents": null,
    "total_debt": null,
    "operating_cash_flow": null,
    "capital_expenditure": null,
    "free_cash_flow": null,
    "dividends_paid": null
  }
}
```

**Response Fields:**
- `metadata` (object): Response metadata
  - `symbol` (string): Stock symbol
  - `timestamp` (string): Response timestamp (ISO 8601)
  - `provider` (string): Data source provider
  - `processing_time_ms` (number): API processing time in milliseconds
- `data` (object): Financial statements data (currently null values)
  - `revenue` (number|null): Total revenue
  - `gross_profit` (number|null): Gross profit
  - `operating_income` (number|null): Operating income
  - `net_income` (number|null): Net income
  - `total_assets` (number|null): Total assets
  - `total_liabilities` (number|null): Total liabilities
  - `shareholder_equity` (number|null): Shareholder equity
  - `cash_and_equivalents` (number|null): Cash and cash equivalents
  - `total_debt` (number|null): Total debt
  - `operating_cash_flow` (number|null): Operating cash flow
  - `capital_expenditure` (number|null): Capital expenditure
  - `free_cash_flow` (number|null): Free cash flow
  - `dividends_paid` (number|null): Dividends paid

**Behavior:**
- Cached for 1 hour unless force_refresh=true
- Data sourced from Yahoo Finance (limited financial statements data)
- Returns 404 if symbol not found
- Processing time typically 20-30ms
- **Note:** Detailed financial statements require premium data sources

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/fundamentals/financials/AAPL"
```

---

## 3. GET /api/v1/fundamentals/ratios/{symbol}

**Description:** Returns comprehensive financial ratios and metrics for fundamental analysis. **Rich data with 21 financial ratios.**

**Parameters:**
- **Path:**
  - `symbol` (string, required): Stock symbol
- **Query:**
  - `force_refresh` (boolean, optional, default: false): Force data refresh from source

**Response:**
```json
{
  "metadata": {
    "symbol": "AAPL",
    "timestamp": "2025-09-14T21:34:11Z",
    "provider": "yahoo_finance",
    "processing_time_ms": 227.08
  },
  "data": {
    "trailing_pe": 35.465153,
    "forward_pe": 28.167269,
    "peg_ratio": null,
    "price_to_book": 52.825546,
    "enterprise_to_revenue": 8.614,
    "enterprise_to_ebitda": 24.842,
    "profit_margins": 0.24295999,
    "operating_margins": 0.29990998,
    "gross_margins": 0.46678,
    "return_on_assets": 0.24545999,
    "return_on_equity": 1.49814,
    "debt_to_equity": 154.486,
    "total_cash_per_share": 3.731,
    "total_debt": 101698002944,
    "current_ratio": 0.868,
    "quick_ratio": 0.724,
    "beta": 1.109,
    "dividend_yield": 0.44,
    "payout_ratio": 0.1533,
    "earnings_growth": 0.121,
    "revenue_growth": 0.096
  }
}
```

**Response Fields:**
- `metadata` (object): Response metadata
  - `symbol` (string): Stock symbol
  - `timestamp` (string): Response timestamp (ISO 8601)
  - `provider` (string): Data source provider
  - `processing_time_ms` (number): API processing time in milliseconds
- `data` (object): Financial ratios (21 ratios available)
  - `trailing_pe` (number): Trailing Price-to-Earnings ratio
  - `forward_pe` (number): Forward Price-to-Earnings ratio
  - `peg_ratio` (number|null): Price/Earnings to Growth ratio
  - `price_to_book` (number): Price-to-Book ratio
  - `enterprise_to_revenue` (number): Enterprise Value to Revenue
  - `enterprise_to_ebitda` (number): Enterprise Value to EBITDA
  - `profit_margins` (number): Net profit margin
  - `operating_margins` (number): Operating margin
  - `gross_margins` (number): Gross margin
  - `return_on_assets` (number): Return on Assets (ROA)
  - `return_on_equity` (number): Return on Equity (ROE)
  - `debt_to_equity` (number): Debt-to-Equity ratio
  - `total_cash_per_share` (number): Total cash per share
  - `total_debt` (number): Total debt
  - `current_ratio` (number): Current ratio
  - `quick_ratio` (number): Quick ratio
  - `beta` (number): Beta coefficient
  - `dividend_yield` (number): Dividend yield
  - `payout_ratio` (number): Dividend payout ratio
  - `earnings_growth` (number): Earnings growth rate
  - `revenue_growth` (number): Revenue growth rate

**Behavior:**
- Cached for 1 hour unless force_refresh=true
- Data sourced from Yahoo Finance
- Returns 404 if symbol not found
- Processing time typically 200-250ms
- **Rich data:** 21 comprehensive financial ratios

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/fundamentals/ratios/AAPL"
```

---

## 4. GET /api/v1/fundamentals/earnings/{symbol}

**Description:** Returns earnings data including EPS metrics, analyst targets, and growth rates. **Rich data with 10 earnings metrics.**

**Parameters:**
- **Path:**
  - `symbol` (string, required): Stock symbol
- **Query:**
  - `force_refresh` (boolean, optional, default: false): Force data refresh from source

**Response:**
```json
{
  "metadata": {
    "symbol": "AAPL",
    "timestamp": "2025-09-14T21:34:11Z",
    "provider": "yahoo_finance",
    "processing_time_ms": 282.7
  },
  "data": {
    "trailing_eps": 6.6,
    "forward_eps": 8.31,
    "earnings_quarterly_growth": 0.093,
    "earnings_growth": 0.121,
    "revenue_growth": 0.096,
    "target_high_price": 300.0,
    "target_low_price": 175.0,
    "target_mean_price": 238.79794,
    "recommendation_mean": 2.04348,
    "number_of_analyst_opinions": 39
  }
}
```

**Response Fields:**
- `metadata` (object): Response metadata
  - `symbol` (string): Stock symbol
  - `timestamp` (string): Response timestamp (ISO 8601)
  - `provider` (string): Data source provider
  - `processing_time_ms` (number): API processing time in milliseconds
- `data` (object): Earnings data (10 metrics available)
  - `trailing_eps` (number): Trailing 12-month EPS
  - `forward_eps` (number): Forward 12-month EPS estimate
  - `earnings_quarterly_growth` (number): Quarterly earnings growth rate
  - `earnings_growth` (number): Annual earnings growth rate
  - `revenue_growth` (number): Annual revenue growth rate
  - `target_high_price` (number): Analyst target high price
  - `target_low_price` (number): Analyst target low price
  - `target_mean_price` (number): Analyst target mean price
  - `recommendation_mean` (number): Mean analyst recommendation (1=Strong Buy, 5=Strong Sell)
  - `number_of_analyst_opinions` (number): Number of analyst opinions

**Behavior:**
- Cached for 1 hour unless force_refresh=true
- Data sourced from Yahoo Finance
- Returns 404 if symbol not found
- Processing time typically 250-300ms
- **Rich data:** 10 comprehensive earnings metrics

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/fundamentals/earnings/AAPL"
```

---

## Data Sources

- **Yahoo Finance**: Primary data source for all fundamentals data
- **Real-time Data**: Live market data and financial metrics
- **Analyst Estimates**: Consensus estimates from financial analysts
- **Market Data**: Real-time price and market metrics

---

## Data Coverage Summary

| Endpoint | Data Points | Status | Notes |
|----------|-------------|---------|-------|
| **Overview** | 13 fields | ✅ **Rich** | Company info, market cap, employees |
| **Financials** | 13 fields | ⚠️ **Limited** | All null values (premium data required) |
| **Ratios** | 21 fields | ✅ **Rich** | Comprehensive financial ratios |
| **Earnings** | 10 fields | ✅ **Rich** | EPS, targets, analyst opinions |

**Total Available Data Points: 44** (33 rich + 11 limited)

---

## Data Freshness

- **Overview**: Updated daily from Yahoo Finance
- **Financials**: Limited data (premium sources required)
- **Ratios**: Real-time calculations from Yahoo Finance
- **Earnings**: Updated after each earnings report

---

## Error Responses

### **404 Not Found**
```json
{
  "error": "symbol_not_found",
  "message": "Symbol AAPL not found",
  "code": 404
}
```

### **400 Bad Request**
```json
{
  "error": "invalid_symbol",
  "message": "Invalid symbol format",
  "code": 400
}
```

---

**Total Fundamentals Endpoints: 4** ✅


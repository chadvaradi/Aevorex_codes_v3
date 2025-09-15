# EODHD Stock Endpoints Documentation

## Overview
This document describes the EODHD Stock API endpoints available in the FinanceHub backend. All endpoints require JWT authentication and provide access to comprehensive stock market data including historical prices, intraday data, corporate actions, and exchange information.

**Base URL**: `/api/v1/eodhd/stock`  
**Authentication**: JWT required for all endpoints  
**Data Provider**: EODHD (End of Day Historical Data)  
**Last Updated**: 2025-09-14  

---

## 1. GET /api/v1/eodhd/stock/eod
**Get End of Day (EOD) Stock Data**

Retrieves historical end-of-day stock price data for a given symbol.

### Parameters
- `symbol` (required): Ticker symbol (e.g., "AAPL", "MSFT")
- `from` (optional): Start date in YYYY-MM-DD format
- `to` (optional): End date in YYYY-MM-DD format

### Response Format
```json
[
  {
    "date": "2025-09-10",
    "open": 225.50,
    "high": 227.80,
    "low": 224.20,
    "close": 226.79,
    "adjusted_close": 226.79,
    "volume": 45000000
  }
]
```

### Usage
```bash
# Get recent EOD data
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/eod?symbol=AAPL&from=2025-09-10&to=2025-09-12"

# Get all available historical data
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/eod?symbol=AAPL"
```

**Status**: ✅ **Working** - Returns fresh stock data with proper date filtering

---

## 2. GET /api/v1/eodhd/stock/intraday
**Get Intraday Stock Data**

Retrieves intraday OHLCV data for a given symbol with configurable intervals.

### Parameters
- `symbol` (required): Ticker symbol (e.g., "AAPL", "MSFT")
- `interval` (optional): Time interval (default: "5m") - Options: 1m, 5m, 15m, 1h, 1d
- `from` (optional): Start datetime in YYYY-MM-DD HH:MM format
- `to` (optional): End datetime in YYYY-MM-DD HH:MM format

### Response Format
```json
[
  {
    "datetime": "2025-09-12 19:55:00",
    "open": 234.00,
    "high": 234.50,
    "low": 233.80,
    "close": 234.059997,
    "volume": 125000
  }
]
```

### Usage
```bash
# Get 5-minute intraday data
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/intraday?symbol=AAPL&interval=5m"

# Get 1-hour data for specific time range
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/intraday?symbol=AAPL&interval=1h&from=2025-09-12 09:00&to=2025-09-12 16:00"
```

**Status**: ✅ **Working** - Returns real-time intraday data with proper timestamps

---

## 3. GET /api/v1/eodhd/stock/splits
**Get Stock Splits Data**

Retrieves historical stock split information for a given symbol.

### Parameters
- `symbol` (required): Ticker symbol (e.g., "AAPL", "MSFT")

### Response Format
```json
[
  {
    "date": "2000-06-21",
    "split_ratio": "2:1",
    "from_factor": 1,
    "to_factor": 2
  }
]
```

### Usage
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/splits?symbol=AAPL"
```

**Status**: ✅ **Working** - Returns historical split data (note: some split_ratio values may be null for very old splits)

---

## 4. GET /api/v1/eodhd/stock/dividends
**Get Stock Dividends Data**

Retrieves historical dividend payments for a given symbol.

### Parameters
- `symbol` (required): Ticker symbol (e.g., "AAPL", "MSFT")

### Response Format
```json
[
  {
    "date": "2025-08-08",
    "value": 0.25,
    "currency": "USD"
  }
]
```

### Usage
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/dividends?symbol=AAPL"
```

**Status**: ✅ **Fixed** - Corrected endpoint path from `/api/dividends/` to `/api/div/` (namespace mismatch), returns historical dividend data

---

## 5. GET /api/v1/eodhd/stock/adjusted
**Get Adjusted Stock Data**

Retrieves end-of-day data with splits and dividends already applied (adjusted prices).

### Parameters
- `symbol` (required): Ticker symbol (e.g., "AAPL", "MSFT")
- `from` (optional): Start date in YYYY-MM-DD format
- `to` (optional): End date in YYYY-MM-DD format

### Response Format
```json
[
  {
    "date": "2025-09-10",
    "open": 225.50,
    "high": 227.80,
    "low": 224.20,
    "close": 226.79,
    "adjusted_close": 226.79,
    "volume": 45000000
  }
]
```

### Usage
```bash
# Get adjusted data for specific date range
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/adjusted?symbol=AAPL&from=2025-09-10&to=2025-09-12"

# Get all available adjusted data
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/adjusted?symbol=AAPL"
```

**Status**: ✅ **Fixed** - Added missing parameter forwarding for `from`/`to` dates, now returns requested date range instead of defaulting to 1980s data

---

## 6. GET /api/v1/eodhd/stock/exchange-tickers
**Get Exchange Tickers List**

Retrieves all tickers available on a specific exchange.

### Parameters
- `exchange` (required): Exchange code (e.g., "US", "NYSE", "NASDAQ", "LSE")
- `delisted` (optional): Include delisted tickers (set to "1")
- `type` (optional): Filter by asset type - Options: common_stock, preferred_stock, stock, etf, fund

### Response Format
```json
[
  {
    "Code": "AAPL",
    "Name": "Apple Inc.",
    "Country": "USA",
    "Exchange": "NASDAQ",
    "Currency": "USD",
    "Type": "Common Stock",
    "Isin": "US0378331005"
  }
]
```

### Usage
```bash
# Get all US exchange tickers
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/exchange-tickers?exchange=US"

# Get only common stocks from NYSE
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/exchange-tickers?exchange=NYSE&type=common_stock"

# Include delisted tickers
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  "https://api.aevorex.com/api/v1/eodhd/stock/exchange-tickers?exchange=US&delisted=1"
```

**Status**: ✅ **Fixed** - Added missing EODHD parameters (`delisted`, `type`) and proper field mapping (EODHD returns `Code`/`Name`, not `code`/`name`), returns 50,000+ tickers for US exchange

---

## 🔧 Technical Implementation

### **Bug Analysis & Fixes**

| Endpoint | Original Issue | Root Cause | Fix Applied | Result |
|----------|----------------|------------|-------------|---------|
| **Dividends** | 404 Not Found | Wrong endpoint path (`/api/dividends/` vs `/api/div/`) | Corrected path mapping | ✅ Returns historical dividend data |
| **Adjusted** | 1980s data instead of requested dates | Missing parameter forwarding (`from`/`to`) | Added parameter forwarding logic | ✅ Returns requested date range |
| **Exchange-tickers** | Null values in response | Missing EODHD parameters + field case mismatch | Added `delisted`/`type` params + proper field handling | ✅ Returns 50K+ tickers with correct field names |
| **Delisted** | 404 Not Found | Non-existent EODHD API endpoint | Removed endpoint entirely | ✅ Clean API surface (no 404s) |

### **Endpoint Mapping**
All endpoints are properly mapped to EODHD API endpoints:

| Our Endpoint | EODHD API | Status |
|--------------|-----------|---------|
| `/eod` | `/api/eod/{symbol}` | ✅ Working |
| `/intraday` | `/api/intraday/{symbol}` | ✅ Working |
| `/splits` | `/api/splits/{symbol}` | ✅ Working |
| `/dividends` | `/api/div/{symbol}` | ✅ Fixed (path correction) |
| `/adjusted` | `/api/eod/{symbol}?adjusted=1` | ✅ Fixed (parameter forwarding) |
| `/exchange-tickers` | `/api/exchange-symbol-list/{exchange}` | ✅ Fixed (parameter + field mapping) |

### **Parameter Forwarding**
All query parameters are properly forwarded to EODHD API:
- Date ranges (`from`, `to`)
- Interval settings (`interval`)
- Filter options (`delisted`, `type`)
- API token and format parameters

### **Error Handling**
- Proper HTTP status codes
- Detailed error messages
- EODHD API error forwarding
- Graceful fallbacks for missing data

---

## 📊 Validation Results

### **Test Date**: 2025-09-14
### **Test Symbol**: AAPL (Apple Inc.)

| Endpoint | Status | Data Quality | Notes |
|----------|--------|--------------|-------|
| EOD | ✅ | Fresh (2025-09-10/11) | Proper date filtering |
| Intraday | ✅ | Real-time (5m intervals) | Current timestamps |
| Splits | ✅ | Historical (1987-2000) | Some null ratios for old splits |
| Dividends | ✅ | Historical (1987+) | Fixed endpoint path |
| Adjusted | ✅ | Fresh (2025-09-10/11) | Fixed date parameter forwarding |
| Exchange-tickers | ✅ | 50,409 US tickers | All major exchanges included |

**Overall Status**: All endpoints operational with proper data quality

---

## 🚫 Removed Endpoints

### **GET /api/v1/eodhd/stock/delisted**
**Status**: ❌ **Removed** - Not supported by EODHD API

**Removal Reason**: Clean API surface approach
- EODHD does not provide a dedicated delisted stocks API endpoint
- Rather than returning 404 errors, endpoint was completely removed
- **Alternative**: Use `/exchange-tickers?delisted=1` to get delisted tickers from specific exchanges
- **Result**: Cleaner API surface without error endpoints

---

## Exchange Codes Reference

### **Major US Exchanges**
- `US` - All US exchanges (NYSE, NASDAQ, etc.) - **Recommended**
- `NYSE` - New York Stock Exchange
- `NASDAQ` - NASDAQ Stock Market
- `BATS` - BATS Global Markets

### **International Exchanges**
- `LSE` - London Stock Exchange
- `XETRA` - Deutsche Börse XETRA
- `TSE` - Tokyo Stock Exchange
- `HKEX` - Hong Kong Exchanges

### **Asset Classes**
- `CC` - Cryptocurrencies
- `FOREX` - Foreign Exchange
- `GBOND` - Government Bonds

---

## Rate Limits & Caching

- **Rate Limits**: Follows EODHD API limits based on subscription plan
- **Caching**: 1 hour for EOD data, 5 minutes for intraday data
- **Authentication**: JWT token required for all requests
- **Data Freshness**: Real-time for intraday, end-of-day for EOD data

---

## Support & Troubleshooting

### **Common Issues**
1. **404 Errors**: Check symbol format and exchange code
2. **Empty Data**: Verify date ranges and symbol validity
3. **Authentication Errors**: Ensure valid JWT token

### **Data Quality Notes**
- Some historical data may have null values for very old records
- Split ratios may be null for splits before 2000
- Dividend data available from 1987 for major stocks
- Exchange ticker lists include both active and delisted securities

---

*Last Updated: 2025-09-14*  
*API Version: v1*  
*Data Provider: EODHD*
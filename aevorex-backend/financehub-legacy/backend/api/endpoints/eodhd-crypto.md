# EODHD - Crypto Endpoints

**Category:** EODHD - Crypto  
**Total Endpoints:** 8  
**Authentication:** JWT required  
**Caching:** 1 hour (list), 5 minutes (quotes), 1 hour (historical)

This category provides cryptocurrency data including quotes, historical prices, and market information. All endpoints use the `.CC` exchange suffix for proper EODHD API integration.

---

## 1. GET /api/v1/eodhd/crypto/list

**Description:** Returns list of available cryptocurrencies with basic information.

**Parameters:** None

**Response:**
```json
{
  "cryptocurrencies": [
    {
      "symbol": "BTC-USD",
      "name": "Bitcoin",
      "currency": "USD",
      "exchange": "Coinbase",
      "type": "cryptocurrency",
      "market_cap": 800000000000,
      "price": 42000.50,
      "change_24h": 1250.75,
      "change_24h_percent": 3.07,
      "volume_24h": 25000000000,
      "rank": 1
    },
    {
      "symbol": "ETH-USD",
      "name": "Ethereum",
      "currency": "USD",
      "exchange": "Coinbase",
      "type": "cryptocurrency",
      "market_cap": 300000000000,
      "price": 2500.25,
      "change_24h": 75.50,
      "change_24h_percent": 3.11,
      "volume_24h": 15000000000,
      "rank": 2
    }
  ],
  "metadata": {
    "total_count": 2,
    "last_updated": "2024-01-15T10:30:00Z",
    "source": "EODHD"
  }
}
```

**Response Fields:**
- `cryptocurrencies` (array): Array of cryptocurrency data
  - `symbol` (string): Cryptocurrency symbol
  - `name` (string): Cryptocurrency name
  - `currency` (string): Quote currency
  - `exchange` (string): Exchange name
  - `type` (string): Instrument type
  - `market_cap` (number): Market capitalization
  - `price` (number): Current price
  - `change_24h` (number): 24-hour price change
  - `change_24h_percent` (number): 24-hour percentage change
  - `volume_24h` (number): 24-hour trading volume
  - `rank` (number): Market cap ranking
- `metadata` (object): Response metadata
  - `total_count` (number): Total number of cryptocurrencies
  - `last_updated` (string): Last update timestamp
  - `source` (string): Data source

**Behavior:**
- Cached for 1 hour
- Includes major cryptocurrencies
- Real-time price updates
- Market cap rankings

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" https://api.aevorex.com/api/v1/eodhd/crypto/list
```

---

## 2. GET /api/v1/eodhd/crypto/{symbol}/quote

**Description:** Returns real-time quote data for a specific cryptocurrency.

**Parameters:**
- **Path:**
  - `symbol` (string, required): Cryptocurrency symbol (e.g., BTC-USD, ETH-USD)

**Response:**
```json
{
  "symbol": "BTC-USD",
  "name": "Bitcoin",
  "price": 42000.50,
  "change": 1250.75,
  "change_percent": 3.07,
  "volume": 25000000000,
  "market_cap": 800000000000,
  "high_24h": 42500.00,
  "low_24h": 40800.00,
  "open_24h": 40749.75,
  "bid": 41995.50,
  "ask": 42005.50,
  "spread": 10.00,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

**Response Fields:**
- `symbol` (string): Cryptocurrency symbol
- `name` (string): Cryptocurrency name
- `price` (number): Current price
- `change` (number): Price change from 24h ago
- `change_percent` (number): Percentage change from 24h ago
- `volume` (number): 24-hour trading volume
- `market_cap` (number): Market capitalization
- `high_24h` (number): 24-hour high price
- `low_24h` (number): 24-hour low price
- `open_24h` (number): 24-hour opening price
- `bid` (number): Current bid price
- `ask` (number): Current ask price
- `spread` (number): Bid-ask spread
- `timestamp` (string): Data timestamp

**Behavior:**
- Cached for 5 minutes
- Real-time price updates
- Returns 404 if symbol not found

**Usage:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/quote
```

---

## 3. GET /api/v1/eodhd/crypto/{symbol}/eod

**Description:** Returns end-of-day cryptocurrency data for a specific date range.

**Parameters:**
- **Path:**
  - `symbol` (string, required): Cryptocurrency symbol
- **Query:**
  - `from_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `to_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)

**Response:**
```json
{
  "symbol": "BTC-USD",
  "data": [
    {
      "date": "2024-01-15",
      "open": 40749.75,
      "high": 42500.00,
      "low": 40800.00,
      "close": 42000.50,
      "volume": 25000000000,
      "adjusted_close": 42000.50
    },
    {
      "date": "2024-01-14",
      "open": 40200.00,
      "high": 41000.00,
      "low": 39800.00,
      "close": 40749.75,
      "volume": 22000000000,
      "adjusted_close": 40749.75
    }
  ],
  "metadata": {
    "symbol": "BTC-USD",
    "total_records": 2,
    "from_date": "2024-01-14",
    "to_date": "2024-01-15",
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `symbol` (string): Cryptocurrency symbol
- `data` (array): Array of daily data
  - `date` (string): Date in YYYY-MM-DD format
  - `open` (number): Opening price
  - `high` (number): High price
  - `low` (number): Low price
  - `close` (number): Closing price
  - `volume` (number): Trading volume
  - `adjusted_close` (number): Adjusted closing price
- `metadata` (object): Response metadata
  - `symbol` (string): Cryptocurrency symbol
  - `total_records` (number): Total number of records
  - `from_date` (string): Start date
  - `to_date` (string): End date
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 1 hour
- **Defaults to last 30 days** if no date range specified (prevents showing 2010 historical data)
- Returns 404 if symbol not found
- Includes helpful metadata when using default date range

**Usage:**
```bash
# Default (last 30 days)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" "https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/eod"

# Custom date range
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" "https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/eod?from=2024-01-01&to=2024-01-31"
```

---

## 4. GET /api/v1/eodhd/crypto/{symbol}/intraday

**Description:** Returns intraday cryptocurrency data with specified interval.

**Parameters:**
- **Path:**
  - `symbol` (string, required): Cryptocurrency symbol
- **Query:**
  - `interval` (string, optional, default: "5m"): Data interval (1m, 5m, 15m, 30m, 1h, 4h, 1d)

**Response:**
```json
{
  "symbol": "BTC-USD",
  "interval": "5m",
  "data": [
    {
      "timestamp": "2024-01-15T10:30:00Z",
      "open": 42000.50,
      "high": 42050.00,
      "low": 41950.00,
      "close": 42025.75,
      "volume": 1250000
    },
    {
      "timestamp": "2024-01-15T10:25:00Z",
      "open": 41950.00,
      "high": 42000.50,
      "low": 41900.00,
      "close": 42000.50,
      "volume": 1100000
    }
  ],
  "metadata": {
    "symbol": "BTC-USD",
    "interval": "5m",
    "total_records": 2,
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `symbol` (string): Cryptocurrency symbol
- `interval` (string): Data interval
- `data` (array): Array of intraday data
  - `timestamp` (string): Data timestamp
  - `open` (number): Opening price
  - `high` (number): High price
  - `low` (number): Low price
  - `close` (number): Closing price
  - `volume` (number): Trading volume
- `metadata` (object): Response metadata
  - `symbol` (string): Cryptocurrency symbol
  - `interval` (string): Data interval
  - `total_records` (number): Total number of records
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 5 minutes
- Real-time data during market hours
- Returns 404 if symbol not found

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/intraday?interval=1h"
```

---

## 5. GET /api/v1/eodhd/crypto/{symbol}/history

**Description:** Returns historical cryptocurrency data for a specified date range.

**Parameters:**
- **Path:**
  - `symbol` (string, required): Cryptocurrency symbol
- **Query:**
  - `from_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `to_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)

**Response:**
```json
{
  "symbol": "BTC-USD",
  "data": [
    {
      "date": "2024-01-15",
      "open": 40749.75,
      "high": 42500.00,
      "low": 40800.00,
      "close": 42000.50,
      "volume": 25000000000,
      "adjusted_close": 42000.50
    },
    {
      "date": "2024-01-14",
      "open": 40200.00,
      "high": 41000.00,
      "low": 39800.00,
      "close": 40749.75,
      "volume": 22000000000,
      "adjusted_close": 40749.75
    }
  ],
  "metadata": {
    "symbol": "BTC-USD",
    "total_records": 2,
    "from_date": "2024-01-14",
    "to_date": "2024-01-15",
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `symbol` (string): Cryptocurrency symbol
- `data` (array): Array of historical data
  - `date` (string): Date in YYYY-MM-DD format
  - `open` (number): Opening price
  - `high` (number): High price
  - `low` (number): Low price
  - `close` (number): Closing price
  - `volume` (number): Trading volume
  - `adjusted_close` (number): Adjusted closing price
- `metadata` (object): Response metadata
  - `symbol` (string): Cryptocurrency symbol
  - `total_records` (number): Total number of records
  - `from_date` (string): Start date
  - `to_date` (string): End date
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 1 hour
- Defaults to last 30 days if no date range specified
- Returns 404 if symbol not found

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/history?from_date=2024-01-01&to_date=2024-01-31"
```

---

## 6. GET /api/v1/eodhd/crypto/{symbol}/splits

**Description:** Returns cryptocurrency splits data (not supported for cryptocurrencies).

**Parameters:**
- **Path:**
  - `symbol` (string, required): Cryptocurrency symbol

**Response:**
```json
{
  "error": "not_supported",
  "message": "Splits are not supported for cryptocurrencies",
  "code": 400
}
```

**Behavior:**
- Returns 400 Bad Request
- Cryptocurrencies do not have stock splits
- This endpoint is maintained for API consistency

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/splits
```

---

## 7. GET /api/v1/eodhd/crypto/{symbol}/dividends

**Description:** Returns cryptocurrency dividends data (not supported for cryptocurrencies).

**Parameters:**
- **Path:**
  - `symbol` (string, required): Cryptocurrency symbol

**Response:**
```json
{
  "error": "not_supported",
  "message": "Dividends are not supported for cryptocurrencies",
  "code": 400
}
```

**Behavior:**
- Returns 400 Bad Request
- Cryptocurrencies do not pay dividends
- This endpoint is maintained for API consistency

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/dividends
```

---

## 8. GET /api/v1/eodhd/crypto/{symbol}/adjusted

**Description:** Returns adjusted cryptocurrency data for a specified date range.

**Parameters:**
- **Path:**
  - `symbol` (string, required): Cryptocurrency symbol
- **Query:**
  - `from_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `to_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)

**Response:**
```json
{
  "symbol": "BTC-USD",
  "data": [
    {
      "date": "2024-01-15",
      "open": 40749.75,
      "high": 42500.00,
      "low": 40800.00,
      "close": 42000.50,
      "volume": 25000000000,
      "adjusted_close": 42000.50
    },
    {
      "date": "2024-01-14",
      "open": 40200.00,
      "high": 41000.00,
      "low": 39800.00,
      "close": 40749.75,
      "volume": 22000000000,
      "adjusted_close": 40749.75
    }
  ],
  "metadata": {
    "symbol": "BTC-USD",
    "total_records": 2,
    "from_date": "2024-01-14",
    "to_date": "2024-01-15",
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `symbol` (string): Cryptocurrency symbol
- `data` (array): Array of adjusted data
  - `date` (string): Date in YYYY-MM-DD format
  - `open` (number): Opening price
  - `high` (number): High price
  - `low` (number): Low price
  - `close` (number): Closing price
  - `volume` (number): Trading volume
  - `adjusted_close` (number): Adjusted closing price
- `metadata` (object): Response metadata
  - `symbol` (string): Cryptocurrency symbol
  - `total_records` (number): Total number of records
  - `from_date` (string): Start date
  - `to_date` (string): End date
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 1 hour
- Defaults to last 30 days if no date range specified
- Returns 404 if symbol not found

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/crypto/BTC-USD/adjusted?from_date=2024-01-01&to_date=2024-01-31"
```

---

## 🔧 Technical Implementation

### **Ticker Mapping**
All crypto endpoints automatically append the `.CC` exchange suffix to cryptocurrency symbols for proper EODHD API integration:

- **Input**: `BTC-USD` 
- **EODHD API Call**: `BTC-USD.CC`
- **Supported Symbols**: BTC-USD, ETH-USD, XRP-USD, LTC-USD, and all major cryptocurrencies

### **Validation Results**
Comprehensive testing confirmed all endpoints work correctly with major cryptocurrencies:

| Symbol | Quote | EOD | Intraday | History | Status |
|--------|-------|-----|----------|---------|--------|
| BTC-USD | ✅ | ✅ | ✅ | ✅ | **Working** |
| ETH-USD | ✅ | ✅ | ✅ | ✅ | **Working** |
| XRP-USD | ✅ | ✅ | ✅ | ✅ | **Working** |
| LTC-USD | ✅ | ✅ | ✅ | ✅ | **Working** |

**Test Date**: 2025-09-14  
**Data Quality**: Real-time, fresh data with proper timestamps  
**Feed Status**: All major crypto feeds operational  

### **Default Date Range Behavior**
To improve user experience, crypto endpoints now use intelligent default date ranges:

- **EOD/History/Adjusted endpoints**: Default to **last 30 days** when no date parameters provided
- **Prevents confusion**: No more 2010 historical data showing by default
- **Helpful metadata**: Response includes note about default behavior and actual date range used
- **Custom ranges**: Users can still specify `?from=YYYY-MM-DD&to=YYYY-MM-DD` for any date range

**Example Response with Default Dates:**
```json
{
  "data": [...],
  "metadata": {
    "symbol": "BTC-USD",
    "note": "Showing last 30 days by default. Use ?from=YYYY-MM-DD&to=YYYY-MM-DD for custom range.",
    "date_range": "2025-08-15 to 2025-09-14"
  }
}
```

---

## Cryptocurrency Features

### **Supported Cryptocurrencies**
- **Major Coins**: Bitcoin, Ethereum, Litecoin, etc.
- **Altcoins**: Various alternative cryptocurrencies
- **Stablecoins**: USDT, USDC, DAI, etc.
- **DeFi Tokens**: Uniswap, Aave, Compound, etc.

### **Data Quality**
- **Real-time**: Live price updates
- **Historical**: Up to 10 years of data
- **Multiple Exchanges**: Aggregated data from major exchanges
- **Volume Data**: Trading volume information

### **Market Coverage**
- **24/7 Trading**: Cryptocurrency markets never close
- **Global Exchanges**: Data from major global exchanges
- **Price Discovery**: Best available prices across exchanges

---

## Performance Considerations

### **Caching Strategy**
- List: 1 hour cache
- Quotes: 5 minutes cache
- Historical: 1 hour cache
- Real-time data during active trading

### **Rate Limiting**
- Standard rate limits apply
- Recommended: 1 request per second
- Burst: up to 10 requests per second

### **Response Time**
- List: 100-200ms
- Quotes: 50-100ms
- Historical: 200-500ms
- Cached responses: < 50ms

---

## Error Responses

### **404 Not Found**
```json
{
  "error": "symbol_not_found",
  "message": "Cryptocurrency symbol BTC-USD not found",
  "code": 404
}
```

### **400 Bad Request**
```json
{
  "error": "invalid_parameters",
  "message": "Invalid date range or interval",
  "code": 400
}
```

---

**Total EODHD Crypto Endpoints: 8** ✅

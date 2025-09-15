# EODHD - Technical Endpoints

**Category:** EODHD - Technical  
**Total Endpoints:** 2  
**Authentication:** Not required  
**Caching:** 1 hour

This category provides technical analysis indicators and stock screening functionality.

---

## 1. GET /api/v1/eodhd/technical/indicators

**Description:** Returns technical indicators data for a specific symbol.

**Parameters:**
- **Query:**
  - `symbol` (string, required): Stock symbol (e.g., AAPL, MSFT, GOOGL)
  - `indicator` (string, required): Technical indicator name (RSI, MACD, SMA, EMA, etc.)
  - `from_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `to_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)
  - `interval` (string, optional, default: "1d"): Data interval (1d, 1w, 1m)

**Response:**
```json
{
  "symbol": "AAPL",
  "indicator": "RSI",
  "interval": "1d",
  "data": [
    {
      "date": "2024-01-15",
      "value": 65.45,
      "signal": "neutral"
    },
    {
      "date": "2024-01-14",
      "value": 62.30,
      "signal": "neutral"
    },
    {
      "date": "2024-01-13",
      "value": 58.75,
      "signal": "neutral"
    }
  ],
  "metadata": {
    "symbol": "AAPL",
    "indicator": "RSI",
    "interval": "1d",
    "total_records": 3,
    "from_date": "2024-01-13",
    "to_date": "2024-01-15",
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `symbol` (string): Stock symbol
- `indicator` (string): Technical indicator name
- `interval` (string): Data interval
- `data` (array): Array of indicator data
  - `date` (string): Date in YYYY-MM-DD format
  - `value` (number): Indicator value
  - `signal` (string): Trading signal (bullish, bearish, neutral)
- `metadata` (object): Response metadata
  - `symbol` (string): Stock symbol
  - `indicator` (string): Technical indicator name
  - `interval` (string): Data interval
  - `total_records` (number): Total number of records
  - `from_date` (string): Start date
  - `to_date` (string): End date
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 1 hour
- Defaults to last 30 days if no date range specified
- Returns 404 if symbol not found
- Returns 400 if indicator not supported

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/technical/indicators?symbol=AAPL&indicator=RSI&from_date=2024-01-01&to_date=2024-01-31"
```

**Supported Indicators:**
- **RSI**: Relative Strength Index
- **MACD**: Moving Average Convergence Divergence
- **SMA**: Simple Moving Average
- **EMA**: Exponential Moving Average
- **Bollinger Bands**: Upper, Middle, Lower bands
- **Stochastic**: %K and %D values
- **Williams %R**: Williams Percent Range
- **CCI**: Commodity Channel Index
- **ADX**: Average Directional Index
- **ATR**: Average True Range

---

## 2. GET /api/v1/eodhd/technical/screener

**Description:** Returns technical screening results for a specific symbol.

**Parameters:**
- **Query:**
  - `symbol` (string, required): Stock symbol
  - `from_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `to_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)
  - `interval` (string, optional, default: "1d"): Data interval (1d, 1w, 1m)

**Response:**
```json
{
  "symbol": "AAPL",
  "interval": "1d",
  "screening_results": {
    "overall_score": 75,
    "trend": "bullish",
    "momentum": "strong",
    "volatility": "moderate",
    "volume": "high",
    "indicators": {
      "RSI": {
        "value": 65.45,
        "signal": "neutral",
        "score": 50
      },
      "MACD": {
        "value": 0.85,
        "signal": "bullish",
        "score": 75
      },
      "SMA_50": {
        "value": 190.25,
        "signal": "bullish",
        "score": 80
      },
      "Bollinger_Bands": {
        "upper": 195.50,
        "middle": 190.25,
        "lower": 185.00,
        "signal": "neutral",
        "score": 60
      }
    },
    "signals": [
      {
        "type": "buy",
        "strength": "strong",
        "description": "Price above 50-day SMA with strong momentum"
      },
      {
        "type": "hold",
        "strength": "weak",
        "description": "RSI in neutral zone"
      }
    ]
  },
  "metadata": {
    "symbol": "AAPL",
    "interval": "1d",
    "from_date": "2024-01-01",
    "to_date": "2024-01-15",
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `symbol` (string): Stock symbol
- `interval` (string): Data interval
- `screening_results` (object): Screening results
  - `overall_score` (number): Overall technical score (0-100)
  - `trend` (string): Trend direction (bullish, bearish, neutral)
  - `momentum` (string): Momentum strength (strong, moderate, weak)
  - `volatility` (string): Volatility level (high, moderate, low)
  - `volume` (string): Volume level (high, moderate, low)
  - `indicators` (object): Individual indicator results
  - `signals` (array): Trading signals
- `metadata` (object): Response metadata
  - `symbol` (string): Stock symbol
  - `interval` (string): Data interval
  - `from_date` (string): Start date
  - `to_date` (string): End date
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 1 hour
- Defaults to last 30 days if no date range specified
- Returns 404 if symbol not found
- Comprehensive technical analysis

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/technical/screener?symbol=AAPL&from_date=2024-01-01&to_date=2024-01-31"
```

---

## Technical Analysis Features

### **Supported Indicators**
- **Trend Indicators**: SMA, EMA, MACD, ADX
- **Momentum Indicators**: RSI, Stochastic, Williams %R
- **Volatility Indicators**: Bollinger Bands, ATR
- **Volume Indicators**: Volume, OBV, A/D Line
- **Oscillators**: CCI, ROC, Momentum

### **Screening Criteria**
- **Trend Analysis**: Price direction and strength
- **Momentum Analysis**: Rate of price change
- **Volatility Analysis**: Price volatility levels
- **Volume Analysis**: Trading volume patterns
- **Support/Resistance**: Key price levels

### **Signal Generation**
- **Buy Signals**: Strong bullish indicators
- **Sell Signals**: Strong bearish indicators
- **Hold Signals**: Neutral or mixed signals
- **Strength Rating**: Signal strength (weak, moderate, strong)

---

## Performance Considerations

### **Caching Strategy**
- 1 hour cache for all technical data
- Real-time calculations during market hours
- Historical data cached longer

### **Rate Limiting**
- Standard rate limits apply
- Recommended: 1 request per second
- Burst: up to 10 requests per second

### **Response Time**
- Indicators: 200-500ms
- Screener: 500ms-1s
- Cached responses: < 100ms

---

## Error Responses

### **404 Not Found**
```json
{
  "error": "symbol_not_found",
  "message": "Stock symbol AAPL not found",
  "code": 404
}
```

### **400 Bad Request**
```json
{
  "error": "invalid_indicator",
  "message": "Indicator XYZ not supported",
  "code": 400
}
```

---

**Total EODHD Technical Endpoints: 2** ✅


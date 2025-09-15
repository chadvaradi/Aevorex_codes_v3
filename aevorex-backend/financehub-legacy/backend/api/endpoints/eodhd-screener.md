# EODHD - Screener Endpoints

**Category:** EODHD - Screener  
**Total Endpoints:** 1  
**Authentication:** Not required  
**Caching:** 1 hour  
**Status:** ✅ **100% Working** - Tested and verified

This category provides stock screening functionality for filtering and analyzing stocks based on various criteria. The screener endpoint has been tested and confirmed working with real EODHD data.

---

## 1. GET /api/v1/eodhd/screener/

**Description:** Runs EODHD stock screener with specified criteria and returns filtered results.

**Parameters:**
- **Query:**
  - `code` (string, required): Screener code or criteria identifier
  - `limit` (integer, optional, default: 50): Maximum number of results to return

**Response:**
```json
{
  "screener_results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "exchange": "NASDAQ",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "market_cap": 3000000000000,
      "price": 193.58,
      "change": 2.45,
      "change_percent": 1.28,
      "volume": 45678900,
      "pe_ratio": 28.5,
      "pb_ratio": 45.2,
      "ps_ratio": 7.8,
      "dividend_yield": 0.44,
      "beta": 1.29,
      "52_week_high": 199.62,
      "52_week_low": 124.17,
      "rsi": 65.45,
      "macd": 0.85,
      "sma_50": 190.25,
      "sma_200": 185.50,
      "score": 85,
      "rank": 1
    },
    {
      "symbol": "MSFT",
      "name": "Microsoft Corporation",
      "exchange": "NASDAQ",
      "sector": "Technology",
      "industry": "Software",
      "market_cap": 2810000000000,
      "price": 378.85,
      "change": -1.25,
      "change_percent": -0.33,
      "volume": 23456700,
      "pe_ratio": 32.1,
      "pb_ratio": 12.8,
      "ps_ratio": 9.2,
      "dividend_yield": 0.68,
      "beta": 0.95,
      "52_week_high": 384.30,
      "52_week_low": 309.45,
      "rsi": 58.30,
      "macd": 0.45,
      "sma_50": 375.20,
      "sma_200": 365.80,
      "score": 78,
      "rank": 2
    }
  ],
  "metadata": {
    "screener_code": "tech_stocks",
    "total_results": 2,
    "limit": 50,
    "criteria": {
      "sector": "Technology",
      "market_cap_min": 1000000000000,
      "pe_ratio_max": 35,
      "rsi_min": 30,
      "rsi_max": 70
    },
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `screener_results` (array): Array of screened stocks
  - `symbol` (string): Stock symbol
  - `name` (string): Company name
  - `exchange` (string): Stock exchange
  - `sector` (string): Business sector
  - `industry` (string): Specific industry
  - `market_cap` (number): Market capitalization
  - `price` (number): Current stock price
  - `change` (number): Price change
  - `change_percent` (number): Percentage change
  - `volume` (number): Trading volume
  - `pe_ratio` (number): Price-to-earnings ratio
  - `pb_ratio` (number): Price-to-book ratio
  - `ps_ratio` (number): Price-to-sales ratio
  - `dividend_yield` (number): Dividend yield
  - `beta` (number): Beta coefficient
  - `52_week_high` (number): 52-week high price
  - `52_week_low` (number): 52-week low price
  - `rsi` (number): Relative Strength Index
  - `macd` (number): MACD value
  - `sma_50` (number): 50-day Simple Moving Average
  - `sma_200` (number): 200-day Simple Moving Average
  - `score` (number): Overall screening score
  - `rank` (number): Ranking within results
- `metadata` (object): Response metadata
  - `screener_code` (string): Screener code used
  - `total_results` (number): Total number of results
  - `limit` (number): Maximum results requested
  - `criteria` (object): Screening criteria applied
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 1 hour
- Returns 400 if screener code not found
- Results sorted by score/rank

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/screener/?code=tech_stocks&limit=20"
```

**Common Screener Codes:**
- `tech_stocks`: Technology sector stocks
- `dividend_stocks`: High dividend yield stocks
- `growth_stocks`: High growth potential stocks
- `value_stocks`: Undervalued stocks
- `momentum_stocks`: High momentum stocks
- `small_cap`: Small capitalization stocks
- `large_cap`: Large capitalization stocks
- `penny_stocks`: Low-priced stocks
- `blue_chip`: Blue chip stocks
- `reit_stocks`: Real Estate Investment Trusts

---

## Screener Features

### **Screening Criteria**
- **Fundamental**: P/E ratio, P/B ratio, P/S ratio, dividend yield
- **Technical**: RSI, MACD, moving averages, price patterns
- **Market**: Market cap, sector, industry, exchange
- **Performance**: Price change, volume, volatility
- **Quality**: Beta, debt-to-equity, return on equity

### **Predefined Screeners**
- **Sector-based**: Technology, healthcare, financials, etc.
- **Style-based**: Growth, value, momentum, quality
- **Size-based**: Large cap, mid cap, small cap, micro cap
- **Risk-based**: Low beta, high beta, defensive, cyclical

### **Custom Screening**
- **Multiple Criteria**: Combine various screening parameters
- **Range Filters**: Set minimum/maximum values for metrics
- **Relative Rankings**: Compare stocks within sectors or markets
- **Dynamic Updates**: Real-time screening results

---

## Performance Considerations

### **Caching Strategy**
- 1 hour cache for optimal performance
- Real-time data for current metrics
- Historical screening results cached longer

### **Rate Limiting**
- Standard rate limits apply
- Recommended: 1 request per 30 seconds
- Burst: up to 5 requests per minute

### **Response Time**
- Simple screeners: 200-500ms
- Complex screeners: 500ms-1s
- Cached responses: < 100ms

---

## Error Responses

### **400 Bad Request**
```json
{
  "error": "invalid_screener_code",
  "message": "Screener code 'invalid_code' not found",
  "code": 400
}
```

### **400 Bad Request**
```json
{
  "error": "invalid_parameters",
  "message": "Limit must be between 1 and 1000",
  "code": 400
}
```

---

## Integration Examples

### **JavaScript/AJAX**
```javascript
// Run stock screener
async function runStockScreener(screenerCode, limit = 50) {
  try {
    const response = await fetch(`/api/v1/eodhd/screener/?code=${screenerCode}&limit=${limit}`);
    const data = await response.json();
    
    if (data.screener_results) {
      data.screener_results.forEach(stock => {
        console.log(`${stock.symbol}: ${stock.name} - Score: ${stock.score}`);
      });
    }
  } catch (error) {
    console.error('Screener failed:', error);
  }
}

// Usage
runStockScreener('tech_stocks', 20);
```

### **Python**
```python
import requests

def run_stock_screener(screener_code, limit=50):
    try:
        response = requests.get(
            'https://api.aevorex.com/api/v1/eodhd/screener/',
            params={
                'code': screener_code,
                'limit': limit
            }
        )
        data = response.json()
        
        if 'screener_results' in data:
            for stock in data['screener_results']:
                print(f"{stock['symbol']}: {stock['name']} - Score: {stock['score']}")
                
    except requests.RequestException as e:
        print(f"Screener failed: {e}")

# Usage
run_stock_screener('tech_stocks', limit=20)
```

---

## Best Practices

### **Screener Selection**
- Choose appropriate screener codes for your analysis
- Set reasonable limits to avoid large responses
- Consider multiple screeners for comprehensive analysis

### **Result Analysis**
- Review screening scores and rankings
- Analyze individual metrics and ratios
- Consider market conditions and trends

### **Performance Optimization**
- Use cached results when possible
- Avoid excessive screening requests
- Monitor rate limits and usage

---

**Total EODHD Screener Endpoints: 1** ✅


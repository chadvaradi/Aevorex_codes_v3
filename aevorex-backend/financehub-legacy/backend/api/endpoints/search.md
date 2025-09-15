# Search Endpoints

**Category:** Search  
**Total Endpoints:** 1  
**Authentication:** Not required  
**Caching:** 1 hour  
**Subscription:** Pro/Enterprise tier required

This category provides ticker search functionality for finding financial instruments and companies.

---

## 1. GET /api/v1/search/

**Description:** Search for tickers, companies, and financial instruments by name, symbol, or other criteria.

**Parameters:**
- **Query:**
  - `query` (string, required): Search term (company name, ticker symbol, or keywords)
  - `limit` (integer, optional, default: 20): Maximum number of results to return
  - `type` (string, optional): Filter by instrument type (stock, crypto, forex, etc.)
  - `exchange` (string, optional): Filter by exchange (NASDAQ, NYSE, etc.)

**Response:**
```json
{
  "results": [
    {
      "symbol": "AAPL",
      "name": "Apple Inc.",
      "type": "stock",
      "exchange": "NASDAQ",
      "country": "United States",
      "currency": "USD",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "market_cap": 3000000000000,
      "price": 193.58,
      "change_percent": 1.28,
      "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
    },
    {
      "symbol": "AAPL.L",
      "name": "Apple Inc.",
      "type": "stock",
      "exchange": "LSE",
      "country": "United Kingdom",
      "currency": "GBP",
      "sector": "Technology",
      "industry": "Consumer Electronics",
      "market_cap": 3000000000000,
      "price": 152.45,
      "change_percent": 1.28,
      "description": "Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide."
    }
  ],
  "metadata": {
    "query": "Apple",
    "total_results": 2,
    "limit": 20,
    "page": 1,
    "search_time_ms": 45
  }
}
```

**Response Fields:**
- `results` (array): Array of search results
  - `symbol` (string): Ticker symbol
  - `name` (string): Company name
  - `type` (string): Instrument type (stock, crypto, forex, etc.)
  - `exchange` (string): Stock exchange
  - `country` (string): Country of incorporation
  - `currency` (string): Currency code
  - `sector` (string): Business sector
  - `industry` (string): Specific industry
  - `market_cap` (number): Market capitalization
  - `price` (number): Current price
  - `change_percent` (number): Percentage change
  - `description` (string): Company description
- `metadata` (object): Search metadata
  - `query` (string): Original search query
  - `total_results` (number): Total number of results found
  - `limit` (number): Maximum results per page
  - `page` (number): Current page number
  - `search_time_ms` (number): Search execution time in milliseconds

**Behavior:**
- Cached for 1 hour
- Pro/Enterprise subscription required
- Case-insensitive search
- Supports partial matches
- Returns results from multiple exchanges and markets

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/search/?query=Apple&limit=10"
```

**Advanced Search Examples:**
```bash
# Search by ticker symbol
curl "https://api.aevorex.com/api/v1/search/?query=AAPL"

# Search by company name
curl "https://api.aevorex.com/api/v1/search/?query=Microsoft"

# Search by sector
curl "https://api.aevorex.com/api/v1/search/?query=technology&type=stock"

# Search by exchange
curl "https://api.aevorex.com/api/v1/search/?query=Apple&exchange=NASDAQ"

# Search cryptocurrencies
curl "https://api.aevorex.com/api/v1/search/?query=Bitcoin&type=crypto"

# Search forex pairs
curl "https://api.aevorex.com/api/v1/search/?query=EURUSD&type=forex"
```

---

## Search Features

### **Multi-Market Support**
- **Stocks**: NYSE, NASDAQ, LSE, TSE, and other major exchanges
- **Cryptocurrencies**: Bitcoin, Ethereum, and other major cryptocurrencies
- **Forex**: Major currency pairs and crosses
- **ETFs**: Exchange-traded funds
- **Indices**: Market indices and benchmarks

### **Search Capabilities**
- **Fuzzy Matching**: Finds results even with typos
- **Partial Matching**: Matches partial company names or symbols
- **Multi-language**: Supports company names in multiple languages
- **Alias Support**: Recognizes common company aliases and abbreviations

### **Filtering Options**
- **Type**: Filter by instrument type
- **Exchange**: Filter by specific exchange
- **Country**: Filter by country of incorporation
- **Sector**: Filter by business sector
- **Market Cap**: Filter by market capitalization range

---

## Search Examples

### **Company Name Search**
```bash
curl "https://api.aevorex.com/api/v1/search/?query=Apple%20Inc"
```

### **Ticker Symbol Search**
```bash
curl "https://api.aevorex.com/api/v1/search/?query=AAPL"
```

### **Sector Search**
```bash
curl "https://api.aevorex.com/api/v1/search/?query=technology&type=stock"
```

### **Cryptocurrency Search**
```bash
curl "https://api.aevorex.com/api/v1/search/?query=Bitcoin&type=crypto"
```

### **Forex Search**
```bash
curl "https://api.aevorex.com/api/v1/search/?query=EURUSD&type=forex"
```

---

## Performance Considerations

### **Caching Strategy**
- Results cached for 1 hour
- Popular searches cached longer
- Real-time data for prices and market metrics

### **Rate Limiting**
- Pro tier: 100 searches per hour
- Enterprise tier: 1000 searches per hour
- Free tier: Not available

### **Response Time**
- Typical response time: 50-200ms
- Complex queries: up to 500ms
- Cached results: < 50ms

---

## Error Responses

### **403 Forbidden (Subscription Required)**
```json
{
  "error": "subscription_required",
  "message": "Pro or Enterprise subscription required for search functionality",
  "code": 403,
  "upgrade_url": "https://api.aevorex.com/pricing"
}
```

### **400 Bad Request**
```json
{
  "error": "invalid_query",
  "message": "Search query must be at least 2 characters long",
  "code": 400
}
```

### **429 Rate Limited**
```json
{
  "error": "rate_limited",
  "message": "Search rate limit exceeded",
  "code": 429,
  "retry_after": 3600
}
```

---

## Integration Examples

### **JavaScript/AJAX**
```javascript
// Search for companies
async function searchTickers(query) {
  try {
    const response = await fetch(`/api/v1/search/?query=${encodeURIComponent(query)}`);
    const data = await response.json();
    
    if (data.results) {
      data.results.forEach(result => {
        console.log(`${result.symbol}: ${result.name} (${result.exchange})`);
      });
    }
  } catch (error) {
    console.error('Search failed:', error);
  }
}

// Usage
searchTickers('Apple');
```

### **Python**
```python
import requests

def search_tickers(query, limit=20):
    try:
        response = requests.get(
            'https://api.aevorex.com/api/v1/search/',
            params={
                'query': query,
                'limit': limit
            }
        )
        data = response.json()
        
        if 'results' in data:
            for result in data['results']:
                print(f"{result['symbol']}: {result['name']} ({result['exchange']})")
                
    except requests.RequestException as e:
        print(f"Search failed: {e}")

# Usage
search_tickers('Apple', limit=10)
```

---

## Best Practices

### **Query Optimization**
- Use specific company names for better results
- Include exchange information when known
- Use appropriate filters to narrow results

### **Result Handling**
- Check for empty results
- Handle rate limiting gracefully
- Cache results client-side when appropriate

### **User Experience**
- Implement autocomplete functionality
- Show loading states during search
- Display relevant metadata (exchange, country, etc.)

---

**Total Search Endpoints: 1** ✅


# EODHD - Macro Endpoints

**Category:** EODHD - Macro  
**Total Endpoints:** 2  
**Authentication:** Not required  
**Caching:** 1 hour

This category provides macroeconomic data including economic calendar and macro indicators.

---

## 1. GET /api/v1/eodhd/macro/economic-calendar

**Description:** Returns economic calendar data with upcoming and historical economic events.

**Parameters:**
- **Query:**
  - `from_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)
  - `to_date` (string, optional): End date in ISO 8601 format (YYYY-MM-DD)
  - `country` (string, optional): Country code to filter events (US, EU, UK, etc.)

**Response:**
```json
{
  "economic_events": [
    {
      "id": "event_12345",
      "title": "Federal Reserve Interest Rate Decision",
      "country": "US",
      "currency": "USD",
      "importance": "high",
      "category": "interest_rates",
      "event_date": "2024-01-15T14:00:00Z",
      "previous_value": "5.25%",
      "forecast_value": "5.25%",
      "actual_value": "5.25%",
      "unit": "percent",
      "description": "Federal Open Market Committee (FOMC) interest rate decision",
      "impact": "high",
      "volatility_expected": true,
      "affected_markets": ["forex", "stocks", "bonds"]
    },
    {
      "id": "event_12346",
      "title": "US Consumer Price Index (CPI)",
      "country": "US",
      "currency": "USD",
      "importance": "high",
      "category": "inflation",
      "event_date": "2024-01-16T08:30:00Z",
      "previous_value": "3.2%",
      "forecast_value": "3.1%",
      "actual_value": null,
      "unit": "percent",
      "description": "Monthly change in consumer prices",
      "impact": "high",
      "volatility_expected": true,
      "affected_markets": ["forex", "stocks", "bonds"]
    }
  ],
  "metadata": {
    "total_events": 2,
    "from_date": "2024-01-15",
    "to_date": "2024-01-16",
    "country_filter": "US",
    "last_updated": "2024-01-15T10:30:00Z"
  }
}
```

**Response Fields:**
- `economic_events` (array): Array of economic events
  - `id` (string): Unique event identifier
  - `title` (string): Event title
  - `country` (string): Country code
  - `currency` (string): Currency code
  - `importance` (string): Event importance (low, medium, high)
  - `category` (string): Event category
  - `event_date` (string): Event date and time
  - `previous_value` (string): Previous value
  - `forecast_value` (string): Forecasted value
  - `actual_value` (string): Actual value (null if not yet released)
  - `unit` (string): Value unit
  - `description` (string): Event description
  - `impact` (string): Market impact level
  - `volatility_expected` (boolean): Whether volatility is expected
  - `affected_markets` (array): Markets likely to be affected
- `metadata` (object): Response metadata
  - `total_events` (number): Total number of events
  - `from_date` (string): Start date
  - `to_date` (string): End date
  - `country_filter` (string): Country filter applied
  - `last_updated` (string): Last update timestamp

**Behavior:**
- Cached for 1 hour
- Defaults to next 7 days if no date range specified
- Returns 400 if invalid date range

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/macro/economic-calendar?from_date=2024-01-15&to_date=2024-01-31&country=US"
```

---

## 2. GET /api/v1/eodhd/macro/macro-indicators

**Description:** Returns macroeconomic indicators data for a specific country.

**Parameters:**
- **Query:**
  - `country` (string, required): Country code (US, EU, UK, JP, etc.)

**Response:**
```json
{
  "country": "US",
  "indicators": [
    {
      "indicator": "GDP Growth Rate",
      "value": "2.1%",
      "unit": "percent",
      "period": "Q3 2023",
      "previous_value": "2.0%",
      "change": "0.1%",
      "trend": "increasing",
      "importance": "high",
      "description": "Quarterly GDP growth rate",
      "last_updated": "2024-01-15T10:30:00Z"
    },
    {
      "indicator": "Inflation Rate (CPI)",
      "value": "3.2%",
      "unit": "percent",
      "period": "December 2023",
      "previous_value": "3.1%",
      "change": "0.1%",
      "trend": "increasing",
      "importance": "high",
      "description": "Consumer Price Index inflation rate",
      "last_updated": "2024-01-15T10:30:00Z"
    },
    {
      "indicator": "Unemployment Rate",
      "value": "3.7%",
      "unit": "percent",
      "period": "December 2023",
      "previous_value": "3.8%",
      "change": "-0.1%",
      "trend": "decreasing",
      "importance": "high",
      "description": "Unemployment rate",
      "last_updated": "2024-01-15T10:30:00Z"
    },
    {
      "indicator": "Interest Rate",
      "value": "5.25%",
      "unit": "percent",
      "period": "January 2024",
      "previous_value": "5.25%",
      "change": "0.0%",
      "trend": "stable",
      "importance": "high",
      "description": "Federal funds rate",
      "last_updated": "2024-01-15T10:30:00Z"
    }
  ],
  "metadata": {
    "country": "US",
    "total_indicators": 4,
    "last_updated": "2024-01-15T10:30:00Z",
    "data_source": "EODHD"
  }
}
```

**Response Fields:**
- `country` (string): Country code
- `indicators` (array): Array of macro indicators
  - `indicator` (string): Indicator name
  - `value` (string): Current value
  - `unit` (string): Value unit
  - `period` (string): Data period
  - `previous_value` (string): Previous value
  - `change` (string): Change from previous
  - `trend` (string): Trend direction (increasing, decreasing, stable)
  - `importance` (string): Indicator importance (low, medium, high)
  - `description` (string): Indicator description
  - `last_updated` (string): Last update timestamp
- `metadata` (object): Response metadata
  - `country` (string): Country code
  - `total_indicators` (number): Total number of indicators
  - `last_updated` (string): Last update timestamp
  - `data_source` (string): Data source

**Behavior:**
- Cached for 1 hour
- Returns 404 if country not found
- Includes key economic indicators

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/macro/macro-indicators?country=US"
```

---

## Macro Data Features

### **Economic Calendar**
- **Event Types**: Interest rates, inflation, employment, GDP, trade balance
- **Importance Levels**: Low, medium, high impact events
- **Market Impact**: Expected volatility and affected markets
- **Historical Data**: Past events with actual vs. forecast values

### **Macro Indicators**
- **GDP**: Gross Domestic Product growth rates
- **Inflation**: Consumer Price Index, Producer Price Index
- **Employment**: Unemployment rates, job creation
- **Monetary Policy**: Interest rates, money supply
- **Trade**: Balance of trade, current account

### **Country Coverage**
- **Major Economies**: US, EU, UK, Japan, China, Canada
- **Emerging Markets**: Brazil, India, Russia, South Africa
- **Regional Data**: Eurozone, ASEAN, BRICS
- **Global Indicators**: World GDP, global inflation

---

## Performance Considerations

### **Caching Strategy**
- 1 hour cache for optimal performance
- Real-time updates for high-impact events
- Historical data cached longer

### **Rate Limiting**
- Standard rate limits apply
- Recommended: 1 request per 30 seconds
- Burst: up to 5 requests per minute

### **Response Time**
- Economic calendar: 200-500ms
- Macro indicators: 100-300ms
- Cached responses: < 100ms

---

## Error Responses

### **404 Not Found**
```json
{
  "error": "country_not_found",
  "message": "Country code 'XX' not found",
  "code": 404
}
```

### **400 Bad Request**
```json
{
  "error": "invalid_date_range",
  "message": "Invalid date range or format",
  "code": 400
}
```

---

## Integration Examples

### **JavaScript/AJAX**
```javascript
// Get economic calendar
async function getEconomicCalendar(fromDate, toDate, country = null) {
  try {
    const params = new URLSearchParams();
    if (fromDate) params.append('from_date', fromDate);
    if (toDate) params.append('to_date', toDate);
    if (country) params.append('country', country);
    
    const response = await fetch(`/api/v1/eodhd/macro/economic-calendar?${params}`);
    const data = await response.json();
    
    if (data.economic_events) {
      data.economic_events.forEach(event => {
        console.log(`${event.title} - ${event.country} (${event.importance})`);
      });
    }
  } catch (error) {
    console.error('Failed to fetch economic calendar:', error);
  }
}

// Get macro indicators
async function getMacroIndicators(country) {
  try {
    const response = await fetch(`/api/v1/eodhd/macro/macro-indicators?country=${country}`);
    const data = await response.json();
    
    if (data.indicators) {
      data.indicators.forEach(indicator => {
        console.log(`${indicator.indicator}: ${indicator.value} (${indicator.trend})`);
      });
    }
  } catch (error) {
    console.error('Failed to fetch macro indicators:', error);
  }
}

// Usage
getEconomicCalendar('2024-01-15', '2024-01-31', 'US');
getMacroIndicators('US');
```

### **Python**
```python
import requests

def get_economic_calendar(from_date=None, to_date=None, country=None):
    try:
        params = {}
        if from_date:
            params['from_date'] = from_date
        if to_date:
            params['to_date'] = to_date
        if country:
            params['country'] = country
        
        response = requests.get(
            'https://api.aevorex.com/api/v1/eodhd/macro/economic-calendar',
            params=params
        )
        data = response.json()
        
        if 'economic_events' in data:
            for event in data['economic_events']:
                print(f"{event['title']} - {event['country']} ({event['importance']})")
                
    except requests.RequestException as e:
        print(f"Failed to fetch economic calendar: {e}")

def get_macro_indicators(country):
    try:
        response = requests.get(
            'https://api.aevorex.com/api/v1/eodhd/macro/macro-indicators',
            params={'country': country}
        )
        data = response.json()
        
        if 'indicators' in data:
            for indicator in data['indicators']:
                print(f"{indicator['indicator']}: {indicator['value']} ({indicator['trend']})")
                
    except requests.RequestException as e:
        print(f"Failed to fetch macro indicators: {e}")

# Usage
get_economic_calendar('2024-01-15', '2024-01-31', 'US')
get_macro_indicators('US')
```

---

## Best Practices

### **Economic Calendar**
- Monitor high-impact events for market volatility
- Compare actual vs. forecast values for market reactions
- Use country filters for relevant markets

### **Macro Indicators**
- Track key indicators for economic health
- Monitor trends and changes over time
- Consider multiple countries for global perspective

### **Data Usage**
- Combine with technical analysis for trading decisions
- Use for fundamental analysis and market outlook
- Monitor for economic policy changes

---

**Total EODHD Macro Endpoints: 2** ✅


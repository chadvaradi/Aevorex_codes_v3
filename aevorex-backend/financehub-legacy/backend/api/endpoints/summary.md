# Summary Endpoints

**Category:** Summary  
**Total Endpoints:** 4  
**Authentication:** Not required  
**Caching:** 1 hour  
**Status:** 🔄 **MCP Integration Planned**

This category provides market summaries for different time periods including daily, weekly, monthly, and custom date ranges.

## 🚧 **Current Status: MCP-Ready Framework**

The Summary module is currently a **framework ready for MCP (Model Context Protocol) integration**. The endpoints are implemented but return placeholder responses as they await AI-powered aggregation logic.

### **Strategic Approach:**
- **Current**: Framework with proper structure, logging, and error handling
- **Future**: MCP agents will aggregate data from multiple sources (EODHD, Macro, Fundamentals)
- **Goal**: Bloomberg-style narrative reports with AI-generated insights

### **Why Not Direct EODHD Integration Now?**
- **Avoid Duplication**: Direct EODHD integration would duplicate existing endpoints (ticker, technicals, intraday)
- **Limited Value**: Users can already access the same data through existing endpoints
- **Future-Proof**: MCP integration will provide unique value through AI aggregation and narrative generation

---

## 1. GET /api/v1/summary/daily

**Description:** Returns daily market summary for a specific date.

**Parameters:**
- **Query:**
  - `target_date` (string, optional): Target date in ISO 8601 format (YYYY-MM-DD), defaults to today

**Response:**
```json
{
  "date": "2024-01-15",
  "summary": {
    "market_overview": {
      "sp500": {
        "symbol": "SPX",
        "price": 4783.45,
        "change": 23.67,
        "change_percent": 0.50
      },
      "nasdaq": {
        "symbol": "IXIC",
        "price": 14972.76,
        "change": 89.34,
        "change_percent": 0.60
      },
      "dow_jones": {
        "symbol": "DJI",
        "price": 37347.58,
        "change": 112.45,
        "change_percent": 0.30
      }
    },
    "sector_performance": [
      {
        "sector": "Technology",
        "change_percent": 0.85,
        "top_performer": "AAPL",
        "top_performer_change": 1.28
      },
      {
        "sector": "Healthcare",
        "change_percent": 0.45,
        "top_performer": "JNJ",
        "top_performer_change": 0.92
      }
    ],
    "top_movers": {
      "gainers": [
        {
          "symbol": "AAPL",
          "name": "Apple Inc.",
          "price": 193.58,
          "change_percent": 1.28
        }
      ],
      "losers": [
        {
          "symbol": "TSLA",
          "name": "Tesla Inc.",
          "price": 234.56,
          "change_percent": -2.15
        }
      ]
    },
    "volume_leaders": [
      {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "volume": 45678900,
        "price": 193.58
      }
    ]
  },
  "metadata": {
    "last_updated": "2024-01-15T16:00:00Z",
    "market_status": "closed",
    "trading_day": true
  }
}
```

**Response Fields:**
- `date` (string): Summary date
- `summary` (object): Market summary data
  - `market_overview` (object): Major indices performance
  - `sector_performance` (array): Sector-wise performance
  - `top_movers` (object): Top gainers and losers
  - `volume_leaders` (array): Highest volume stocks
- `metadata` (object): Summary metadata
  - `last_updated` (string): Last update timestamp
  - `market_status` (string): Market status (open, closed, pre-market, after-hours)
  - `trading_day` (boolean): Whether it's a trading day

**Behavior:**
- Cached for 1 hour
- Defaults to current date if not specified
- Returns 404 for future dates
- Includes pre-market and after-hours data when available

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/summary/daily?target_date=2024-01-15"
```

---

## 2. GET /api/v1/summary/weekly

**Description:** Returns weekly market summary for a specific week.

**Parameters:**
- **Query:**
  - `week_start` (string, optional): Week start date in ISO 8601 format (YYYY-MM-DD), defaults to current week

**Response:**
```json
{
  "week_start": "2024-01-15",
  "week_end": "2024-01-19",
  "summary": {
    "weekly_performance": {
      "sp500": {
        "symbol": "SPX",
        "start_price": 4759.78,
        "end_price": 4783.45,
        "change": 23.67,
        "change_percent": 0.50
      },
      "nasdaq": {
        "symbol": "IXIC",
        "start_price": 14883.42,
        "end_price": 14972.76,
        "change": 89.34,
        "change_percent": 0.60
      }
    },
    "sector_rotation": [
      {
        "sector": "Technology",
        "weekly_change_percent": 2.15,
        "rank": 1
      },
      {
        "sector": "Healthcare",
        "weekly_change_percent": 1.45,
        "rank": 2
      }
    ],
    "weekly_highlights": [
      {
        "date": "2024-01-16",
        "event": "Apple earnings beat expectations",
        "impact": "positive",
        "affected_stocks": ["AAPL", "TSM", "QCOM"]
      }
    ],
    "volatility_metrics": {
      "vix": 18.45,
      "vix_change": -1.23,
      "market_fear_greed_index": 65
    }
  },
  "metadata": {
    "last_updated": "2024-01-19T16:00:00Z",
    "trading_days": 5,
    "market_status": "closed"
  }
}
```

**Response Fields:**
- `week_start` (string): Week start date
- `week_end` (string): Week end date
- `summary` (object): Weekly summary data
  - `weekly_performance` (object): Weekly performance of major indices
  - `sector_rotation` (array): Sector performance ranking
  - `weekly_highlights` (array): Key market events during the week
  - `volatility_metrics` (object): Volatility and sentiment indicators
- `metadata` (object): Summary metadata
  - `last_updated` (string): Last update timestamp
  - `trading_days` (number): Number of trading days in the week
  - `market_status` (string): Market status

**Behavior:**
- Cached for 1 hour
- Defaults to current week if not specified
- Includes weekend and holiday adjustments
- Returns 404 for future weeks

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/summary/weekly?week_start=2024-01-15"
```

---

## 3. GET /api/v1/summary/custom

**Description:** Returns custom market summary for a specified date range.

**Parameters:**
- **Query:**
  - `start_date` (string, required): Start date in ISO 8601 format (YYYY-MM-DD)
  - `end_date` (string, required): End date in ISO 8601 format (YYYY-MM-DD)

**Response:**
```json
{
  "start_date": "2024-01-01",
  "end_date": "2024-01-31",
  "summary": {
    "period_performance": {
      "sp500": {
        "symbol": "SPX",
        "start_price": 4769.83,
        "end_price": 4783.45,
        "change": 13.62,
        "change_percent": 0.29
      },
      "nasdaq": {
        "symbol": "IXIC",
        "start_price": 14883.42,
        "end_price": 14972.76,
        "change": 89.34,
        "change_percent": 0.60
      }
    },
    "best_performing_sectors": [
      {
        "sector": "Technology",
        "change_percent": 3.45,
        "top_stock": "AAPL",
        "top_stock_change": 5.67
      }
    ],
    "worst_performing_sectors": [
      {
        "sector": "Energy",
        "change_percent": -2.15,
        "worst_stock": "XOM",
        "worst_stock_change": -4.23
      }
    ],
    "key_events": [
      {
        "date": "2024-01-15",
        "event": "Federal Reserve meeting",
        "impact": "market_wide",
        "description": "Fed maintains interest rates"
      }
    ],
    "statistics": {
      "trading_days": 22,
      "average_volume": 45000000000,
      "volatility_period": 18.45,
      "correlation_sp500_nasdaq": 0.89
    }
  },
  "metadata": {
    "last_updated": "2024-01-31T16:00:00Z",
    "period_days": 31,
    "trading_days": 22
  }
}
```

**Response Fields:**
- `start_date` (string): Period start date
- `end_date` (string): Period end date
- `summary` (object): Custom period summary data
  - `period_performance` (object): Performance of major indices
  - `best_performing_sectors` (array): Top performing sectors
  - `worst_performing_sectors` (array): Worst performing sectors
  - `key_events` (array): Important market events
  - `statistics` (object): Period statistics
- `metadata` (object): Summary metadata
  - `last_updated` (string): Last update timestamp
  - `period_days` (number): Total days in period
  - `trading_days` (number): Trading days in period

**Behavior:**
- Cached for 1 hour
- Maximum period: 1 year
- Returns 400 for invalid date ranges
- Includes weekend and holiday adjustments

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/summary/custom?start_date=2024-01-01&end_date=2024-01-31"
```

---

## 4. GET /api/v1/summary/monthly

**Description:** Returns monthly market summary for a specific month.

**Parameters:**
- **Query:**
  - `month_start` (string, optional): Month start date in ISO 8601 format (YYYY-MM-DD), defaults to current month

**Response:**
```json
{
  "month": "2024-01",
  "month_start": "2024-01-01",
  "month_end": "2024-01-31",
  "summary": {
    "monthly_performance": {
      "sp500": {
        "symbol": "SPX",
        "start_price": 4769.83,
        "end_price": 4783.45,
        "change": 13.62,
        "change_percent": 0.29
      },
      "nasdaq": {
        "symbol": "IXIC",
        "start_price": 14883.42,
        "end_price": 14972.76,
        "change": 89.34,
        "change_percent": 0.60
      }
    },
    "monthly_highlights": [
      {
        "date": "2024-01-15",
        "event": "Apple earnings beat expectations",
        "impact": "positive",
        "affected_sectors": ["Technology", "Consumer Electronics"]
      },
      {
        "date": "2024-01-22",
        "event": "Federal Reserve maintains rates",
        "impact": "neutral",
        "affected_sectors": ["Financials", "Real Estate"]
      }
    ],
    "sector_performance": [
      {
        "sector": "Technology",
        "monthly_change_percent": 3.45,
        "rank": 1,
        "top_performer": "AAPL",
        "top_performer_change": 5.67
      },
      {
        "sector": "Healthcare",
        "monthly_change_percent": 2.15,
        "rank": 2,
        "top_performer": "JNJ",
        "top_performer_change": 3.89
      }
    ],
    "monthly_statistics": {
      "trading_days": 22,
      "average_daily_volume": 45000000000,
      "volatility_average": 18.45,
      "correlation_sp500_nasdaq": 0.89,
      "market_cap_change": 0.29
    }
  },
  "metadata": {
    "last_updated": "2024-01-31T16:00:00Z",
    "trading_days": 22,
    "market_status": "closed"
  }
}
```

**Response Fields:**
- `month` (string): Month identifier (YYYY-MM)
- `month_start` (string): Month start date
- `month_end` (string): Month end date
- `summary` (object): Monthly summary data
  - `monthly_performance` (object): Monthly performance of major indices
  - `monthly_highlights` (array): Key market events during the month
  - `sector_performance` (array): Sector performance ranking
  - `monthly_statistics` (object): Monthly market statistics
- `metadata` (object): Summary metadata
  - `last_updated` (string): Last update timestamp
  - `trading_days` (number): Number of trading days in the month
  - `market_status` (string): Market status

**Behavior:**
- Cached for 1 hour
- Defaults to current month if not specified
- Includes weekend and holiday adjustments
- Returns 404 for future months

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/summary/monthly?month_start=2024-01-01"
```

---

## Summary Features

### **Time Period Support**
- **Daily**: Current day or specific date
- **Weekly**: Current week or specific week
- **Monthly**: Current month or specific month
- **Custom**: Any date range up to 1 year

### **Market Coverage**
- **Major Indices**: S&P 500, NASDAQ, Dow Jones
- **Sector Performance**: All major sectors
- **Individual Stocks**: Top movers and volume leaders
- **Market Events**: Earnings, Fed meetings, economic data

### **Data Quality**
- **Real-time**: Current market data
- **Historical**: Past performance data
- **Adjusted**: Weekend and holiday adjustments
- **Validated**: Multiple data source validation

---

## Performance Considerations

### **Caching Strategy**
- 1-hour cache for optimal performance
- Real-time data for current periods
- Historical data cached longer

### **Response Time**
- Daily summary: 100-200ms
- Weekly summary: 200-300ms
- Monthly summary: 300-500ms
- Custom summary: 500ms-1s

### **Data Volume**
- Daily: ~50KB
- Weekly: ~100KB
- Monthly: ~150KB
- Custom: varies by period

---

## Error Responses

### **400 Bad Request**
```json
{
  "error": "invalid_date_range",
  "message": "Start date must be before end date",
  "code": 400
}
```

### **404 Not Found**
```json
{
  "error": "date_not_found",
  "message": "No data available for the specified date",
  "code": 404
}
```

---

**Total Summary Endpoints: 4** ✅


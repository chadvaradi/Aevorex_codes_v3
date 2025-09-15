# EODHD - News Endpoints

**Category:** EODHD - News  
**Total Endpoints:** 1  
**Authentication:** Not required  
**Caching:** 15 minutes

This category provides financial news feed data from various sources.

---

## 1. GET /api/v1/eodhd/news/

**Description:** Returns latest financial news feed with optional filtering by tickers, language, and date range.

**Parameters:**
- **Query:**
  - `tickers` (string, optional): Comma-separated list of ticker symbols to filter news
  - `limit` (integer, optional, default: 20): Maximum number of news articles to return
  - `lang` (string, optional, default: "en"): Language code (en, es, fr, de, etc.)
  - `from_date` (string, optional): Start date in ISO 8601 format (YYYY-MM-DD)

**Response:**
```json
{
  "news": [
    {
      "id": "news_12345",
      "title": "Apple Reports Strong Q4 Earnings, Beats Expectations",
      "summary": "Apple Inc. reported better-than-expected quarterly earnings, driven by strong iPhone sales and services revenue growth.",
      "content": "Apple Inc. (AAPL) reported fourth-quarter earnings that exceeded analyst expectations...",
      "url": "https://example.com/news/apple-q4-earnings",
      "source": "Financial Times",
      "author": "John Smith",
      "published_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z",
      "tickers": ["AAPL"],
      "sentiment": "positive",
      "sentiment_score": 0.75,
      "category": "earnings",
      "tags": ["earnings", "iphone", "services", "revenue"],
      "image_url": "https://example.com/images/apple-earnings.jpg",
      "language": "en"
    },
    {
      "id": "news_12346",
      "title": "Federal Reserve Maintains Interest Rates at Current Level",
      "summary": "The Federal Reserve kept interest rates unchanged at 5.25%, citing ongoing inflation concerns and economic uncertainty.",
      "content": "The Federal Reserve announced today that it will maintain the federal funds rate at 5.25%...",
      "url": "https://example.com/news/fed-rates-decision",
      "source": "Reuters",
      "author": "Jane Doe",
      "published_at": "2024-01-15T09:15:00Z",
      "updated_at": "2024-01-15T09:15:00Z",
      "tickers": ["SPY", "QQQ", "DIA"],
      "sentiment": "neutral",
      "sentiment_score": 0.10,
      "category": "macro",
      "tags": ["federal-reserve", "interest-rates", "inflation", "monetary-policy"],
      "image_url": "https://example.com/images/fed-meeting.jpg",
      "language": "en"
    }
  ],
  "metadata": {
    "total_count": 2,
    "limit": 20,
    "language": "en",
    "last_updated": "2024-01-15T10:30:00Z",
    "sources": ["Financial Times", "Reuters", "Bloomberg", "CNBC"]
  }
}
```

**Response Fields:**
- `news` (array): Array of news articles
  - `id` (string): Unique news article identifier
  - `title` (string): News article title
  - `summary` (string): Brief summary of the article
  - `content` (string): Full article content (truncated in response)
  - `url` (string): Original article URL
  - `source` (string): News source name
  - `author` (string): Article author
  - `published_at` (string): Publication timestamp
  - `updated_at` (string): Last update timestamp
  - `tickers` (array): Related stock tickers
  - `sentiment` (string): Sentiment analysis (positive, negative, neutral)
  - `sentiment_score` (number): Sentiment score (-1 to 1)
  - `category` (string): News category (earnings, macro, mergers, etc.)
  - `tags` (array): Article tags
  - `image_url` (string): Article image URL
  - `language` (string): Article language code
- `metadata` (object): Response metadata
  - `total_count` (number): Total number of articles returned
  - `limit` (number): Maximum articles requested
  - `language` (string): Language filter applied
  - `last_updated` (string): Last update timestamp
  - `sources` (array): Available news sources

**Behavior:**
- Cached for 15 minutes
- Real-time news updates
- Supports multiple languages
- Sentiment analysis included

**Usage:**
```bash
curl "https://api.aevorex.com/api/v1/eodhd/news/?tickers=AAPL,MSFT&limit=10&lang=en"
```

**Advanced Usage Examples:**
```bash
# Get latest news for specific tickers
curl "https://api.aevorex.com/api/v1/eodhd/news/?tickers=AAPL,MSFT,GOOGL&limit=5"

# Get news in Spanish
curl "https://api.aevorex.com/api/v1/eodhd/news/?lang=es&limit=10"

# Get news from specific date
curl "https://api.aevorex.com/api/v1/eodhd/news/?from_date=2024-01-15&limit=20"

# Get all latest news
curl "https://api.aevorex.com/api/v1/eodhd/news/?limit=50"
```

---

## News Features

### **News Sources**
- **Financial Media**: Bloomberg, Reuters, Financial Times, CNBC
- **Business News**: Wall Street Journal, MarketWatch, Yahoo Finance
- **International**: BBC Business, Deutsche Welle, Le Monde
- **Specialized**: Seeking Alpha, Motley Fool, Benzinga

### **Content Categories**
- **Earnings**: Quarterly and annual earnings reports
- **Macro**: Economic indicators, central bank decisions
- **Mergers**: M&A announcements and deals
- **IPO**: Initial public offerings and listings
- **Regulatory**: SEC filings, regulatory changes
- **Market**: Market analysis and commentary

### **Sentiment Analysis**
- **Positive**: Bullish news, positive developments
- **Negative**: Bearish news, negative developments
- **Neutral**: Factual reporting, mixed signals
- **Score Range**: -1.0 (very negative) to 1.0 (very positive)

### **Language Support**
- **English**: Default language
- **Spanish**: Spanish language news
- **French**: French language news
- **German**: German language news
- **Other**: Additional languages available

---

## Performance Considerations

### **Caching Strategy**
- 15 minutes cache for optimal freshness
- Real-time updates during market hours
- Historical news cached longer

### **Rate Limiting**
- Standard rate limits apply
- Recommended: 1 request per 30 seconds
- Burst: up to 5 requests per minute

### **Response Time**
- Latest news: 100-200ms
- Filtered news: 200-300ms
- Cached responses: < 50ms

---

## Error Responses

### **400 Bad Request**
```json
{
  "error": "invalid_parameters",
  "message": "Invalid language code or date format",
  "code": 400
}
```

### **429 Rate Limited**
```json
{
  "error": "rate_limited",
  "message": "News API rate limit exceeded",
  "code": 429,
  "retry_after": 30
}
```

---

## Integration Examples

### **JavaScript/AJAX**
```javascript
// Fetch latest financial news
async function getFinancialNews(tickers = [], limit = 20) {
  try {
    const params = new URLSearchParams();
    if (tickers.length > 0) {
      params.append('tickers', tickers.join(','));
    }
    params.append('limit', limit.toString());
    
    const response = await fetch(`/api/v1/eodhd/news/?${params}`);
    const data = await response.json();
    
    if (data.news) {
      data.news.forEach(article => {
        console.log(`${article.title} - ${article.source} (${article.sentiment})`);
      });
    }
  } catch (error) {
    console.error('Failed to fetch news:', error);
  }
}

// Usage
getFinancialNews(['AAPL', 'MSFT'], 10);
```

### **Python**
```python
import requests

def get_financial_news(tickers=None, limit=20, language='en'):
    try:
        params = {
            'limit': limit,
            'lang': language
        }
        
        if tickers:
            params['tickers'] = ','.join(tickers)
        
        response = requests.get(
            'https://api.aevorex.com/api/v1/eodhd/news/',
            params=params
        )
        data = response.json()
        
        if 'news' in data:
            for article in data['news']:
                print(f"{article['title']} - {article['source']} ({article['sentiment']})")
                
    except requests.RequestException as e:
        print(f"Failed to fetch news: {e}")

# Usage
get_financial_news(['AAPL', 'MSFT'], limit=10)
```

---

## Best Practices

### **News Filtering**
- Use specific tickers for relevant news
- Set appropriate limits to avoid large responses
- Use language filters for international content

### **Sentiment Analysis**
- Monitor sentiment trends over time
- Combine with technical analysis for trading decisions
- Consider news impact on market movements

### **Content Consumption**
- Check article URLs for full content
- Respect news source terms of service
- Use summaries for quick market overview

---

**Total EODHD News Endpoints: 1** ✅


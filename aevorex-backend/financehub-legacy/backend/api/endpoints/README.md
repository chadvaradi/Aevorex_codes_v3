# Aevorex FinanceHub API Documentation

**Version:** 1.0  
**Base URL:** `https://api.aevorex.com`  
**Total Endpoints:** 82

This is the central navigation for the FinanceHub Legacy API documentation. Each endpoint category has its own detailed documentation file.

---

## 📋 Quick Overview

| Category | Endpoints | Documentation File | Description |
|----------|-----------|-------------------|-------------|
| **System** | 2 | [system.md](./system.md) | Health checks and metrics |
| **Macro Data** | 21 | [macro.md](./macro.md) | Central bank rates, yield curves, economic indicators |
| **Authentication** | 8 | [auth.md](./auth.md) | OAuth login, user management, token refresh |
| **EODHD - Crypto** | 8 | [eodhd-crypto.md](./eodhd-crypto.md) | Cryptocurrency data and quotes |
| **EODHD - Stock** | 6 | [eodhd-stock.md](./eodhd-stock.md) | Stock market data, EOD, intraday, dividends, splits |
| **EODHD - Technical** | 2 | [eodhd-technical.md](./eodhd-technical.md) | Technical indicators and stock screener |
| **EODHD - News** | 1 | [eodhd-news.md](./eodhd-news.md) | Financial news feed |
| **EODHD - Forex** | 8 | [eodhd-forex.md](./eodhd-forex.md) | Foreign exchange rates and data ✅ **100% Working** |
| **EODHD - Screener** | 1 | [eodhd-screener-macro.md](./eodhd-screener-macro.md) | Stock screening functionality ✅ **100% Working** |
| **EODHD - Macro** | 2 | [eodhd-screener-macro.md](./eodhd-screener-macro.md) | Economic calendar and macro indicators ⚠️ **Limited** |
| **EODHD - Exchanges** | 4 | [eodhd-exchanges.md](./eodhd-exchanges.md) | **Dynamic** exchange information and trading hours ✅ **100% Working** |
| **EODHD - Intraday** | 1 | [eodhd-intraday.md](./eodhd-intraday.md) | Intraday market data ✅ **100% Working** |
| **Fundamentals** | 4 | [fundamentals.md](./fundamentals.md) | Company financials, ratios, earnings ✅ **100% Working** |
| **Ticker Tape** | 2 | [ticker-tape.md](./ticker-tape.md) | EODHD-only real-time ticker feed ✅ **100% Working** |
| **Chat** | 4 | [chat.md](./chat.md) | AI-powered financial analysis ✅ **Working** |
| **Search** | 1 | [search.md](./search.md) | Ticker search functionality ✅ **100% Working** |
| **Summary** | 4 | [summary.md](./summary.md) | Market summaries (daily, weekly, monthly) 🔄 **MCP Integration Planned** |
| **TradingView** | 3 | [tradingview.md](./tradingview.md) | TradingView chart integration ✅ **100% Working** |
| **Billing** | 1 | [billing.md](./billing.md) | Payment webhook handler |

---

## 🚀 Getting Started

1. **System Health**: Start with [system.md](./system.md) to check API status
2. **Authentication**: See [auth.md](./auth.md) for login and user management
3. **Data Access**: Choose your data category from the table above
4. **AI Analysis**: Use [chat.md](./chat.md) for AI-powered financial insights

---

## 📊 Endpoint Categories by Use Case

### **Market Data**
- **Real-time**: [ticker-tape.md](./ticker-tape.md)
- **Historical**: [eodhd-stock.md](./eodhd-stock.md), [eodhd-crypto.md](./eodhd-crypto.md), [eodhd-forex.md](./eodhd-forex.md)
- **Technical**: [eodhd-technical.md](./eodhd-technical.md)
- **Fundamentals**: [fundamentals.md](./fundamentals.md)

### **Economic Data**
- **Central Banks**: [macro.md](./macro.md)
- **Economic Calendar**: [eodhd-macro.md](./eodhd-macro.md)
- **Market News**: [eodhd-news.md](./eodhd-news.md)

### **Analysis & Insights**
- **AI Chat**: [chat.md](./chat.md)
- **Market Summaries**: [summary.md](./summary.md)
- **Stock Screening**: [eodhd-screener.md](./eodhd-screener.md)
- **Search**: [search.md](./search.md)

### **Integration**
- **TradingView**: [tradingview.md](./tradingview.md) - **Production Ready** 🚀
  - Symbols endpoint: Real EODHD data
  - Symbol config: TradingView-compatible format
  - Bars endpoint: Dual EOD/intraday logic with real OHLCV data
- **Webhooks**: [billing.md](./billing.md)

### **Market Status & Trading Hours**
- **Dynamic Trading Hours**: [eodhd-exchanges.md](./eodhd-exchanges.md) - Real-time EODHD API integration
- **Market Status**: Live market open/closed status with holiday detection
- **Timezone Support**: Accurate timezone handling for global exchanges

---

## 🔧 General API Information

### **Authentication**
- Most endpoints require **JWT authentication**
- Premium features require **Pro/Enterprise** subscription
- OAuth flow available via [auth.md](./auth.md)

### **Rate Limits**
- **Free Tier**: 100 requests/hour
- **Pro Tier**: 1000 requests/hour  
- **Enterprise**: Custom limits

### **Response Formats**
- **JSON**: All endpoints return JSON
- **Dates**: ISO 8601 format (YYYY-MM-DD)
- **Timestamps**: ISO 8601 with timezone (YYYY-MM-DDTHH:MM:SSZ)

### **Error Handling**
- **200**: Success
- **400**: Bad Request
- **401**: Unauthorized
- **403**: Forbidden (subscription required)
- **404**: Not Found
- **429**: Rate Limited
- **500**: Internal Server Error

### **Caching**
- Most endpoints cached for **1 hour**
- Real-time data cached for **5 minutes**
- Static data cached for **1 day**

---

## 📞 Support

- **Documentation Issues**: Check individual category files
- **API Questions**: Contact development team
- **Subscription**: See [billing.md](./billing.md)

---

**Total Endpoints: 82** ✅

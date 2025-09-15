# FRED API Availability Matrix - MCP Integration

## 🎯 **Purpose**
This matrix clearly defines what data is **guaranteed available** vs **limited** vs **not available** in the FRED API for MCP integration. This is critical for user trust and product positioning.

## 📊 **Availability Status**

| Status | Meaning | User Experience |
|--------|---------|-----------------|
| ✅ **AVAILABLE** | Spot/real-time data, high quality | User gets exactly what they expect |
| ⚠️ **LIMITED** | Index/average data, medium quality | User gets alternative data with clear warning |
| ❌ **NOT AVAILABLE** | No suitable data in FRED | User gets explicit "no data" message |

---

## 💰 **COMMODITIES**

### ✅ **AVAILABLE - Spot Prices**
| Commodity | FRED Series | Data Type | Quality | Notes |
|-----------|-------------|-----------|---------|-------|
| **WTI Crude Oil** | `DCOILWTICO` | Spot Price | High | Real-time, daily |
| **Brent Crude Oil** | `DCOILBRENTEU` | Spot Price | High | Real-time, daily |

### ⚠️ **LIMITED - Indices Only**
| Commodity | FRED Series | Data Type | Quality | Warning Message |
|-----------|-------------|-----------|---------|-----------------|
| **Gold** | `IR14270` | Import Price Index | Medium | "Spot GOLD not available. Returned price index instead." |
| **Silver** | `IR14299` | Import Price Index | Medium | "Spot SILVER not available. Returned price index instead." |
| **Natural Gas** | `PNGASEUUSDM` | Europe Price | Medium | "Global natural gas spot not available. Returned Europe price instead." |
| **Sugar** | `PSUGAISAUSDM` | International Price | Medium | "Spot sugar not available. Returned international price instead." |
| **Coffee** | `PCOFFOTMUSDM` | Specific Grade | Medium | "General coffee spot not available. Returned specific grade price instead." |

### ❌ **NOT AVAILABLE**
| Commodity | Reason | Response |
|-----------|--------|----------|
| **Platinum** | No FRED data | "Platinum spot price not available in FRED API" |
| **Palladium** | No FRED data | "Palladium spot price not available in FRED API" |
| **Wheat** | No FRED data | "Wheat spot price not available in FRED API" |
| **Corn** | No FRED data | "Corn spot price not available in FRED API" |
| **Soybeans** | No FRED data | "Soybeans spot price not available in FRED API" |
| **Gasoline** | No FRED data | "Gasoline spot price not available in FRED API" |

---

## 💱 **EXCHANGE RATES**

### ✅ **AVAILABLE - Spot Rates**
| Currency Pair | FRED Series | Data Type | Quality | Notes |
|---------------|-------------|-----------|---------|-------|
| **EUR/USD** | `DEXUSEU` | Spot Rate | High | Real-time, daily |
| **GBP/USD** | `DEXUSUK` | Spot Rate | High | Real-time, daily |
| **JPY/USD** | `DEXJPUS` | Spot Rate | High | Real-time, daily |
| **CHF/USD** | `DEXCHUS` | Spot Rate | High | Real-time, daily |
| **CAD/USD** | `DEXCAUS` | Spot Rate | High | Real-time, daily |
| **AUD/USD** | `DEXUSAL` | Spot Rate | High | Real-time, daily |

### ⚠️ **LIMITED - Monthly Averages**
| Currency Pair | FRED Series | Data Type | Quality | Warning Message |
|---------------|-------------|-----------|---------|-----------------|
| **HUF/USD** | `CCUSMA02HUM618N` | Monthly Average | Medium | "HUF/USD spot not available. Returned monthly average instead." |
| **CZK/USD** | `CCUSMA02CZM618N` | Monthly Average | Medium | "CZK/USD spot not available. Returned monthly average instead." |
| **TRY/USD** | `DEXTRUS` | Spot Rate | Medium | "TRY/USD data may have gaps. Use with caution." |
| **RUB/USD** | `DEXRUBUS` | Spot Rate | Medium | "RUB/USD data may have gaps. Use with caution." |

### ❌ **NOT AVAILABLE**
| Currency Pair | Reason | Response |
|---------------|--------|----------|
| **BRL/USD** | No FRED data | "BRL/USD not available in FRED API" |
| **INR/USD** | No FRED data | "INR/USD not available in FRED API" |
| **CNY/USD** | No FRED data | "CNY/USD not available in FRED API" |

---

## 🏦 **POLICY RATES**

### ✅ **AVAILABLE - Real-time**
| Rate | FRED Series | Data Type | Quality | Notes |
|------|-------------|-----------|---------|-------|
| **Fed Funds Rate** | `FEDFUNDS` | Policy Rate | High | Real-time, daily |
| **Fed Target Upper** | `DFEDTARU` | Policy Rate | High | Real-time, daily |
| **Fed Target Lower** | `DFEDTARL` | Policy Rate | High | Real-time, daily |
| **Interest on Reserves** | `IORB` | Policy Rate | High | Real-time, daily |

---

## 🚨 **CRITICAL USER EXPERIENCE RULES**

### **Rule 1: No Misleading Fallbacks**
- ❌ **Never** return EUR/USD data when user asks for HUF/USD
- ❌ **Never** return gold index when user asks for gold spot
- ✅ **Always** return explicit "not available" message

### **Rule 2: Clear Warning Messages**
- ⚠️ **Always** warn when returning alternative data
- ⚠️ **Always** explain what type of data is being returned
- ⚠️ **Always** indicate data quality level

### **Rule 3: Consistent Response Format**
```json
{
  "status": "warning",
  "message": "Spot GOLD not available in FRED. Returned price index instead.",
  "data_type_info": {
    "data_type": "commodity_price_index",
    "quality": "medium",
    "description": "Commodity price index (not spot price)",
    "frequency": "monthly",
    "source": "FRED"
  },
  "data": { ... }
}
```

---

## 🎯 **MCP INTEGRATION IMPACT**

### **✅ Guaranteed for MCP**
- Oil prices (WTI, Brent) - spot prices
- Major FX pairs (EUR/USD, GBP/USD, JPY/USD, CHF/USD, CAD/USD, AUD/USD) - spot rates
- Fed Policy Rates - real-time rates

### **⚠️ Limited for MCP**
- Gold/Silver - price indices only
- Emerging FX (HUF, CZK, TRY, RUB) - monthly averages or unreliable data
- Agricultural commodities - specific grades only

### **❌ Not Available for MCP**
- Platinum, Palladium
- Wheat, Corn, Soybeans
- BRL/USD, INR/USD, CNY/USD
- Gasoline, Heating Oil

---

## 🔧 **IMPLEMENTATION REQUIREMENTS**

### **1. Response Status Codes**
- `200 OK`: Exact data requested (spot price, spot rate)
- `200 OK` with `"status": "warning"`: Alternative data provided
- `404 Not Found`: No suitable data available

### **2. Warning Messages**
- Must be clear and specific
- Must explain what alternative data is provided
- Must indicate data quality level

### **3. No Automatic Fallbacks**
- Remove misleading fallback chains
- Return explicit "not available" for unsupported requests
- Only provide alternatives with clear warnings

---

## 📋 **USER COMMUNICATION**

### **Product Positioning**
- **"We provide real-time spot prices for major commodities and currencies"**
- **"For some assets, we provide the best available alternative data with clear warnings"**
- **"We never mislead users with incorrect data types"**

### **Documentation**
- Clear availability matrix
- Explicit limitations
- Warning message examples
- Data quality explanations

---

*Last updated: 2025-09-15*
*Version: 1.0*

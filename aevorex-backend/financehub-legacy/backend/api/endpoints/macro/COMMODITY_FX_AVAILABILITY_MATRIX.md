# Commodity & FX Availability Matrix - FRED API

## 🎯 Cél
Ez a dokumentum tisztázza, hogy mely commodity és FX adatok elérhetők a FRED API-ban, és milyen minőségben. Ez kritikus az MCP integrációhoz és a felhasználói elvárások kezeléséhez.

## 📊 Jelmagyarázat

| Szimbólum | Jelentés |
|-----------|----------|
| ✅ | **Spot/Real-time ár** - Valódi piaci ár, naponta frissül |
| ⚠️ | **Index/Proxy** - Nem valódi spot ár, hanem index vagy proxy |
| ❌ | **Nem elérhető** - Nincs megfelelő adat a FRED API-ban |
| 🔄 | **Fallback szükséges** - Harmadik fél adatforrás kell (EODHD, IMF, stb.) |

---

## 💰 **COMMODITIES**

### Precious Metals
| Commodity | FRED Status | Available Series | Data Type | Quality | Notes |
|-----------|-------------|------------------|-----------|---------|-------|
| **GOLD** | ⚠️ | `IR14270`, `IQ12260`, `WPU15940222` | Export Price Index, Jewelry Index | Medium | Nincs valódi spot price |
| **SILVER** | ⚠️ | `IR14299`, `SLVPRUSD` | Import Price Index, Proxy | Medium | Nincs valódi spot price |
| **PLATINUM** | ❌ | - | - | - | Nincs elérhető adat |
| **PALLADIUM** | ❌ | - | - | - | Nincs elérhető adat |

### Energy
| Commodity | FRED Status | Available Series | Data Type | Quality | Notes |
|-----------|-------------|------------------|-----------|---------|-------|
| **OIL (WTI)** | ✅ | `DCOILWTICO` | Spot Price | High | Valódi spot price, naponta frissül |
| **OIL (Brent)** | ✅ | `DCOILBRENTEU` | Spot Price | High | Valódi spot price, naponta frissül |
| **NATURAL GAS** | ⚠️ | `PNGASEUUSDM`, `MHHNGSP` | Europe Price, Henry Hub | Medium | Nem minden régió elérhető |
| **GASOLINE** | ❌ | - | - | - | Nincs elérhető adat |

### Agricultural
| Commodity | FRED Status | Available Series | Data Type | Quality | Notes |
|-----------|-------------|------------------|-----------|---------|-------|
| **SUGAR** | ⚠️ | `PSUGAISAUSDM` | International Price | Medium | Nem spot, hanem international price |
| **COFFEE** | ⚠️ | `PCOFFOTMUSDM` | Other Mild Arabicas | Medium | Nem spot, hanem specific grade |
| **WHEAT** | ❌ | - | - | - | Nincs elérhető adat |
| **CORN** | ❌ | - | - | - | Nincs elérhető adat |
| **SOYBEANS** | ❌ | - | - | - | Nincs elérhető adat |

---

## 💱 **EXCHANGE RATES**

### Major Pairs
| Currency Pair | FRED Status | Available Series | Data Type | Quality | Notes |
|---------------|-------------|------------------|-----------|---------|-------|
| **EUR/USD** | ✅ | `DEXUSEU` | Spot Rate | High | Valódi spot rate, naponta frissül |
| **GBP/USD** | ✅ | `DEXUSUK` | Spot Rate | High | Valódi spot rate, naponta frissül |
| **JPY/USD** | ✅ | `DEXJPUS` | Spot Rate | High | Valódi spot rate, naponta frissül |
| **CHF/USD** | ✅ | `DEXCHUS` | Spot Rate | High | Valódi spot rate, naponta frissül |
| **CAD/USD** | ✅ | `DEXCAUS` | Spot Rate | High | Valódi spot rate, naponta frissül |
| **AUD/USD** | ✅ | `DEXUSAL` | Spot Rate | High | Valódi spot rate, naponta frissül |

### Emerging Markets
| Currency Pair | FRED Status | Available Series | Data Type | Quality | Notes |
|---------------|-------------|------------------|-----------|---------|-------|
| **HUF/USD** | ⚠️ | `CCUSMA02HUM618N` | Monthly Average | Medium | Nem spot, hanem monthly average |
| **CZK/USD** | ⚠️ | `CCUSMA02CZM618N` | Monthly Average | Medium | Nem spot, hanem monthly average |
| **TRY/USD** | ⚠️ | `DEXTRUS` | Spot Rate | Medium | Deprecated, adatgaps |
| **RUB/USD** | ⚠️ | `DEXRUBUS` | Spot Rate | Medium | Deprecated, adatgaps |
| **CNY/USD** | ⚠️ | `DEXCHUS` | Spot Rate | Medium | Deprecated, adatgaps |
| **BRL/USD** | ❌ | - | - | - | Nincs elérhető adat |
| **INR/USD** | ❌ | - | - | - | Nincs elérhető adat |

---

## 🚨 **KRITIKUS PROBLÉMÁK**

### 1. **Adattípus inkonzisztencia**
- **GOLD**: User spot árat vár → Export price indexet kap
- **HUF/USD**: User spot rate-ot vár → Monthly average-t kap
- **SUGAR**: User spot árat vár → International price-t kap

### 2. **Fallback logika problémák**
- **GOLD** → `DEXUSEU` (teljesen más adattípus)
- **HUF** → `DEXUSEU` (teljesen más deviza)
- **SILVER** → `IQ12260` (nem silver, hanem gold export index)

### 3. **Deprecated sorozatok**
- `DEXTRUS`, `DEXRUBUS`, `DEXCHUS` - adatgaps, nem megbízható
- `GOLDAMGBD228NLBM` - deprecated, nincs friss adat

---

## 🎯 **AJÁNLÁSOK**

### 1. **Immediate Fixes (Tech)**
```python
# Távolítsuk el a félrevezető fallback-okat
SERIES_FALLBACKS = {
    "GOLD": ["IR14270"],  # Csak gold-related index
    "SILVER": ["IR14299"],  # Csak silver-related index
    "HUF": ["CCUSMA02HUM618N"],  # Csak HUF-related data
    # Ne adjunk vissza teljesen más adattípust!
}
```

### 2. **Product Strategy**
- **Transparency**: Minden endpoint válaszban jelezzük az adattípust
- **User Education**: Dokumentáljuk, hogy mit kap a user
- **Fallback Strategy**: Csak azonos típusú adatokra fallback-oljunk

### 3. **Long-term Solution**
- **EODHD Integration**: Valódi spot prices commodities-hez
- **IMF Integration**: Emerging market currencies-hez
- **Hybrid Approach**: FRED + EODHD + IMF kombináció

---

## 📋 **MCP INTEGRATION IMPACT**

### ✅ **MCP-ben garantálható**
- Oil (WTI, Brent) - valódi spot prices
- Major FX pairs (EUR/USD, GBP/USD, JPY/USD, stb.) - valódi spot rates
- Fed Policy Rates - valódi policy rates

### ⚠️ **MCP-ben korlátozottan elérhető**
- Gold/Silver - csak indexek, nem spot prices
- Emerging FX - csak monthly averages, nem spot rates
- Agricultural commodities - csak specific grades, nem spot prices

### ❌ **MCP-ben nem elérhető**
- Platinum, Palladium
- Wheat, Corn, Soybeans
- BRL/USD, INR/USD
- Gasoline, Heating Oil

---

## 🔧 **IMPLEMENTATION PLAN**

### Phase 1: Fix Current Issues
1. Remove misleading fallbacks
2. Add data type indicators to responses
3. Update documentation

### Phase 2: Enhanced Fallback Strategy
1. Implement type-aware fallbacks
2. Add data quality indicators
3. User education materials

### Phase 3: External Data Integration
1. EODHD integration for commodities
2. IMF integration for emerging currencies
3. Hybrid data source management

---

*Utolsó frissítés: 2025-09-15*
*Verzió: 1.0*

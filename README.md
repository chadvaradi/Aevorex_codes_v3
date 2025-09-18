# Aevorex Local v3

## Áttekintés

Aevorex egy prémium szintű equity research platform, amely ötvözi a trading platform mélységét (pl. TradingView) és az LLM-oldalak intuitív párbeszéd-élményét (pl. Perplexity, Grok).

## 🚀 ÚJ: MCP-Ready API

**Multi-Channel Platform (MCP) kompatibilis** - teljes ChatGPT és Cursor integráció támogatás!

### MCP Főbb jellemzők

- **✅ MCP Manifest**: `/.well-known/ai-plugin.json` és `/.well-known/openapi.yaml`
- **✅ Standardizált válaszok**: Minden endpoint MCP-ready formátumban (`status`, `meta`, `data`)
- **✅ Cache integráció**: Redis-alapú intelligens cache kezelés
- **✅ Error handling**: Strukturált hibaüzenetek MCP-kompatibilis formátumban
- **✅ Provider metadata**: Részletes meta információk minden válaszban

## Főbb jellemzők

- **FinanceHub modul**: Professzionális equity research élmény
- **AI-powered elemzés**: Valós időben frissülő AI-sztrukturált insightok
- **TradingView integráció**: Advanced charting funkcionalitás
- **Moduláris architektúra**: Backend (FastAPI) és Frontend (Next.js) szétválasztás
- **MCP Integration**: Teljes ChatGPT és Cursor kompatibilitás

## Projekt struktúra

```
Aevorex_local_v3/
├── aevorex-backend/          # Backend API (FastAPI)
│   ├── api/                  # API endpoints
│   ├── financehub-legacy/    # FinanceHub modul backend (MCP-ready)
│   │   ├── backend/          # FastAPI backend
│   │   │   ├── api/endpoints/ # MCP-ready endpoints
│   │   │   │   ├── eodhd/     # EODHD API (Stock, Crypto, Forex, Technical, News)
│   │   │   │   ├── fundamentals/ # Yahoo Finance fundamentals
│   │   │   │   ├── macro/     # FRED, ECB, MNB, EMMI APIs
│   │   │   │   ├── search/    # Symbol search
│   │   │   │   └── well_known/ # MCP manifest endpoints
│   │   │   ├── middleware/    # JWT auth, CORS
│   │   │   └── shared/        # Response builders, cache
│   │   ├── mcp/              # MCP specifications
│   │   │   └── specs/        # OpenAPI YAML files
│   │   └── .well-known/      # MCP manifest files
│   └── main.py              # Backend entry point
├── aevorex-frontend/         # Frontend (Next.js)
│   ├── app/                 # Next.js app directory
│   ├── lib/                 # Utility functions
│   └── public/              # Static assets
└── archive/                 # Archív kódok
```

## Telepítés és futtatás

### Backend (localhost:8084) - MCP-Ready
```bash
cd aevorex-backend/financehub-legacy
pip install -r requirements.txt
python3 -m backend.main --host 0.0.0.0 --port 8084
```

### Frontend (localhost:8083)
```bash
cd aevorex-frontend
npm install
npm run dev
```

## 🔗 MCP Integráció

### ChatGPT Desktop App
1. **MCP konfiguráció létrehozása:**
```bash
# MCP config fájl létrehozása
mkdir -p ~/Library/Application\ Support/com.openai.chat/
cp ~/.cursor/mcp.json ~/Library/Application\ Support/com.openai.chat/mcp.json
```

2. **ChatGPT-ben használat:**
   - A ChatGPT automatikusan felismeri a FinanceHub MCP szervert
   - Használhatod a `/api/v1/` endpointokat közvetlenül

### Cursor IDE
1. **MCP konfiguráció:** `~/.cursor/mcp.json` már beállítva
2. **Automatikus integráció:** Cursor automatikusan felismeri a FinanceHub szervert

### MCP Manifest Endpoints
```bash
# MCP manifest ellenőrzése
curl http://localhost:8084/.well-known/ai-plugin.json
curl http://localhost:8084/.well-known/openapi.yaml
curl http://localhost:8084/.well-known/health
```

## FinanceHub modul

A FinanceHub modul a következő főbb komponenseket tartalmazza:

1. **Ticker-szalag**: Kattintható elemek, amelyek `GET /api/v1/stock/{ticker}` endpoint-ot hívnak
2. **Elemző buborék-rács**: Négy fix buborék (Company Overview, Financial Metrics, Technical Analysis, News Highlights)
3. **TradingView Advanced Chart**: Integrált charting megoldás
4. **AI Summary Chat**: Tokenenként streamelt AI-válaszok

## 📊 API Endpoints (MCP-Ready)

### EODHD Endpoints
- **Stock**: `/api/v1/eodhd/stock/{symbol}` - Részvény adatok
- **Crypto**: `/api/v1/eodhd/crypto/{symbol}` - Kripto adatok  
- **Forex**: `/api/v1/eodhd/forex/{pair}` - Forex párok
- **Technical**: `/api/v1/eodhd/indicators/{symbol}` - Technikai mutatók
- **News**: `/api/v1/eodhd/news/{symbol}` - Hírek
- **Screener**: `/api/v1/eodhd/screener` - Részvény szűrő

### Fundamentals Endpoints  
- **Overview**: `/api/v1/fundamentals/overview/{symbol}` - Cég áttekintés
- **Ratios**: `/api/v1/fundamentals/ratios/{symbol}` - Pénzügyi mutatók
- **Earnings**: `/api/v1/fundamentals/earnings/{symbol}` - Eredmények

### Macro Endpoints
- **FED**: `/api/v1/macro/fed/series/{series_id}` - FED adatok
- **ECB**: `/api/v1/macro/ecb/series/{series_id}` - ECB adatok
- **MNB**: `/api/v1/macro/mnb/series/{series_id}` - MNB adatok

### Search & MCP
- **Search**: `/api/v1/search/{query}` - Szimbólum keresés
- **MCP Manifest**: `/.well-known/ai-plugin.json` - ChatGPT integráció

## Technológiai stack

- **Backend**: FastAPI, Python 3.13, MCP Protocol
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **AI**: OpenAI GPT-4-turbo, Gemini Pro
- **Adatforrások**: EODHD, Yahoo Finance, FRED, ECB, MNB, EMMI
- **Cache**: Redis (intelligens cache kezelés)
- **Database**: PostgreSQL (Supabase)
- **MCP**: Multi-Channel Platform integráció

## Fejlesztési irányelvek

### Prémium UX & Performance
- **60 fps animációk**: `requestAnimationFrame` optimalizált animációk
- **Skeleton-loader**: < 200ms shimmer effekt
- **Dark/light téma**: Konzisztens stílus tokenek
- **Mobil-breakpoint**: < 768px teljes funkcionalitás

### MCP-Ready Architektúra
- **Standardizált válaszok**: Minden endpoint `status`, `meta`, `data` formátumban
- **Cache integráció**: Redis-alapú intelligens cache kezelés
- **Error handling**: Strukturált hibaüzenetek MCP-kompatibilis formátumban
- **Provider metadata**: Részletes meta információk minden válaszban

### Moduláris felépítés
- **Komponens limit**: ≤ 160 sor, szétbontás `*.view.tsx` és `*.logic.ts` fájlokra
- **Adat-fedés vizsgálata**: Minden új backend-mező 72 órán belül propagálódik a frontend-be
- **Verseny-differenciátor**: Olyan insightokat ad, amit a Bloomberg/Perplexity/IBKR sem kínál

### MCP Integration Standards
- **Manifest compliance**: `/.well-known/` endpointok ChatGPT standard szerint
- **OpenAPI spec**: Teljes OpenAPI 3.0 specifikáció minden modulhoz
- **Response consistency**: Egységes meta struktúra minden endpointnál

## 🧪 Gyors tesztelés

### MCP Manifest ellenőrzése
```bash
# Manifest fájlok
curl http://localhost:8084/.well-known/ai-plugin.json | jq
curl http://localhost:8084/.well-known/openapi.yaml

# Health check
curl http://localhost:8084/.well-known/health
```

### API Endpoint tesztelés
```bash
# EODHD Stock
curl "http://localhost:8084/api/v1/eodhd/stock/AAPL" | jq '.meta'

# Fundamentals
curl "http://localhost:8084/api/v1/fundamentals/overview/AAPL" | jq '.meta'

# Macro (FED)
curl "http://localhost:8084/api/v1/macro/fed/series/DFF" | jq '.meta'
```

### MCP Response formátum ellenőrzése
```bash
# Minden válasz tartalmazza: status, meta, data
curl "http://localhost:8084/api/v1/eodhd/stock/AAPL" | jq 'keys'
# Várható: ["status", "meta", "data"]

# Meta struktúra ellenőrzése
curl "http://localhost:8084/api/v1/eodhd/stock/AAPL" | jq '.meta | keys'
# Várható: ["provider", "mcp_ready", "data_type", "cache_status", "last_updated", ...]
```

## Licenc

Privát projekt - Aevorex


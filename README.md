# Aevorex Local v3

## Áttekintés

Aevorex egy prémium szintű equity research platform, amely ötvözi a trading platform mélységét (pl. TradingView) és az LLM-oldalak intuitív párbeszéd-élményét (pl. Perplexity, Grok).

## Főbb jellemzők

- **FinanceHub modul**: Professzionális equity research élmény
- **AI-powered elemzés**: Valós időben frissülő AI-sztrukturált insightok
- **TradingView integráció**: Advanced charting funkcionalitás
- **Moduláris architektúra**: Backend (FastAPI) és Frontend (Next.js) szétválasztás

## Projekt struktúra

```
Aevorex_local_v3/
├── aevorex-backend/          # Backend API (FastAPI)
│   ├── api/                  # API endpoints
│   ├── financehub-legacy/    # FinanceHub modul backend
│   └── main.py              # Backend entry point
├── aevorex-frontend/         # Frontend (Next.js)
│   ├── app/                 # Next.js app directory
│   ├── lib/                 # Utility functions
│   └── public/              # Static assets
└── archive/                 # Archív kódok
```

## Telepítés és futtatás

### Backend (localhost:8084)
```bash
cd aevorex-backend
pip install -r requirements.txt
python main.py
```

### Frontend (localhost:8083)
```bash
cd aevorex-frontend
npm install
npm run dev
```

## FinanceHub modul

A FinanceHub modul a következő főbb komponenseket tartalmazza:

1. **Ticker-szalag**: Kattintható elemek, amelyek `GET /api/v1/stock/{ticker}` endpoint-ot hívnak
2. **Elemző buborék-rács**: Négy fix buborék (Company Overview, Financial Metrics, Technical Analysis, News Highlights)
3. **TradingView Advanced Chart**: Integrált charting megoldás
4. **AI Summary Chat**: Tokenenként streamelt AI-válaszok

## Technológiai stack

- **Backend**: FastAPI, Python 3.13
- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **AI**: OpenAI GPT-4-turbo, Gemini Pro
- **Adatforrások**: EODHD, Alpha Vantage, FRED, ECB
- **Cache**: Redis
- **Database**: PostgreSQL (Supabase)

## Fejlesztési irányelvek

- Prémium UX minősítések: 60 fps animációk, skeleton-loader < 200ms
- Moduláris felépítés: komponens ≤ 160 sor, szétbontás `*.view.tsx` és `*.logic.ts` fájlokra
- Adat-fedés vizsgálata: minden új backend-mező 72 órán belül propagálódik a frontend-be
- Verseny-differenciátor: olyan insightokat ad, amit a Bloomberg/Perplexity/IBKR sem kínál

## Licenc

Privát projekt - Aevorex

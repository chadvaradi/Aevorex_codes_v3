# Backend – Mappastruktúra és Adatforrás-irányelvek (v1)

Ez a dokumentum röviden elmagyarázza a `backend/` könyvtár elemeit **és** rögzíti,
hogy az egyes API-csoportok mely adatforrásokra támaszkodnak (elsődleges / tartalék).

> Megjegyzés: a környezeti változók és kulcsok ebben a verzióban szándékosan NINCSENEK dokumentálva.

---

## 1) Mappastruktúra – mit hova tegyünk?

backend/
ai/                # LLM-pipeline-ok (report, összefoglaló, scoring), promtok és AI-szervizek
pipelines/
prompts/
services/

api/               # Külső interfész (FastAPI/Router-ek)
admin/
auth/
integrations/
ibkr/
auth/
config/
market_data/
trading/
utils/
macro/
market/
news/
subscription/

core/              # Közös keretréteg
cache/
db/
sql/
http/
logging/
security/
settings/

data/              # Adatforrás-kliensek (SDK/wrapper) és adapterek
eodhd/
fmp/
macro/
ecb/
fred/
marketaux/
newsapi/
yfinance/

docs/              # Belső dokumentáció
infra/             # Deploy/ops
cloudflare/
docker/
monitoring/
grafana/
dashboards/
provisioning/
ngrok/

middleware/
jwt_auth/

models/            # Pydantic/ORM modellek
scripts/           # Seed/migráció/egyszeri hasznos scriptek
services/          # Domain-szervizek (üzleti logika)
notifications/
reporting/
subscriptions/
tradingview/

tests/
integrations/

utils/

---

## 2) Adatforrás-mátrix (prioritás + tartalék)

### 2.1. **EODHD – All World Extended (29.99 $/hó)**
**Quota (user visszajelzése alapján):** ~100 000 hívás/nap, 1000/perc, ~500 welcome bonus, ~30+ év történet.

**Funkciók, amelyeket használunk / használhatunk:**
- **Részvény/ETF/Fund árfolyamok:** End-of-Day + **Intraday** (OHLCV).
- **Live (késleltetett) árfolyamok:** stocks ~15 perc, **FX/Crypto ~1 perc**.
- **Technikai API:** indikátorok, moving average-ek stb.
- **Screener API** és **Search API**.
- **US Ticks / Real-time websockets** (első körben **nem** használjuk, később opció).
- **Exchanges meta:** támogatott tőzsdék listája, tickerek, kereskedési órák.
- **Economic Events / Macroeconomic Data** (ha a csomagodban engedélyezett).
- **Financial News Feed API** (használható a hírcsatornához – lásd 2.4).
- **Logók (~40k)**.

> **Fontos:** A **Fundamentals** (mérleg, P&L, cash-flow, multiples stb.) **külön „Fundamentals Data Feed” csomag** (59.99 $/hó) – **nem** része a 29.99 $-os All World Extended-nek.

**Mappa-hozzárendelés:**
- `data/eodhd/` – HTTP kliens(ek), endpoint-wrapper(ek), rate-limit guard.
- `api/market/` – piaci adatok és technikai végpontok EODHD-ről.
- `api/news/` – hírek esetén EODHD News Feed is támogatott forrás.
- `api/macro/` – ha EODHD makró/eco engedélyezett, itt is elérhető adapterrel.

---

### 2.2. **FMP** (tartalék/alternatíva – különösen Fundamentals)
- **Elsődleges forrás a Fundamentals-hoz**, mivel EODHD Fundamentals nincs előfizetve.
- Használható: vállalati mutatók, EPS előrejelzés, target price modulok (ha a te FMP csomagod engedi).
- `data/fmp/` és `api/market/` fundamentals-alvégpontjai.

### 2.3. **YFinance** (freemium, tartalék)
- Árfolyam és intraday adatok **backupként** (ratelimit/fedés esetén).
- `data/yfinance/` – egyszerű wrapper; csak fallbackként hívjuk.

### 2.4. **Hírek**
- **Elsődleges:** EODHD **Financial News Feed API** *(mivel a csomagodban elérhető – user infó)*.
- **Tartalék / kiegészítés:** **Marketaux** (freemium).
- **Dedup & rankelés:** cím+forrás hash, időbélyeg szerinti rendezés, opcionális AI összefoglaló.
- `data/eodhd/` és/vagy `data/marketaux/` + `api/news/`.

### 2.5. **Makró**
- **ECB / FRED** a fő forrás (stabil, ingyenes).
- EODHD „Economic/Macro” modulok csak **kiegészítő** szerepben (ha csomag engedi).
- `data/macro/ecb/`, `data/macro/fred/` + `api/macro/`.

### 2.6. **IBKR**
- Kereskedési **integráció** (paper/live): auth, market_data, trading.
- Nem elsődleges adatforrás árfolyamokra; cél: order flow és számla-információ.
- `api/integrations/ibkr/`.

---

## 3) Végpontok – forrásprioritások

**Market árfolyam / gyertyák (OHLCV):**  
1) EODHD (EOD + Intraday), 2) YFinance (fallback)

**Technikai indikátorok:**  
1) EODHD Technical API, 2) (opcionális) lokális számítás később

**Screener / Search:**  
1) EODHD Screener/Search

**Hírek:**  
1) EODHD News Feed, 2) Marketaux (merge + dedupe)

**Fundamentals (P&L, BS, CF, ratios):**  
1) **FMP** (elsődleges), 2) (később) EODHD Fundamentals, ha előfizetsz

**Makró (kamatok, hozamgörbe, infláció, FX policy):**  
1) ECB/FRED (elsődleges), 2) EODHD macro/eco (ha kell kiegészítés)

**Tőzsdei meta (exchanges, órák, ticker listák):**  
1) EODHD Exchanges API

---

## 4) Könyvtárszintű feladatleírás (rövid)

- `ai/pipelines/` – AI-riportok (pl. napi/ heti összefoglaló), piaci & makró inputok összeállítása.
- `ai/prompts/` – sablonok a különböző pipeline-okhoz (news digest, earnings recap stb.).
- `ai/services/` – OpenRouter-hívások, tokenőrzés, aszink feldolgozás.

- `api/market/` – gyertyák, árak, technikai indikátorok, screener/search végpontok.
- `api/news/` – hírek (EODHD/Marketaux), összefoglaló, kategorizálás.
- `api/macro/` – ECB/FRED adatlekérések (yield curve, policy rates, infláció).
- `api/subscription/` – Lemon Squeezy webhook/billing státusz-ellenőrzés.
- `api/integrations/ibkr/` – auth, order, positions, executions, market_data (IBKR API).

- `core/http/` – közös HTTP kliens (retry, backoff, **per-source throttle**; pl. EODHD 1000/min).
- `core/cache/` – Redis cache (pl. intraday/technicals rövid TTL).
- `core/logging/` – strukturált logok, request-id.
- `core/security/` – JWT, OAuth.
- `core/settings/` – globális app-konfig (feature flag-ekkel).

- `data/*` – **forrásspecifikus** adapterek (EODHD/FMP/YF/Marketaux/NewsAPI/ECB/FRED).
- `services/reporting/` – AI által generált PDF/HTML riportok összerakása.
- `services/subscriptions/` – LS API-k, licenc státusz lekérdezés.
- `services/notifications/` – email/SNS/SES értesítések.
- `services/tradingview/` – widget integráció, esetleges 3rd party tv-data proxy.

---

## 5) Rate limit & cache elv (rövid)

- **EODHD:** 1000/perc – kliensoldali bucket limiter + rövid TTL cache intraday hívásokra.  
- **Fallback stratégia:** hibára/limitre YFinance, híreknél Marketaux merge.  
- **Dedup:** hírek és ticker-meta: `(source, title|id, published_at)` hash.

---

## 6) Tesztelés

- `tests/integrations/` – smoke: EODHD OHLCV, Technical, News; FMP fundamentals; ECB yield curve.
- Minimal end-to-end: `api/market/candles` → `ai/pipelines/daily-digest` bemenet.

---

## 7) Teendők (MVP)

1. `data/eodhd/` kliens + limiter + alap endpointok (EOD, Intraday, Technical, Search).  
2. `api/market/` és `api/news/` alap routerek EODHD-vel.  
3. `data/fmp/` Fundamentals kliens + `api/market/fundamentals`.  
4. `data/macro/ecb|fred/` + `api/macro/` (yield curve, policy rates).  
5. Hírek dedup + AI-s összefoglaló pipeline (opcionális első körben).  

> EODHD „Economic/Macro/Financial Events/Logók” és „US Ticks/Websocket” modulok opcionálisak – később kapcsoljuk be, ha kell.


# Chat Endpoints

**Category:** Chat  
**Total Endpoints:** 4  
**Authentication:** Not required  
**Caching:** Based on context (varies)

This category provides AI-powered financial analysis through chat interfaces. The chat system can access any data source (fundamentals, technical, news, macro, crypto, forex, **trading hours**) based on the provided context.

---

## 1. GET /api/v1/chat/health

**Description:** Chat service health check endpoint.

**Parameters:** None

**Response:**
```json
{
  "status": "ok",
  "service": "chat",
  "timestamp": "2024-01-15T10:30:00Z",
  "models_available": 3,
  "active_sessions": 42
}
```

**Response Fields:**
- `status` (string): Service status ("ok", "degraded", "error")
- `service` (string): Service identifier
- `timestamp` (string): Current server time
- `models_available` (integer): Number of available AI models
- `active_sessions` (integer): Current active chat sessions

**Behavior:**
- No authentication required
- No caching
- Returns 200 OK when chat service is healthy

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/chat/health
```

---

## 2. GET /api/v1/chat/models

**Description:** Returns list of available AI models for chat functionality.

**Parameters:** None

**Response:**
```json
{
  "models": {
    "deepseek-free": "deepseek/deepseek-chat-v3.1:free",
    "gemini-2.0-flash": "google/gemini-2.0-flash-001"
  },
  "default": "deepseek-free"
}
```

**Response Fields:**
- `models` (object): Available model aliases and their full model IDs
- `default` (string): Default model alias to use when none specified

**Behavior:**
- No authentication required
- Cached for 1 hour
- Returns available models with pricing and capabilities

**Usage:**
```bash
curl https://api.aevorex.com/api/v1/chat/models
```

---

## 3. POST /api/v1/chat/rapid

**Description:** Rapid chat response with access to any data source. Provides quick, concise answers with real-time financial data.

**Parameters:**
- **Body:**
  - `messages` (array, required): Array of chat messages
  - `context` (object, optional): Context configuration
  - `model` (string, optional, default: "gpt-4o-mini"): AI model to use

**Request Body Structure:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What's the current BUBOR 3M rate and how does it compare to last month?"
    }
  ],
  "context": {
    "ticker": "HUF",
    "data_sources": ["macro", "fundamentals"]
  },
  "model": "gpt-4o-mini"
}
```

**Context Object:**
- `ticker` (string, optional): Financial instrument symbol
- `data_sources` (array, optional): Available data sources
  - `"fundamentals"`: Company financial data
  - `"technical"`: Technical indicators
  - `"news"`: Financial news
  - `"macro"`: Macroeconomic data
  - `"crypto"`: Cryptocurrency data
  - `"forex"`: Foreign exchange data

**Response:**
```json
{
  "id": "chatcmpl-1757891493",
  "object": "chat.completion",
  "created": 1757891493,
  "model": "gemini-2.0-flash",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Sajnálom, de nincs hozzáférésem az aktuális árfolyamokhoz valós időben. Az árfolyamok folyamatosan változnak. Használja az alábbiakat az aktuális információk beszerzéséhez:\n*   **Pénzügyi weboldalak:** Nézzen utána olyan megbízható pénzügyi weboldalakon, mint a Google Finance, Yahoo Finance, vagy Bloomberg."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 56,
    "completion_tokens": 93,
    "total_tokens": 149,
    "prompt_tokens_details": {
      "cached_tokens": 0
    },
    "completion_tokens_details": {
      "reasoning_tokens": 0,
      "image_tokens": 0
    }
  }
}
```

**Response Fields:**
- `id` (string): Unique response identifier
- `object` (string): Response type ("chat.completion")
- `created` (integer): Unix timestamp of response creation
- `model` (string): Model used for generation
- `choices` (array): Array of response choices
  - `index` (integer): Choice index
  - `message` (object): Response message
    - `role` (string): Message role ("assistant")
    - `content` (string): AI-generated response content
  - `finish_reason` (string): Reason for completion ("stop")
- `usage` (object): Token usage statistics
  - `prompt_tokens` (integer): Input tokens used
  - `completion_tokens` (integer): Output tokens generated
  - `total_tokens` (integer): Total tokens used
  - `prompt_tokens_details` (object): Detailed prompt token info
  - `completion_tokens_details` (object): Detailed completion token info

**Behavior:**
- No authentication required
- Cached based on context and message content
- Response time typically 2-5 seconds
- Access to real-time financial data

**Usage:**
```bash
curl -X POST https://api.aevorex.com/api/v1/chat/rapid \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Analyze AAPL stock performance"}
    ],
    "context": {
      "ticker": "AAPL",
      "data_sources": ["fundamentals", "technical", "news"]
    },
    "model": "gpt-4o-mini"
  }'
```

---

## 4. POST /api/v1/chat/deep

**Description:** Deep analysis chat response with access to any data source. Provides comprehensive, detailed analysis with streaming response capability.

**Parameters:**
- **Body:**
  - `messages` (array, required): Array of chat messages
  - `context` (object, optional): Context configuration
  - `model` (string, optional, default: "gpt-4o-mini"): AI model to use

**Request Body Structure:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Provide a comprehensive analysis of Apple Inc. including financial health, market position, and investment outlook"
    }
  ],
  "context": {
    "ticker": "AAPL",
    "data_sources": ["fundamentals", "technical", "news", "macro"]
  },
  "model": "gpt-4o"
}
```

**Response (Streaming):**
```
data: {"content": "R"}

data: {"content": "endben, itt egy mélyreható elemzés a Tesla (TSLA"}

data: {"content": ") részvényről, melynek célja, hogy több szempontból is"}

data: {"content": " átfogó képet adjon a helyzetről:\n\n**Rövid összefoglaló**\n\nA Tesla egy ambiciózus cég,"}

data: {"content": " amely az elektromos járművek (EV) piacának vezető szereplőjévé vált, és emellett energiatárolással, napelemgy"}

data: {"content": "ártással és mesterséges intelligenciával is foglalkozik. A cég innovatív technológiái és a márkaimázsa jelentős piaci részesedést és magas értékelést eredményezett. Az"}

data: {"content": "onban a növekedési ütem lassulása, a verseny erősödése és a makrogazdasági tényezők jelentős kihívásokat jelentenek.\n\n**1. Technikai elemzés**\n\n*   **"}

data: {"content": "Jelenlegi árfolyam:** A TSLA jelenlegi árfolyama [aktuális árfolyam adat] körül mozog.\n*   **Trendek:**\n    *   Rövid távú: Az elmúlt hónapokban volatilis mozgás volt jellemző, de egyelőre nincs"}

data: {"content": " egyértelmű trend.\n    *   Hosszú távú: A hosszú távú trend továbbra is emelkedőnek tekinthető, de a korábbi meredekség mérséklődött.\n*   **Támasz és ellenállás szintek:**\n    *"}

data: {"content": "   Támasz: Fontos támaszszintek találhatók [konkrét árfolyam szint] és [konkrét árfolyam szint] körül. Ha ezek a szintek elesnek, további esés várható.\n    *   Ellenállás: Ellenállás várható [konkrét"}

data: {"content": " árfolyam szint] és [konkrét árfolyam szint] körül. Ezen szintek áttörése további emelkedést vetíthet előre.\n*   **Technikai indikátorok:**\n    *   Mozgóátlagok: Az 50 napos mozgóátlag"}

data: {"content": " gyakran a 200 napos mozgóátlag alatt van, ami medvés jelet mutat.\n    *   RSI (Relative Strength Index): Az RSI [aktuális RSI érték]. Az 50 alatti érték túlértékesítettséget jelezhet"}

data: {"content": ", míg a 70 feletti érték túlvételt.\n    *   MACD (Moving Average Convergence Divergence): A MACD vonalak keresztezése vételi vagy eladási jeleket adhat.\n*   **Összefoglaló:** A technikai kép"}

data: {"content": " vegyes. Rövid távon további volatilitás várható, míg hosszú távon az emelkedő trend továbbra is fennáll, de a lendület gyengült.\n\n**2. Fundamentális elemzés**\n\n*   **Bevétel és nyereség:** A Tesla be"}

data: {"content": "vétele az elmúlt években jelentősen nőtt, de a növekedési ütem lassul. A nyereségesség javult, de továbbra is függ az autóeladásoktól és az adókedvezményektől.\n*   **Piacrészesedés:**"}

data: {"content": " A Tesla továbbra is vezető szerepet tölt be az elektromos járművek piacán, de a verseny egyre élesebb. A hagyományos autógyártók is egyre több elektromos modellt dobnak piacra.\n*   **Verseny:** A Tesla versenytársai"}

data: {"content": " közé tartozik a BYD, a Volkswagen, a General Motors, a Ford és a Rivian. A verseny erősödése nyomást gyakorolhat a Tesla árrésére és piaci részesedésére.\n*   **Értékelés:** A Tesla P/E (árfolyam/nyeres"}

data: {"content": "ég) mutatója magas a hagyományos autógyártókhoz képest, ami azt jelzi, hogy a befektetők magas növekedési várakozásokat támasztanak a céggel szemben. A P/S (árfolyam/bevétel) mutató szintén magas."}

data: {"content": "\n*   **Adósság:** A Tesla adósságszintje csökkent az elmúlt években, ami pozitív jel.\n*   **Vezetés:** Elon Musk vezetése innovatív, de gyakran kiszámíthatatlan. A vezetéssel kapcsolatos"}

data: {"content": " kockázatok mindig jelen vannak.\n*   **Növekedési lehetőségek:**\n    *   Új modellek: A Cybertruck és más új modellek bevezetése segíthet a növekedés fenntartásában.\n    *   Energiatárolás és napelemek:"}

data: {"content": " Az energiatárolási és napelem üzletágak jelentős növekedési potenciállal rendelkeznek.\n    *   Nemzetközi terjeszkedés: A Tesla terjeszkedése Kínában és más feltörekvő piacokon szintén hozzájárulhat a növeked"}

data: {"content": "éshez.\n*   **Kockázatok:**\n    *   Termelési problémák: A Tesla korábban többször is szembesült termelési problémákkal, amelyek negatívan befolyásolhatják a bevételeket.\n    *   Akk"}

data: {"content": "umulátor-ellátási problémák: Az akkumulátorok ellátása kritikus fontosságú a Tesla számára. Az ellátási lánc zavarai befolyásolhatják a termelést.\n    *   Szabályozási kockázatok: A kormányzati szabályozások"}

data: {"content": " és az adókedvezmények változásai befolyásolhatják a Tesla eredményeit.\n*   **Összefoglaló:** A Tesla fundamentumai erősek, de a magas értékelés és a növekvő verseny kockázatot jelent.\n\n**3. Pi"}

data: {"content": "aci hangulat**\n\n*   **Befektetői hangulat:** A befektetői hangulat vegyes. Egyes befektetők továbbra is optimisták a Tesla jövőjével kapcsolatban, míg mások aggódnak a növekedési ütem lassulása"}

data: {"content": " és a verseny miatt. A közösségi média és a hírek nagyban befolyásolják a piaci hangulatot.\n*   **Elemzői vélemények:** Az elemzői vélemények megoszlanak. Egyes elemzők vételi ajánlást adnak a Tesla rés"}

data: {"content": "zvényére, míg mások tartást vagy eladást javasolnak.\n*   **Short interest:** A short interest (short pozíciók aránya) viszonylag magas, ami azt jelzi, hogy sok befektető számít az árfolyam esésére.\n\n"}

data: {"content": "**4. Kockázatértékelés**\n\n*   **Piaci kockázat:** Az elektromos járművek piaca gyorsan változik, és a Tesla piaci részesedése csökkenhet a verseny erősödésével.\n*   **Végrehajtási kock"}

data: {"content": "ázat:** A Tesla-nak sikeresen végre kell hajtania a növekedési terveit, beleértve az új modellek bevezetését és a termelés felfuttatását.\n*   **Technológiai kockázat:** A Tesla innovatív technológiái versenyelő"}

data: {"content": "nyt biztosítanak, de fennáll a kockázat, hogy más cégek jobb technológiákat fejlesztenek ki.\n*   **Szabályozási kockázat:** A kormányzati szabályozások és az adókedvezmények változásai befolyásolhatják a Tesla eredm"}

data: {"content": "ényeit.\n*   **Makrogazdasági kockázat:** A gazdasági lassulás és a magas kamatlábak csökkenthetik az autóeladásokat és a befektetéseket.\n\n**5. Befektetési ajánlások**\n\nTekintettel a fenti elemzésre"}

data: {"content": ", a következő forgatókönyvek valószínűek:\n\n*   **Befektetési időtáv:** A befektetési döntés nagymértékben függ a befektetési időtávtól és a kockázattűrő képességtől.\n*   **R"}

data: {"content": "övid távú befektetők:** A rövid távú befektetők számára a Tesla részvénye magas kockázatot jelent, mivel az árfolyam volatilis és a piaci hangulat gyorsan változhat.\n*   **Hosszú távú befektetők:**"}

data: {"content": " A hosszú távú befektetők számára a Tesla részvénye továbbra is vonzó lehet, ha hisznek a cég jövőbeli növekedésében és innovációs képességében. Ugyanakkor a magas értékelés és a verseny erősödése miatt érdemes ó"}

data: {"content": "vatosnak lenni.\n*   **Lehetséges stratégiák:**\n    *   Vétel: Ha hiszel a Tesla hosszú távú növekedésében, akkor vételi pozíciót vehetsz fel, de érdemes diverzifikálni a portfóli"}

data: {"content": "ódát és figyelembe venni a kockázatokat.\n    *   Tartás: Ha már rendelkezel Tesla részvényekkel, akkor érdemes tartani a pozíciódat, de figyelni a piaci fejleményeket és a cég teljesítményét.\n    *"}

data: {"content": "   Eladás: Ha aggódsz a növekedési ütem lassulása, a verseny erősödése vagy a magas értékelés miatt, akkor érdemes eladni a részvényeidet.\n*   **Fontos megjegyzés:** Ez az elemzés tájékoztató"}

data: {"content": " jellegű, és nem minősül befektetési tanácsadásnak. Minden befektetési döntés előtt konzultálj egy képzett pénzügyi tanácsadóval, és vedd figyelembe a saját egyéni körülményeidet.\n\n**Követ"}

data: {"content": "keztetés**\n\nA Tesla egy izgalmas cég, amely jelentős hatást gyakorolt az autóiparra és az energiapiacra. A cég jövője azonban tele van kihívásokkal és lehetőségekkel. A befektetőknek alaposan mérlegelniük kell"}

data: {"content": " a kockázatokat és a potenciális hozamokat, mielőtt befektetési döntést hoznak.\n\nRemélem, ez a részletes elemzés segít jobban megérteni a Tesla helyzetét! Ha további kérdéseid vannak, nyugodtan tedd fel!\n"}

data: {"content": ""}

data: [DONE]
```

**Response Types:**
- `content`: Streaming content chunks with actual response text
- `[DONE]`: Analysis finished

**Behavior:**
- No authentication required
- Cached based on context and message content
- Streaming response for real-time content delivery
- Response time typically 10-30 seconds
- Access to comprehensive financial data
- Pro+ subscription recommended for optimal performance

**Usage:**
```bash
curl -X POST https://api.aevorex.com/api/v1/chat/deep \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Deep analysis of AAPL stock"}
    ],
    "context": {
      "ticker": "AAPL",
      "data_sources": ["fundamentals", "technical", "news", "macro"]
    },
    "model": "gpt-4o"
  }'
```

---

## Chat Features

### **Data Source Integration**
- **Fundamentals**: Company financials, ratios, earnings
- **Technical**: Price charts, indicators, patterns
- **News**: Latest financial news and sentiment
- **Macro**: Economic indicators, central bank rates
- **Crypto**: Cryptocurrency prices and analysis
- **Forex**: Foreign exchange rates and trends

### **Model Selection**
- **gpt-4o-mini**: Fast, cost-effective for simple queries
- **gpt-4o**: Balanced performance for most use cases
- **claude-3-5-sonnet**: Advanced reasoning for complex analysis

### **Response Types**
- **Rapid**: Quick answers (2-5 seconds)
- **Deep**: Comprehensive analysis (10-30 seconds, streaming)

### **Caching Strategy**
- Responses cached based on message content and context
- Cache duration varies by data source freshness
- Real-time data always fetched fresh

---

## Best Practices

### **Context Configuration**
```json
{
  "context": {
    "ticker": "AAPL",
    "data_sources": ["fundamentals", "technical", "news"]
  }
}
```

### **Message Structure**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Clear, specific question about financial data"
    }
  ]
}
```

### **Error Handling**
- **400**: Invalid request format
- **429**: Rate limit exceeded
- **500**: Service temporarily unavailable

---

**Total Chat Endpoints: 4** ✅


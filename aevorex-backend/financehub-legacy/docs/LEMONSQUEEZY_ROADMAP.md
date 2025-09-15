# 🛣️ LemonSqueezy Integration Roadmap - 4 Lépéses Terv

## 🎯 **Cél: Production-Ready LemonSqueezy Webhook Integráció**

**Jelenlegi állapot:** Webhook endpoint működik, signature validáció aktív, de DB integráció hiányos  
**Célállapot:** Teljes funkcionális subscription management rendszer

---

## 📋 **4 Lépéses Roadmap**

### **1. 🔧 Subscription Model Fix**
**Időtartam:** 2-3 óra  
**Prioritás:** 🔴 **KRITIKUS**

#### **Feladatok:**
- [ ] **user_id mapping javítása**
  - LemonSqueezy `customer_id` → belső `user_id` konverzió
  - User lookup implementálása
  - Fallback handling hiányzó user_id esetén

- [ ] **current_period_end timestamp kezelés**
  - `renews_at` és `ends_at` mezők parsing
  - ISO 8601 dátum konverzió
  - Null értékek kezelése

- [ ] **status mapping implementálása**
  - LemonSqueezy status → belső subscription status
  - Status transition validáció
  - Enum értékek definiálása

- [ ] **Pydantic model validáció javítása**
  - Required/optional mezők tisztázása
  - Validation rules finomhangolása
  - Error messages javítása

#### **Tesztelés:**
```bash
# Subscription model validáció teszt
curl -X POST http://localhost:8084/api/v1/billing/lemonsqueezy \
  -H "X-Signature: [valid_signature]" \
  -d @subscription_created.json
# Várható: HTTP 200 + subscription mentve DB-be
```

---

### **2. 📊 Debug Logging Enhancement**
**Időtartam:** 1-2 óra  
**Prioritás:** 🟡 **KÖZEPES**

#### **Feladatok:**
- [ ] **Payload logging implementálása**
  - Teljes webhook payload naplózása
  - Sensitive data masking
  - Structured logging formátum

- [ ] **Field mapping logging**
  - Minden mező konverziója nyomon követése
  - Mapping success/failure logging
  - Data transformation audit trail

- [ ] **Validation error logging**
  - Részletes Pydantic hibaüzenetek
  - Field-level validation errors
  - Stack trace logging

- [ ] **Database operation logging**
  - CRUD műveletek nyomon követése
  - SQL query logging (dev környezetben)
  - Transaction success/failure logging

#### **Tesztelés:**
```bash
# Log output ellenőrzése
tail -f backend.log | grep "subscription"
# Várható: részletes field mapping és validation logok
```

---

### **3. 🧪 Sandbox LemonSqueezy Teszt**
**Időtartam:** 2-3 óra  
**Prioritás:** 🟡 **KÖZEPES**

#### **Feladatok:**
- [ ] **LemonSqueezy sandbox account setup**
  - Developer account létrehozása
  - Sandbox store konfigurálása
  - Webhook endpoint regisztrálása

- [ ] **Valós webhook tesztelés**
  - `subscription_created` event triggerelése
  - `subscription_updated` event tesztelése
  - `subscription_cancelled` event validálása

- [ ] **Payload validáció**
  - Valós LemonSqueezy formátum ellenőrzése
  - Field mapping tesztelése
  - Edge case kezelés (null értékek, special characters)

- [ ] **Signature validáció éles teszt**
  - Valódi LemonSqueezy signature ellenőrzése
  - HMAC validáció production környezetben
  - Security testing

#### **Tesztelés:**
```bash
# Sandbox webhook teszt
# LemonSqueezy admin panel → Webhook settings → Send test webhook
# Várható: backend logokban valós payload feldolgozás
```

---

### **4. 🗄️ Database Integration Teszt**
**Időtartam:** 3-4 óra  
**Prioritás:** 🔴 **KRITIKUS**

#### **Feladatok:**
- [ ] **Subscription CRUD műveletek**
  - Create: új subscription létrehozása
  - Read: subscription lekérdezése user_id alapján
  - Update: subscription státusz frissítése
  - Delete: subscription törlése (soft delete)

- [ ] **User-Subscription kapcsolat**
  - Foreign key integráció
  - User lookup implementálása
  - Subscription history tracking

- [ ] **Data consistency ellenőrzés**
  - Subscription state szinkronizálás
  - Duplicate prevention
  - Data integrity constraints

- [ ] **End-to-end flow tesztelés**
  - Teljes subscription lifecycle
  - Payment flow integráció
  - User permission updates

#### **Tesztelés:**
```bash
# Database integráció teszt
# 1. Webhook → subscription létrehozás
# 2. User lookup → subscription lekérdezés
# 3. Status update → subscription frissítés
# 4. End-to-end flow → teljes lifecycle
```

---

## 🎯 **Success Criteria**

### **1. Lépés Befejezése:**
- ✅ Subscription model validáció hibamentes
- ✅ user_id és current_period_end mezők helyesen kezelve
- ✅ Pydantic validation errors eltűntek

### **2. Lépés Befejezése:**
- ✅ Részletes debug logging minden művelethez
- ✅ Field mapping audit trail
- ✅ Validation error tracking

### **3. Lépés Befejezése:**
- ✅ Valós LemonSqueezy sandbox integráció
- ✅ Éles webhook események feldolgozva
- ✅ Production-ready signature validáció

### **4. Lépés Befejezése:**
- ✅ Teljes database integráció
- ✅ User-subscription kapcsolat működik
- ✅ End-to-end subscription lifecycle

---

## 📅 **Időzítés**

| Lépés | Időtartam | Prioritás | Függőség |
|-------|-----------|-----------|----------|
| 1. Subscription Model Fix | 2-3 óra | 🔴 Kritikus | - |
| 2. Debug Logging | 1-2 óra | 🟡 Közepes | 1. lépés után |
| 3. Sandbox Teszt | 2-3 óra | 🟡 Közepes | 1. lépés után |
| 4. DB Integráció | 3-4 óra | 🔴 Kritikus | 1. lépés után |

**Összes becsült idő:** 8-12 óra fejlesztés + tesztelés

---

## 🚀 **Production Ready Eredmény**

A 4 lépés elvégzése után:

- ✅ **Teljes funkcionális webhook endpoint**
- ✅ **Production-ready subscription management**
- ✅ **Valós LemonSqueezy integráció**
- ✅ **Robusztus error handling és logging**
- ✅ **End-to-end subscription lifecycle**

**Eredmény:** A billing endpoint valóban production-ready állapotban lesz! 🎯

---

**Utolsó frissítés:** 2025-01-15  
**Státusz:** Roadmap kész ✅  
**Következő lépés:** 1. Subscription Model Fix implementálása 🛠️

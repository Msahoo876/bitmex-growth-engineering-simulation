# TESTING.md

# BitMEX Growth Engineering Simulation - End-to-End Testing Guide

## Prerequisites

Backend:

```bash
uvicorn app.main:app --reload
```

Frontend:

```bash
npm run dev
```

Swagger:

```text
http://localhost:8000/api/v1/docs
```

Frontend:

```text
http://localhost:5173
```

---

# Test User Journey

We will simulate:

Landing Page
→ Signup
→ KYC Started
→ KYC Completed
→ Deposit Started
→ Deposit Completed
→ Trade Opened
→ Trade Closed

Use the same userId throughout the test.

```text
mahesh_demo_001
```

---

# Step 1 — Identify User

POST /api/v1/identify

```json
{
  "userId": "mahesh_demo_001",
  "traits": {
    "country": "India",
    "device": "Desktop",
    "source": "google",
    "campaign": "btc_launch_campaign"
  },
  "timestamp": "2026-06-02T10:00:00Z",
  "messageId": "identify_001"
}
```

Expected:

* User profile created
* User visible in analytics

---

# Step 2 — Landing Page View

POST /api/v1/page

```json
{
  "userId": "mahesh_demo_001",
  "name": "Landing Page",
  "url": "https://bitmex-demo.com",
  "title": "BitMEX Landing Page",
  "properties": {
    "source": "google"
  },
  "timestamp": "2026-06-02T10:01:00Z",
  "messageId": "page_001"
}
```

Expected:

* Landing page count increases
* Funnel entry count increases

---

# Step 3 — User Signup

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "user_signed_up",
  "properties": {
    "source": "google",
    "campaign": "btc_launch_campaign"
  },
  "timestamp": "2026-06-02T10:02:00Z",
  "messageId": "signup_001"
}
```

Expected:

* Total Users +1
* Signup Funnel +1
* Google Attribution +1

---

# Step 4 — KYC Started

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "kyc_started",
  "properties": {
    "country": "India"
  },
  "timestamp": "2026-06-02T10:03:00Z",
  "messageId": "kyc_started_001"
}
```

Expected:

* KYC Started +1

---

# Step 5 — KYC Completed

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "kyc_completed",
  "properties": {
    "verification_method": "passport"
  },
  "timestamp": "2026-06-02T10:04:00Z",
  "messageId": "kyc_completed_001"
}
```

Expected:

* KYC Completed +1

---

# Step 6 — Deposit Started

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "deposit_started",
  "properties": {
    "currency": "USDT"
  },
  "timestamp": "2026-06-02T10:05:00Z",
  "messageId": "deposit_started_001"
}
```

Expected:

* Deposit Started +1

---

# Step 7 — Deposit Completed

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "deposit_completed",
  "properties": {
    "currency": "USDT",
    "amount": 1000
  },
  "timestamp": "2026-06-02T10:06:00Z",
  "messageId": "deposit_completed_001"
}
```

Expected:

* Revenue increases
* Deposit Conversion increases

---

# Step 8 — Trade Opened

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "trade_opened",
  "properties": {
    "symbol": "BTCUSDT",
    "amount": 1000,
    "leverage": 10
  },
  "timestamp": "2026-06-02T10:07:00Z",
  "messageId": "trade_opened_001"
}
```

Expected:

* Active Traders +1
* Trade Funnel +1

---

# Step 9 — Trade Closed

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "trade_closed",
  "properties": {
    "symbol": "BTCUSDT",
    "profit": 250
  },
  "timestamp": "2026-06-02T10:08:00Z",
  "messageId": "trade_closed_001"
}
```

Expected:

* Trading Metrics Update
* Revenue Metrics Update

---

# Attribution Testing

## Telegram Campaign

POST /api/v1/track

```json
{
  "userId": "telegram_user_001",
  "event": "user_signed_up",
  "properties": {
    "source": "telegram",
    "campaign": "telegram_trader_community",
    "deep_link": "telegram://bitmex/invite"
  },
  "timestamp": "2026-06-02T11:00:00Z",
  "messageId": "telegram_signup_001"
}
```

Expected:

* Telegram Attribution increases
* Deep Link Attribution increases

---

## Referral Signup

POST /api/v1/track

```json
{
  "userId": "referral_user_001",
  "event": "user_signed_up",
  "properties": {
    "source": "referral",
    "referral_code": "TRADER100"
  },
  "timestamp": "2026-06-02T11:10:00Z",
  "messageId": "referral_signup_001"
}
```

Expected:

* Referral Attribution increases

---

# Duplicate Event Test

Submit this request twice.

POST /api/v1/track

```json
{
  "userId": "mahesh_demo_001",
  "event": "trade_opened",
  "properties": {
    "symbol": "BTCUSDT"
  },
  "timestamp": "2026-06-02T12:00:00Z",
  "messageId": "duplicate_test_001"
}
```

Expected:

* Duplicate Detection increases

Check:

```http
GET /api/v1/quality/duplicates
```

---

# Generate AI Insights

POST /api/v1/insights/generate

```json
{
  "insight_types": [
    "executive",
    "funnel",
    "attribution",
    "quality",
    "recommendations"
  ],
  "persist": true
}
```

Expected:

* Executive Summary Generated
* Recommendations Generated

---

# Verify Analytics

Open:

```http
GET /api/v1/analytics/funnel
GET /api/v1/analytics/conversion
GET /api/v1/analytics/dropoff
GET /api/v1/analytics/retention
GET /api/v1/analytics/cohorts
```

Expected:

* Funnel populated
* Conversion rates calculated
* Dropoff visible

---

# Verify Attribution

Open:

```http
GET /api/v1/attribution/sources
GET /api/v1/attribution/campaigns
GET /api/v1/attribution/top-source
GET /api/v1/attribution/deep-links
GET /api/v1/attribution/referrals
```

Expected:

* Google Attribution
* Telegram Attribution
* Referral Attribution

---

# Verify Dashboard

Refresh Frontend

Expected:

* Total Users updated
* Active Users updated
* Active Traders updated
* Revenue updated
* Top Source updated
* AI Insights visible

If all sections update successfully, the platform is functioning correctly end-to-end.

# TESTING.md

# BitMEX Growth Engineering Simulation - Testing Guide

This guide demonstrates how to interact with the Growth Engineering Analytics Platform and observe real-time changes across:

* Dashboard
* Funnel Analytics
* Attribution Analytics
* Data Quality
* AI Insights

---

# Prerequisites

Start Backend:

```bash
uvicorn app.main:app --reload
```

Backend URL:

```text
http://localhost:8000
```

Swagger UI:

```text
http://localhost:8000/api/v1/docs
```

Start Frontend:

```bash
npm run dev
```

Frontend URL:

```text
http://localhost:5173
```

---

# Test Scenario

We will simulate a complete user journey:

Landing Page
→ Signup
→ KYC
→ Deposit
→ Trade

and observe the analytics platform update automatically.

---

# Step 1 - Identify User

Endpoint:

```http
POST /api/v1/identify
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "traits": {
    "country": "India",
    "device": "Desktop",
    "source": "google",
    "campaign": "btc_launch_campaign"
  }
}
```

Expected Result:

* User profile created
* User appears in analytics datasets

---

# Step 2 - Landing Page View

Endpoint:

```http
POST /api/v1/page
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "pageName": "Landing Page"
}
```

Expected Dashboard Impact:

* Landing Page count increases
* Funnel entry count increases

---

# Step 3 - User Signup

Endpoint:

```http
POST /api/v1/track
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "event": "user_signed_up",
  "properties": {
    "source": "google",
    "campaign": "btc_launch_campaign"
  }
}
```

Expected Impact:

Dashboard:

* Total Users +1

Funnels:

* Signup count +1

Attribution:

* Google source count increases

---

# Step 4 - KYC Started

Endpoint:

```http
POST /api/v1/track
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "event": "kyc_started",
  "properties": {
    "country": "India"
  }
}
```

Expected Impact:

Funnels:

* KYC Started count increases

Analytics:

* Signup → KYC conversion updates

---

# Step 5 - KYC Completed

Endpoint:

```http
POST /api/v1/track
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "event": "kyc_completed",
  "properties": {
    "verification_method": "passport"
  }
}
```

Expected Impact:

Funnels:

* KYC Completion increases

AI Insights:

* Funnel health metrics update

---

# Step 6 - Deposit Started

Endpoint:

```http
POST /api/v1/track
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "event": "deposit_started",
  "properties": {
    "currency": "USDT"
  }
}
```

Expected Impact:

Funnels:

* Deposit Started increases

Analytics:

* KYC → Deposit conversion updates

---

# Step 7 - Deposit Completed

Endpoint:

```http
POST /api/v1/track
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "event": "deposit_completed",
  "properties": {
    "currency": "USDT",
    "amount": 1000
  }
}
```

Expected Impact:

Dashboard:

* Revenue increases

Funnels:

* Deposit Completion increases

Attribution:

* Deposit attribution metrics update

---

# Step 8 - Trade Opened

Endpoint:

```http
POST /api/v1/track
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "event": "trade_opened",
  "properties": {
    "symbol": "BTCUSDT",
    "amount": 1000,
    "leverage": 10
  }
}
```

Expected Impact:

Dashboard:

* Active Traders +1
* Revenue updates

Funnels:

* Trade Completion increases

Analytics:

* Signup → Trade conversion updates

Attribution:

* Google conversion performance improves

---

# Step 9 - Trade Closed

Endpoint:

```http
POST /api/v1/track
```

Request:

```json
{
  "userId": "mahesh_demo_001",
  "event": "trade_closed",
  "properties": {
    "symbol": "BTCUSDT",
    "profit": 250
  }
}
```

Expected Impact:

Analytics:

* Trading activity increases

Dashboard:

* Revenue metrics update

---

# Attribution Testing

Test Telegram Attribution

```json
{
  "userId": "telegram_user_001",
  "event": "user_signed_up",
  "properties": {
    "source": "telegram",
    "campaign": "telegram_trader_community"
  }
}
```

Expected Result:

Attribution Dashboard:

* Telegram source count increases

---

# Referral Testing

```json
{
  "userId": "referral_user_001",
  "event": "user_signed_up",
  "properties": {
    "source": "referral",
    "referralCode": "TRADER100"
  }
}
```

Expected Result:

Referral metrics increase.

---

# Data Quality Testing

Duplicate Event Test

Send the same request twice:

```json
{
  "messageId": "duplicate_test_001",
  "userId": "mahesh_demo_001",
  "event": "trade_opened",
  "properties": {
    "symbol": "BTCUSDT"
  }
}
```

Expected Result:

Data Quality Dashboard:

* Duplicate count increases

---

# AI Insights Testing

Generate fresh insights:

Endpoint:

```http
POST /api/v1/insights/generate
```

Expected Result:

AI Insights page updates with:

* Executive Summary
* Funnel Recommendations
* Attribution Recommendations
* Data Quality Recommendations

---

# Verification Checklist

Dashboard

✓ Total Users updates

✓ Active Users updates

✓ Active Traders updates

✓ Revenue updates

✓ Health Score visible

Funnels

✓ Landing Page

✓ Signup

✓ KYC

✓ Deposit

✓ Trade

Attribution

✓ Google attribution

✓ Telegram attribution

✓ Referral attribution

Data Quality

✓ Duplicate detection

✓ Anomaly detection

✓ Health score

AI Insights

✓ Executive summary

✓ Growth recommendations

✓ Attribution recommendations

✓ Data quality recommendations

---

# Success Criteria

The platform is functioning correctly if:

1. Events are accepted by the Track API.
2. Funnel metrics update.
3. Attribution metrics update.
4. Dashboard KPIs change.
5. AI insights can be regenerated.
6. Data Quality metrics detect issues.
7. All pages display updated information without errors.

```
```

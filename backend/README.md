# Backend — Phase 1: Foundation

Growth Engineering Analytics Platform API foundation (FastAPI + SQLAlchemy + Alembic).

## Structure

```
backend/
├── app/
│   ├── api/           # API layer (routes, DI)
│   ├── core/          # Configuration
│   ├── db/            # Database engine & session
│   ├── models/        # SQLAlchemy ORM models
│   ├── repositories/  # Repository layer
│   ├── schemas/       # Pydantic schemas
│   ├── services/      # Service layer (Phases 2–6)
│   └── main.py        # FastAPI entrypoint
├── alembic/           # Migrations
├── Dockerfile
└── requirements.txt
```

## Prerequisites

- Python 3.12+
- PostgreSQL 15+
- Redis 7+ (readiness check only in Phase 1)

## Local setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# Edit .env with your PostgreSQL and Redis settings

alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints

### Phase 1 — Foundation

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/api/v1/health` | Liveness |
| GET | `/api/v1/ready` | Readiness (DB + Redis) |
| GET | `/api/v1/docs` | OpenAPI Swagger UI |

### Phase 2 — Event tracking

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/track` | Track a taxonomy event |
| POST | `/api/v1/identify` | Identify user + traits |
| POST | `/api/v1/page` | Record a page view |
| POST | `/api/v1/events` | Unified ingest (`type`: track \| identify \| page) |
| GET | `/api/v1/events` | Event explorer (search/filter) |
| GET | `/api/v1/events/{eventId}` | Get single event |
| GET | `/api/v1/events/health` | Ingestion health metrics |

### Phase 3 — Analytics

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/analytics/funnel` | Funnel step counts & completion rate |
| GET | `/api/v1/analytics/conversion` | Step-to-step conversion rates |
| GET | `/api/v1/analytics/dropoff` | Dropoff between funnel steps |
| GET | `/api/v1/analytics/retention` | D1 / D7 / D30 retention |
| GET | `/api/v1/analytics/cohorts` | Cohort retention by signup date |

Query params: `from`, `to` (ISO datetime), `funnel` (optional), `persist_snapshot` (default `true`).

Default funnel: Landing → Signup → KYC → Deposit → Trade.

### Phase 4 — Attribution

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/attribution/sources` | Source performance by touch type |
| GET | `/api/v1/attribution/campaigns` | Campaign performance by source/touch |
| GET | `/api/v1/attribution/top-source` | Highest performing acquisition source |
| GET | `/api/v1/attribution/deep-links` | Deep link attribution metrics |
| GET | `/api/v1/attribution/referrals` | Referral code attribution metrics |

Query params: `from`, `to` (ISO datetime), `refresh` (default `true`).

### Phase 5 — Data quality

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/quality/health` | Aggregate data health score (stored in `health_scores`) |
| GET | `/api/v1/quality/duplicates` | Duplicate `messageId` detection |
| GET | `/api/v1/quality/schema-errors` | Schema / taxonomy validation issues |
| GET | `/api/v1/quality/funnel-integrity` | Broken funnel path detection |
| GET | `/api/v1/quality/anomalies` | Event volume anomaly detection |

Query params: `from`, `to` (ISO datetime), `persist_score` (health endpoint, default `true`), `funnel` (funnel-integrity).

## Tests

```powershell
pytest -v
```

## Database tables

`users`, `events`, `campaigns`, `attributions`, `funnels`, `analytics_snapshots`, `insights`, `event_validation_logs`, `health_scores`

Indexed fields: `user_id`, `event_name`, `timestamp`, `campaign_id` (per specification).

## Docker

```bash
docker build -t growth-backend .
docker run --env-file .env -p 8000:8000 growth-backend
```

Full Docker Compose stack is planned for Phase 8.

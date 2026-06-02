"""Event health metrics API."""

from fastapi import APIRouter, Query

from app.api.deps import EventHealthServiceDep
from app.schemas.event_health import EventHealthMetrics

router = APIRouter(prefix="/events", tags=["event-health"])


@router.get("/health", response_model=EventHealthMetrics, summary="Event ingestion health metrics")
def event_health(
    service: EventHealthServiceDep,
    period_hours: int = Query(default=24, ge=1, le=168, description="Lookback window in hours"),
) -> EventHealthMetrics:
    return service.get_health_metrics(period_hours=period_hours)

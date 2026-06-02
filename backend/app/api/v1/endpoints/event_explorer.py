"""Event Explorer API — search and retrieve stored events."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.api.deps import EventExplorerServiceDep
from app.schemas.events import EventExplorerResponse, EventRecordSchema

router = APIRouter(prefix="/events", tags=["event-explorer"])


@router.get("", response_model=EventExplorerResponse, summary="Search and list events")
def list_events(
    service: EventExplorerServiceDep,
    event_name: str | None = Query(default=None),
    event_type: str | None = Query(default=None),
    user_id: str | None = Query(default=None, description="External user ID"),
    anonymous_id: str | None = Query(default=None),
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
) -> EventExplorerResponse:
    return service.search(
        event_name=event_name,
        event_type=event_type,
        user_external_id=user_id,
        anonymous_id=anonymous_id,
        from_timestamp=from_timestamp,
        to_timestamp=to_timestamp,
        limit=limit,
        offset=offset,
    )


@router.get("/{event_id}", response_model=EventRecordSchema, summary="Get event by event_id")
def get_event(
    event_id: str,
    service: EventExplorerServiceDep,
) -> EventRecordSchema:
    return service.get_by_event_id(event_id)

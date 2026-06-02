"""Segment-style ingestion endpoints: track, identify, page, events."""

import logging

from fastapi import APIRouter, status
from pydantic import ValidationError as PydanticValidationError

from app.api.deps import EventTrackingServiceDep
from app.schemas.events import (
    EventIngestResponse,
    IdentifyRequest,
    IngestEventRequest,
    PageRequest,
    TrackRequest,
    ValidationIssueSchema,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["event-tracking"])


@router.post(
    "/track",
    response_model=EventIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Track a custom event",
)
def track_event(
    payload: TrackRequest,
    service: EventTrackingServiceDep,
) -> EventIngestResponse:
    return service.track(payload)


@router.post(
    "/identify",
    response_model=EventIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Identify a user and merge traits",
)
def identify_user(
    payload: IdentifyRequest,
    service: EventTrackingServiceDep,
) -> EventIngestResponse:
    return service.identify(payload)


@router.post(
    "/page",
    response_model=EventIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Record a page view",
)
def page_view(
    payload: PageRequest,
    service: EventTrackingServiceDep,
) -> EventIngestResponse:
    return service.page(payload)


@router.post(
    "/events",
    response_model=EventIngestResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Unified event ingestion (track | identify | page)",
)
def ingest_event(
    body: IngestEventRequest,
    service: EventTrackingServiceDep,
) -> EventIngestResponse:
    try:
        if body.type == "track":
            payload = TrackRequest.model_validate(body.payload)
            return service.track(payload)
        if body.type == "identify":
            payload = IdentifyRequest.model_validate(body.payload)
            return service.identify(payload)
        payload = PageRequest.model_validate(body.payload)
        return service.page(payload)
    except PydanticValidationError as exc:
        logger.warning("Invalid unified event payload type=%s: %s", body.type, exc)
        return EventIngestResponse(
            success=False,
            validation=[
                ValidationIssueSchema(code="invalid_schema", message=err["msg"])
                for err in exc.errors()
            ],
        )

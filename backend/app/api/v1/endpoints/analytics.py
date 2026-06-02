"""Analytics REST API — funnel, conversion, dropoff, retention, cohorts."""

import logging
from datetime import datetime

from fastapi import APIRouter, Query

from app.api.deps import AnalyticsServiceDep
from app.schemas.analytics import (
    CohortAnalyticsResponse,
    ConversionAnalyticsResponse,
    DropoffAnalyticsResponse,
    FunnelAnalyticsResponse,
    RetentionAnalyticsResponse,
)
from app.services.analytics_service import AnalyticsService, FunnelNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])


def _resolve_period(
    from_timestamp: datetime | None,
    to_timestamp: datetime | None,
) -> tuple[datetime, datetime]:
    if from_timestamp and to_timestamp:
        return from_timestamp, to_timestamp
    return AnalyticsService.default_period()


@router.get("/funnel", response_model=FunnelAnalyticsResponse, summary="Funnel analytics")
def get_funnel_analytics(
    service: AnalyticsServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    funnel: str | None = Query(default=None, description="Funnel name (default funnel if omitted)"),
    persist_snapshot: bool = Query(default=True),
) -> FunnelAnalyticsResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    try:
        return service.get_funnel_analytics(
            period_start=period_start,
            period_end=period_end,
            funnel_name=funnel,
            persist_snapshot=persist_snapshot,
        )
    except FunnelNotFoundError:
        raise


@router.get(
    "/conversion",
    response_model=ConversionAnalyticsResponse,
    summary="Step-to-step conversion analytics",
)
def get_conversion_analytics(
    service: AnalyticsServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    funnel: str | None = Query(default=None),
    persist_snapshot: bool = Query(default=True),
) -> ConversionAnalyticsResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    try:
        return service.get_conversion_analytics(
            period_start=period_start,
            period_end=period_end,
            funnel_name=funnel,
            persist_snapshot=persist_snapshot,
        )
    except FunnelNotFoundError:
        raise


@router.get(
    "/dropoff",
    response_model=DropoffAnalyticsResponse,
    summary="Funnel dropoff analysis",
)
def get_dropoff_analytics(
    service: AnalyticsServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    funnel: str | None = Query(default=None),
    persist_snapshot: bool = Query(default=True),
) -> DropoffAnalyticsResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    try:
        return service.get_dropoff_analytics(
            period_start=period_start,
            period_end=period_end,
            funnel_name=funnel,
            persist_snapshot=persist_snapshot,
        )
    except FunnelNotFoundError:
        raise


@router.get(
    "/retention",
    response_model=RetentionAnalyticsResponse,
    summary="D1 / D7 / D30 retention analytics",
)
def get_retention_analytics(
    service: AnalyticsServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    anchor_event: str = Query(default="user_signed_up"),
    persist_snapshot: bool = Query(default=True),
) -> RetentionAnalyticsResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_retention_analytics(
        period_start=period_start,
        period_end=period_end,
        anchor_event=anchor_event,
        persist_snapshot=persist_snapshot,
    )


@router.get(
    "/cohorts",
    response_model=CohortAnalyticsResponse,
    summary="Cohort retention by signup date",
)
def get_cohort_analytics(
    service: AnalyticsServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    anchor_event: str = Query(default="user_signed_up"),
    persist_snapshot: bool = Query(default=True),
) -> CohortAnalyticsResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_cohort_analytics(
        period_start=period_start,
        period_end=period_end,
        anchor_event=anchor_event,
        persist_snapshot=persist_snapshot,
    )

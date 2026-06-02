"""Data quality monitoring APIs."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.api.deps import DataQualityServiceDep
from app.schemas.quality import (
    AnomaliesResponse,
    DataHealthResponse,
    DuplicatesResponse,
    FunnelIntegrityResponse,
    SchemaErrorsResponse,
)
from app.services.data_quality_service import DataQualityService

router = APIRouter(prefix="/quality", tags=["data-quality"])


def _resolve_period(
    from_timestamp: datetime | None,
    to_timestamp: datetime | None,
) -> tuple[datetime, datetime]:
    if from_timestamp and to_timestamp:
        return from_timestamp, to_timestamp
    return DataQualityService.default_period()


@router.get("/health", response_model=DataHealthResponse, summary="Aggregate data health score")
def quality_health(
    service: DataQualityServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    persist_score: bool = Query(default=True),
) -> DataHealthResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_health(
        period_start=period_start,
        period_end=period_end,
        persist_score=persist_score,
    )


@router.get("/duplicates", response_model=DuplicatesResponse, summary="Duplicate event detection")
def quality_duplicates(
    service: DataQualityServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
) -> DuplicatesResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_duplicates(period_start=period_start, period_end=period_end)


@router.get(
    "/schema-errors",
    response_model=SchemaErrorsResponse,
    summary="Schema validation monitoring",
)
def quality_schema_errors(
    service: DataQualityServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
) -> SchemaErrorsResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_schema_errors(period_start=period_start, period_end=period_end)


@router.get(
    "/funnel-integrity",
    response_model=FunnelIntegrityResponse,
    summary="Broken funnel path detection",
)
def quality_funnel_integrity(
    service: DataQualityServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    funnel: str | None = Query(default=None),
) -> FunnelIntegrityResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_funnel_integrity(
        period_start=period_start,
        period_end=period_end,
        funnel_name=funnel,
    )


@router.get(
    "/anomalies",
    response_model=AnomaliesResponse,
    summary="Event volume anomaly detection",
)
def quality_anomalies(
    service: DataQualityServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
) -> AnomaliesResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_anomalies(period_start=period_start, period_end=period_end)

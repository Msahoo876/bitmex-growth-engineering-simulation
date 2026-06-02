"""AI insights APIs."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Query

from app.api.deps import ExecutiveReportServiceDep
from app.schemas.insights import (
    ExecutiveSummaryResponse,
    GeneratedInsightsResponse,
    InsightGenerateRequest,
    InsightListResponse,
    InsightResponse,
)
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/insights", tags=["ai-insights"])


def _resolve_period(
    from_timestamp: datetime | None,
    to_timestamp: datetime | None,
) -> tuple[datetime, datetime]:
    if from_timestamp and to_timestamp:
        return from_timestamp, to_timestamp
    return AnalyticsService.default_period()


@router.post("/generate", response_model=GeneratedInsightsResponse, summary="Generate AI insights")
def generate_insights(
    payload: InsightGenerateRequest,
    service: ExecutiveReportServiceDep,
) -> GeneratedInsightsResponse:
    period_start, period_end = _resolve_period(payload.from_timestamp, payload.to_timestamp)
    insights = service.generate_insights(
        insight_types=list(payload.insight_types),
        period_start=period_start,
        period_end=period_end,
        persist=payload.persist,
    )
    return GeneratedInsightsResponse(insights=insights, generated_count=len(insights))


@router.get("", response_model=InsightListResponse, summary="List generated insights")
def list_insights(
    service: ExecutiveReportServiceDep,
    insight_type: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> InsightListResponse:
    return InsightListResponse(
        insights=service.list_insights(insight_type=insight_type, limit=limit, offset=offset)
    )


@router.get(
    "/executive-summary",
    response_model=ExecutiveSummaryResponse,
    summary="Latest executive AI summary",
)
def executive_summary(service: ExecutiveReportServiceDep) -> ExecutiveSummaryResponse:
    return service.get_executive_summary()


@router.get("/{insight_id}", response_model=InsightResponse, summary="Get a generated insight")
def get_insight(insight_id: UUID, service: ExecutiveReportServiceDep) -> InsightResponse:
    return service.get_insight(insight_id)

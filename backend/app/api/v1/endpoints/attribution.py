"""Attribution APIs."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.api.deps import AttributionServiceDep
from app.schemas.attribution import (
    CampaignAttributionResponse,
    DeepLinkResponse,
    ReferralResponse,
    SourceAttributionResponse,
    TopSourceResponse,
)
from app.services.attribution_service import AttributionService

router = APIRouter(prefix="/attribution", tags=["attribution"])


def _resolve_period(
    from_timestamp: datetime | None,
    to_timestamp: datetime | None,
) -> tuple[datetime, datetime]:
    if from_timestamp and to_timestamp:
        return from_timestamp, to_timestamp
    return AttributionService.default_period()


@router.get("/sources", response_model=SourceAttributionResponse)
def attribution_sources(
    service: AttributionServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    refresh: bool = Query(default=True),
) -> SourceAttributionResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_sources(period_start=period_start, period_end=period_end, refresh=refresh)


@router.get("/campaigns", response_model=CampaignAttributionResponse)
def attribution_campaigns(
    service: AttributionServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    refresh: bool = Query(default=True),
) -> CampaignAttributionResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_campaigns(period_start=period_start, period_end=period_end, refresh=refresh)


@router.get("/top-source", response_model=TopSourceResponse)
def attribution_top_source(
    service: AttributionServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    refresh: bool = Query(default=True),
) -> TopSourceResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_top_source(period_start=period_start, period_end=period_end, refresh=refresh)


@router.get("/deep-links", response_model=DeepLinkResponse)
def attribution_deep_links(
    service: AttributionServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    refresh: bool = Query(default=True),
) -> DeepLinkResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_deep_links(period_start=period_start, period_end=period_end, refresh=refresh)


@router.get("/referrals", response_model=ReferralResponse)
def attribution_referrals(
    service: AttributionServiceDep,
    from_timestamp: datetime | None = Query(default=None, alias="from"),
    to_timestamp: datetime | None = Query(default=None, alias="to"),
    refresh: bool = Query(default=True),
) -> ReferralResponse:
    period_start, period_end = _resolve_period(from_timestamp, to_timestamp)
    return service.get_referrals(period_start=period_start, period_end=period_end, refresh=refresh)

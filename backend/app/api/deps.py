"""FastAPI dependency injection wiring."""

from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from redis import Redis
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.repositories.base import BaseRepository
from app.services.analytics_service import AnalyticsService
from app.services.attribution_service import AttributionService
from app.services.data_quality_service import DataQualityService
from app.services.event_explorer_service import EventExplorerService
from app.services.event_health_service import EventHealthService
from app.services.event_tracking_service import EventTrackingService
from app.services.ai.executive_report_service import ExecutiveReportService

SettingsDep = Annotated[Settings, Depends(get_settings)]
DbSessionDep = Annotated[Session, Depends(get_db)]


def get_redis(settings: SettingsDep) -> Generator[Redis, None, None]:
    client = Redis.from_url(settings.redis_dsn, decode_responses=True)
    try:
        yield client
    finally:
        client.close()


RedisDep = Annotated[Redis, Depends(get_redis)]


def get_event_tracking_service(db: DbSessionDep) -> Generator[EventTrackingService, None, None]:
    yield EventTrackingService(db)


def get_event_explorer_service(db: DbSessionDep) -> Generator[EventExplorerService, None, None]:
    yield EventExplorerService(db)


def get_event_health_service(db: DbSessionDep) -> Generator[EventHealthService, None, None]:
    yield EventHealthService(db)


def get_analytics_service(db: DbSessionDep) -> Generator[AnalyticsService, None, None]:
    yield AnalyticsService(db)


def get_attribution_service(db: DbSessionDep) -> Generator[AttributionService, None, None]:
    yield AttributionService(db)


def get_data_quality_service(db: DbSessionDep) -> Generator[DataQualityService, None, None]:
    yield DataQualityService(db)


def get_executive_report_service(
    db: DbSessionDep,
    settings: SettingsDep,
) -> Generator[ExecutiveReportService, None, None]:
    yield ExecutiveReportService(db, settings)


EventTrackingServiceDep = Annotated[EventTrackingService, Depends(get_event_tracking_service)]
EventExplorerServiceDep = Annotated[EventExplorerService, Depends(get_event_explorer_service)]
EventHealthServiceDep = Annotated[EventHealthService, Depends(get_event_health_service)]
AnalyticsServiceDep = Annotated[AnalyticsService, Depends(get_analytics_service)]
AttributionServiceDep = Annotated[AttributionService, Depends(get_attribution_service)]
DataQualityServiceDep = Annotated[DataQualityService, Depends(get_data_quality_service)]
ExecutiveReportServiceDep = Annotated[ExecutiveReportService, Depends(get_executive_report_service)]


def get_repository(model: type) -> type:
    def _factory(db: DbSessionDep) -> BaseRepository:
        return BaseRepository(db, model)

    return _factory

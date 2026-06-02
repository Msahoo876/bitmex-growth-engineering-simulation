"""Analytics orchestration — funnel, conversion, dropoff, retention, cohorts."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.domain.funnels import (
    RETENTION_ACTIVITY_EVENTS,
    RETENTION_ANCHOR_EVENT,
    RETENTION_DAYS,
)
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.analytics_snapshot_repository import AnalyticsSnapshotRepository
from app.repositories.funnel_repository import FunnelRepository
from app.schemas.analytics import (
    AnalyticsPeriod,
    CohortAnalyticsResponse,
    CohortRowResponse,
    ConversionAnalyticsResponse,
    ConversionStepResponse,
    DropoffAnalyticsResponse,
    DropoffStepResponse,
    FunnelAnalyticsResponse,
    FunnelStepResponse,
    RetentionAnalyticsResponse,
    RetentionPeriodResponse,
)
from app.services.analytics.funnel_engine import FunnelAnalyticsEngine
from app.services.analytics.retention_engine import RetentionAnalyticsEngine

logger = logging.getLogger(__name__)


class FunnelNotFoundError(AppError):
    def __init__(self, funnel_name: str) -> None:
        super().__init__(message=f"Funnel '{funnel_name}' not found.", code="funnel_not_found")


class AnalyticsService:
    """Transforms raw events into business metrics and persists snapshots."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._analytics = AnalyticsRepository(session)
        self._funnels = FunnelRepository(session)
        self._snapshots = AnalyticsSnapshotRepository(session)
        self._funnel_engine = FunnelAnalyticsEngine()
        self._retention_engine = RetentionAnalyticsEngine()

    def get_funnel_analytics(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        funnel_name: str | None = None,
        persist_snapshot: bool = True,
    ) -> FunnelAnalyticsResponse:
        funnel_result = self._compute_funnel(
            period_start=period_start,
            period_end=period_end,
            funnel_name=funnel_name,
        )
        response = FunnelAnalyticsResponse(
            funnel_name=funnel_result.funnel_name,
            period=AnalyticsPeriod(start=period_start, end=period_end),
            steps=[
                FunnelStepResponse(
                    key=s.key,
                    label=s.label,
                    event_name=s.event_name,
                    users=s.users,
                    conversion_rate_from_previous=s.conversion_rate_from_previous,
                    conversion_rate_from_start=s.conversion_rate_from_start,
                )
                for s in funnel_result.steps
            ],
            total_entered=funnel_result.total_entered,
            total_completed=funnel_result.total_completed,
            completion_rate=funnel_result.completion_rate,
        )
        if persist_snapshot:
            snapshot = self._persist(
                snapshot_type="funnel",
                period_start=period_start,
                period_end=period_end,
                metrics=response.model_dump(mode="json"),
            )
            response.snapshot_id = str(snapshot.id)
        self._session.commit()
        logger.info(
            "Funnel analytics computed funnel=%s entered=%s completed=%s",
            funnel_result.funnel_name,
            funnel_result.total_entered,
            funnel_result.total_completed,
        )
        return response

    def get_conversion_analytics(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        funnel_name: str | None = None,
        persist_snapshot: bool = True,
    ) -> ConversionAnalyticsResponse:
        funnel_result = self._compute_funnel(
            period_start=period_start,
            period_end=period_end,
            funnel_name=funnel_name,
        )
        conversions: list[ConversionStepResponse] = []
        for index in range(1, len(funnel_result.steps)):
            prev_step = funnel_result.steps[index - 1]
            curr_step = funnel_result.steps[index]
            rate = (
                round((curr_step.users / prev_step.users) * 100, 2)
                if prev_step.users > 0
                else 0.0
            )
            conversions.append(
                ConversionStepResponse(
                    from_step=prev_step.key,
                    to_step=curr_step.key,
                    from_event=prev_step.event_name,
                    to_event=curr_step.event_name,
                    users_at_from_step=prev_step.users,
                    users_at_to_step=curr_step.users,
                    conversion_rate=rate,
                )
            )

        overall = funnel_result.completion_rate
        response = ConversionAnalyticsResponse(
            funnel_name=funnel_result.funnel_name,
            period=AnalyticsPeriod(start=period_start, end=period_end),
            conversions=conversions,
            overall_conversion_rate=overall,
        )
        if persist_snapshot:
            snapshot = self._persist(
                snapshot_type="conversion",
                period_start=period_start,
                period_end=period_end,
                metrics=response.model_dump(mode="json"),
            )
            response.snapshot_id = str(snapshot.id)
        self._session.commit()
        logger.info("Conversion analytics computed funnel=%s", funnel_result.funnel_name)
        return response

    def get_dropoff_analytics(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        funnel_name: str | None = None,
        persist_snapshot: bool = True,
    ) -> DropoffAnalyticsResponse:
        funnel_result = self._compute_funnel(
            period_start=period_start,
            period_end=period_end,
            funnel_name=funnel_name,
        )
        dropoff_result = self._funnel_engine.compute_dropoff(funnel_result)
        response = DropoffAnalyticsResponse(
            funnel_name=dropoff_result.funnel_name,
            period=AnalyticsPeriod(start=period_start, end=period_end),
            steps=[
                DropoffStepResponse(
                    from_step=s.from_step,
                    to_step=s.to_step,
                    users_lost=s.users_lost,
                    dropoff_rate=s.dropoff_rate,
                )
                for s in dropoff_result.steps
            ],
            largest_dropoff_step=dropoff_result.largest_dropoff_step,
        )
        if persist_snapshot:
            snapshot = self._persist(
                snapshot_type="dropoff",
                period_start=period_start,
                period_end=period_end,
                metrics=response.model_dump(mode="json"),
            )
            response.snapshot_id = str(snapshot.id)
        self._session.commit()
        logger.info("Dropoff analytics computed funnel=%s", dropoff_result.funnel_name)
        return response

    def get_retention_analytics(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        anchor_event: str = RETENTION_ANCHOR_EVENT,
        persist_snapshot: bool = True,
    ) -> RetentionAnalyticsResponse:
        activity_end = period_end + timedelta(days=max(RETENTION_DAYS))
        anchor_records = self._analytics.fetch_anchor_events(
            anchor_event=anchor_event,
            period_start=period_start,
            period_end=period_end,
        )
        activity_records = self._analytics.fetch_activity_events(
            activity_events=list(RETENTION_ACTIVITY_EVENTS),
            period_start=period_start,
            period_end=activity_end,
        )
        result = self._retention_engine.compute_retention(
            anchor_event=anchor_event,
            activity_events=RETENTION_ACTIVITY_EVENTS,
            anchor_records=anchor_records,
            activity_records=activity_records,
            retention_days=RETENTION_DAYS,
        )
        response = RetentionAnalyticsResponse(
            anchor_event=result.anchor_event,
            period=AnalyticsPeriod(start=period_start, end=period_end),
            cohort_size=result.cohort_size,
            periods=[
                RetentionPeriodResponse(
                    day=p.day,
                    retained_users=p.retained_users,
                    retention_rate=p.retention_rate,
                )
                for p in result.periods
            ],
        )
        if persist_snapshot:
            snapshot = self._persist(
                snapshot_type="retention",
                period_start=period_start,
                period_end=period_end,
                metrics=response.model_dump(mode="json"),
            )
            response.snapshot_id = str(snapshot.id)
        self._session.commit()
        logger.info("Retention analytics cohort_size=%s", result.cohort_size)
        return response

    def get_cohort_analytics(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        anchor_event: str = RETENTION_ANCHOR_EVENT,
        persist_snapshot: bool = True,
    ) -> CohortAnalyticsResponse:
        activity_end = period_end + timedelta(days=max(RETENTION_DAYS))
        anchor_records = self._analytics.fetch_anchor_events(
            anchor_event=anchor_event,
            period_start=period_start,
            period_end=period_end,
        )
        activity_records = self._analytics.fetch_activity_events(
            activity_events=list(RETENTION_ACTIVITY_EVENTS),
            period_start=period_start,
            period_end=activity_end,
        )
        result = self._retention_engine.compute_cohorts(
            anchor_event=anchor_event,
            activity_events=RETENTION_ACTIVITY_EVENTS,
            anchor_records=anchor_records,
            activity_records=activity_records,
        )
        response = CohortAnalyticsResponse(
            anchor_event=result.anchor_event,
            period=AnalyticsPeriod(start=period_start, end=period_end),
            cohorts=[
                CohortRowResponse(
                    cohort_date=c.cohort_date,
                    cohort_size=c.cohort_size,
                    d1_retention=c.d1_retention,
                    d7_retention=c.d7_retention,
                    d30_retention=c.d30_retention,
                )
                for c in result.cohorts
            ],
        )
        if persist_snapshot:
            snapshot = self._persist(
                snapshot_type="cohort",
                period_start=period_start,
                period_end=period_end,
                metrics=response.model_dump(mode="json"),
            )
            response.snapshot_id = str(snapshot.id)
        self._session.commit()
        logger.info("Cohort analytics rows=%s", len(result.cohorts))
        return response

    def _compute_funnel(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        funnel_name: str | None,
    ):
        try:
            resolved_name, step_defs = self._funnels.resolve_steps(funnel_name)
        except ValueError as exc:
            raise FunnelNotFoundError(funnel_name or "") from exc

        event_names = [s.event_name for s in step_defs]
        records = self._analytics.fetch_events_for_steps(
            event_names=event_names,
            period_start=period_start,
            period_end=period_end,
        )
        grouped = self._analytics.group_events_by_identity(records)
        return self._funnel_engine.compute_funnel(
            funnel_name=resolved_name,
            step_definitions=step_defs,
            grouped_events=grouped,
        )

    def _persist(
        self,
        *,
        snapshot_type: str,
        period_start: datetime,
        period_end: datetime,
        metrics: dict[str, Any],
    ):
        return self._snapshots.save_snapshot(
            snapshot_type=snapshot_type,
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
        )

    @staticmethod
    def default_period(days: int = 30) -> tuple[datetime, datetime]:
        end = datetime.now(UTC)
        start = end - timedelta(days=days)
        return start, end

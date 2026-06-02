"""Data quality monitoring service."""

import logging
from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.domain.funnels import DEFAULT_FUNNEL_NAME, DEFAULT_FUNNEL_STEPS
from app.repositories.funnel_repository import FunnelRepository
from app.repositories.health_score_repository import HealthScoreRepository
from app.repositories.quality_repository import DuplicateMessageGroup, QualityRepository
from app.schemas.quality import (
    AnomaliesResponse,
    BrokenFunnelPathItem,
    DataHealthResponse,
    DuplicateGroupResponse,
    DuplicatesResponse,
    FunnelIntegrityResponse,
    MissingPropertyItem,
    MissingPropertiesSummary,
    QualityPeriod,
    SchemaErrorItem,
    SchemaErrorsResponse,
    VolumeAnomalyItem,
)
from app.services.quality.quality_engine import DataQualityEngine

logger = logging.getLogger(__name__)


class DataQualityService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._quality = QualityRepository(session)
        self._health_scores = HealthScoreRepository(session)
        self._funnels = FunnelRepository(session)
        self._engine = DataQualityEngine()

    def get_health(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        persist_score: bool = True,
    ) -> DataHealthResponse:
        audit = self._run_audit(period_start=period_start, period_end=period_end)
        breakdown = {
            "duplicate_penalty": min(25.0, (audit.duplicate_events / max(audit.total_events, 1)) * 25),
            "schema_penalty": min(25.0, (audit.schema_error_count / max(audit.total_events, 1)) * 25),
            "missing_property_penalty": min(
                20.0, (audit.missing_property_count / max(audit.total_events, 1)) * 20
            ),
            "anomaly_penalty": min(15.0, audit.volume_anomaly_count * 3),
            "funnel_integrity_penalty": min(
                15.0, (audit.broken_funnel_paths / max(audit.total_events, 1)) * 15
            ),
        }
        snapshot_id = None
        if persist_score:
            snapshot = self._health_scores.save_score(
                score=audit.health_score,
                period_start=period_start,
                period_end=period_end,
                breakdown={
                    "summary": {
                        "total_events": audit.total_events,
                        "duplicate_groups": audit.duplicate_groups,
                        "duplicate_events": audit.duplicate_events,
                        "schema_error_count": audit.schema_error_count,
                        "missing_property_count": audit.missing_property_count,
                        "volume_anomaly_count": audit.volume_anomaly_count,
                        "broken_funnel_paths": audit.broken_funnel_paths,
                    },
                    "penalties": breakdown,
                },
                check_type="data_quality",
            )
            snapshot_id = str(snapshot.id)
            self._session.commit()

        logger.info(
            "Data health score=%.2f events=%s duplicates=%s",
            audit.health_score,
            audit.total_events,
            audit.duplicate_groups,
        )
        return DataHealthResponse(
            period=QualityPeriod(start=period_start, end=period_end),
            health_score=audit.health_score,
            snapshot_id=snapshot_id,
            summary={
                "total_events": audit.total_events,
                "duplicate_groups": audit.duplicate_groups,
                "duplicate_events": audit.duplicate_events,
                "schema_error_count": audit.schema_error_count,
                "missing_property_count": audit.missing_property_count,
                "volume_anomaly_count": audit.volume_anomaly_count,
                "broken_funnel_paths": audit.broken_funnel_paths,
            },
            breakdown=breakdown,
        )

    def get_duplicates(
        self, *, period_start: datetime, period_end: datetime
    ) -> DuplicatesResponse:
        stored = self._quality.find_duplicate_message_ids(
            period_start=period_start, period_end=period_end
        )
        logged = self._quality.find_duplicate_message_ids_from_logs(
            period_start=period_start, period_end=period_end
        )
        merged: dict[str, DuplicateMessageGroup] = {}
        for group in stored + logged:
            existing = merged.get(group.message_id)
            if existing is None or group.count > existing.count:
                merged[group.message_id] = group
        groups = list(merged.values())
        duplicate_events = sum(g.count for g in logged) + sum(
            max(0, g.count - 1) for g in stored
        )
        return DuplicatesResponse(
            period=QualityPeriod(start=period_start, end=period_end),
            total_duplicate_groups=len(groups),
            total_duplicate_events=duplicate_events,
            groups=[
                DuplicateGroupResponse(
                    message_id=g.message_id, count=g.count, event_ids=g.event_ids
                )
                for g in groups
            ],
        )

    def get_schema_errors(
        self, *, period_start: datetime, period_end: datetime
    ) -> SchemaErrorsResponse:
        log_errors = self._quality.schema_errors_from_logs(
            period_start=period_start, period_end=period_end
        )
        events = self._quality.fetch_events_for_audit(
            period_start=period_start, period_end=period_end
        )
        stored_violations = self._engine.detect_stored_schema_violations(events)

        errors: list[SchemaErrorItem] = [
            SchemaErrorItem(
                validation_code=item.get("validation_code"),
                event_name=item.get("event_name"),
                message_id=item.get("message_id"),
                message=item["message"],
            )
            for item in log_errors
        ]
        for violation in stored_violations:
            errors.append(
                SchemaErrorItem(
                    event_id=violation["event_id"],
                    event_name=violation["event_name"],
                    issue=violation["issue"],
                    message=f"Stored event schema violation: {violation['issue']}",
                )
            )
        return SchemaErrorsResponse(
            period=QualityPeriod(start=period_start, end=period_end),
            total_errors=len(errors),
            errors=errors,
        )

    def get_missing_properties(
        self, *, period_start: datetime, period_end: datetime
    ) -> MissingPropertiesSummary:
        events = self._quality.fetch_events_for_audit(
            period_start=period_start, period_end=period_end
        )
        issues = self._engine.detect_missing_properties(events)
        return MissingPropertiesSummary(
            period=QualityPeriod(start=period_start, end=period_end),
            total_issues=len(issues),
            issues=[
                MissingPropertyItem(
                    event_id=i.event_id,
                    event_name=i.event_name,
                    missing_fields=i.missing_fields,
                )
                for i in issues
            ],
        )

    def get_anomalies(
        self, *, period_start: datetime, period_end: datetime
    ) -> AnomaliesResponse:
        daily = self._quality.daily_event_volume(
            period_start=period_start, period_end=period_end
        )
        detected = self._engine.detect_volume_anomalies(daily)
        return AnomaliesResponse(
            period=QualityPeriod(start=period_start, end=period_end),
            total_anomalies=len(detected),
            daily_volume={str(day): count for day, count in sorted(daily.items())},
            anomalies=[
                VolumeAnomalyItem(
                    date=a.date,
                    count=a.count,
                    baseline_mean=a.baseline_mean,
                    deviation_pct=a.deviation_pct,
                )
                for a in detected
            ],
        )

    def get_funnel_integrity(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        funnel_name: str | None = None,
    ) -> FunnelIntegrityResponse:
        try:
            resolved_name, steps = self._funnels.resolve_steps(funnel_name)
        except ValueError:
            resolved_name, steps = DEFAULT_FUNNEL_NAME, list(DEFAULT_FUNNEL_STEPS)

        event_names = [s.event_name for s in steps]
        events = self._quality.fetch_funnel_events(
            event_names=event_names,
            period_start=period_start,
            period_end=period_end,
        )
        broken = self._engine.detect_broken_funnel_paths(events, steps)
        return FunnelIntegrityResponse(
            period=QualityPeriod(start=period_start, end=period_end),
            funnel_name=resolved_name,
            total_broken_paths=len(broken),
            broken_paths=[
                BrokenFunnelPathItem(
                    identity=b.identity,
                    skipped_step=b.skipped_step,
                    reached_step=b.reached_step,
                )
                for b in broken
            ],
        )

    def _run_audit(self, *, period_start: datetime, period_end: datetime):
        events = self._quality.fetch_events_for_audit(
            period_start=period_start, period_end=period_end
        )
        duplicates = self._quality.find_duplicate_message_ids(
            period_start=period_start, period_end=period_end
        )
        log_errors = self._quality.schema_errors_from_logs(
            period_start=period_start, period_end=period_end
        )
        stored_schema = self._engine.detect_stored_schema_violations(events)
        missing = self._engine.detect_missing_properties(events)
        daily = self._quality.daily_event_volume(
            period_start=period_start, period_end=period_end
        )
        anomalies = self._engine.detect_volume_anomalies(daily)

        try:
            _, steps = self._funnels.resolve_steps(None)
        except ValueError:
            steps = list(DEFAULT_FUNNEL_STEPS)
        funnel_events = self._quality.fetch_funnel_events(
            event_names=[s.event_name for s in steps],
            period_start=period_start,
            period_end=period_end,
        )
        broken = self._engine.detect_broken_funnel_paths(funnel_events, steps)

        return self._engine.build_summary(
            total_events=len(events),
            duplicate_groups=duplicates,
            schema_error_count=len(log_errors) + len(stored_schema),
            missing_property_count=len(missing),
            volume_anomaly_count=len(anomalies),
            broken_funnel_paths=len(broken),
        )

    @staticmethod
    def default_period(days: int = 30) -> tuple[datetime, datetime]:
        end = datetime.now(UTC)
        start = end - timedelta(days=days)
        return start, end

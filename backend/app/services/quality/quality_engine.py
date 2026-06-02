"""Pure data quality computation logic."""

from dataclasses import dataclass
from datetime import date
from statistics import mean, stdev

from app.domain.funnels import FunnelStepDefinition
from app.domain.quality_rules import (
    MIN_EVENTS_FOR_ANOMALY,
    VOLUME_ANOMALY_THRESHOLD_PCT,
    is_valid_event_name,
    missing_required_properties,
)
from app.repositories.quality_repository import (
    DuplicateMessageGroup,
    StoredEventAuditRow,
)


@dataclass(frozen=True)
class MissingPropertyIssue:
    event_id: str
    event_name: str
    missing_fields: list[str]


@dataclass(frozen=True)
class VolumeAnomaly:
    date: date
    count: int
    baseline_mean: float
    deviation_pct: float


@dataclass(frozen=True)
class BrokenFunnelPath:
    identity: str
    skipped_step: str
    reached_step: str


@dataclass(frozen=True)
class QualityAuditSummary:
    total_events: int
    duplicate_groups: int
    duplicate_events: int
    schema_error_count: int
    missing_property_count: int
    volume_anomaly_count: int
    broken_funnel_paths: int
    health_score: float


class DataQualityEngine:
    def detect_missing_properties(self, events: list[StoredEventAuditRow]) -> list[MissingPropertyIssue]:
        issues: list[MissingPropertyIssue] = []
        for event in events:
            if event.event_type not in ("track", "page"):
                continue
            missing = missing_required_properties(event.event_name, event.properties)
            if missing:
                issues.append(
                    MissingPropertyIssue(
                        event_id=event.event_id,
                        event_name=event.event_name,
                        missing_fields=missing,
                    )
                )
        return issues

    def detect_stored_schema_violations(
        self, events: list[StoredEventAuditRow]
    ) -> list[dict[str, str]]:
        violations: list[dict[str, str]] = []
        for event in events:
            if event.event_type == "track" and not is_valid_event_name(event.event_name):
                violations.append(
                    {
                        "event_id": event.event_id,
                        "event_name": event.event_name,
                        "issue": "unknown_event_name",
                    }
                )
            if event.event_type in ("track", "page") and not event.user_id and not event.anonymous_id:
                violations.append(
                    {
                        "event_id": event.event_id,
                        "event_name": event.event_name,
                        "issue": "missing_user_id",
                    }
                )
            if event.properties is not None and not isinstance(event.properties, dict):
                violations.append(
                    {
                        "event_id": event.event_id,
                        "event_name": event.event_name,
                        "issue": "invalid_schema",
                    }
                )
        return violations

    def detect_volume_anomalies(self, daily_volume: dict[date, int]) -> list[VolumeAnomaly]:
        if not daily_volume:
            return []
        total = sum(daily_volume.values())
        if total < MIN_EVENTS_FOR_ANOMALY:
            return []

        counts = list(daily_volume.values())
        if len(counts) < 2:
            return []

        baseline = mean(counts)
        if baseline <= 0:
            return []

        spread = stdev(counts) if len(counts) > 1 else 0.0
        anomalies: list[VolumeAnomaly] = []
        for day, count in sorted(daily_volume.items()):
            deviation_pct = abs(count - baseline) / baseline * 100
            if deviation_pct >= VOLUME_ANOMALY_THRESHOLD_PCT:
                if spread > 0 and abs(count - baseline) < spread:
                    continue
                anomalies.append(
                    VolumeAnomaly(
                        date=day,
                        count=count,
                        baseline_mean=round(baseline, 2),
                        deviation_pct=round(deviation_pct, 2),
                    )
                )
        return anomalies

    def detect_broken_funnel_paths(
        self,
        events: list[StoredEventAuditRow],
        steps: list[FunnelStepDefinition],
    ) -> list[BrokenFunnelPath]:
        step_names = [s.event_name for s in steps]
        step_index = {name: i for i, name in enumerate(step_names)}
        grouped: dict[str, list[StoredEventAuditRow]] = {}

        for event in events:
            if event.event_name not in step_index:
                continue
            if event.user_id:
                identity = f"user:{event.user_id}"
            elif event.anonymous_id:
                identity = f"anon:{event.anonymous_id}"
            else:
                continue
            grouped.setdefault(identity, []).append(event)

        broken: list[BrokenFunnelPath] = []
        for identity, user_events in grouped.items():
            ordered = sorted(user_events, key=lambda e: e.timestamp)
            max_index = -1
            for event in ordered:
                idx = step_index[event.event_name]
                if idx > max_index + 1:
                    broken.append(
                        BrokenFunnelPath(
                            identity=identity,
                            skipped_step=step_names[max_index + 1] if max_index >= 0 else step_names[0],
                            reached_step=event.event_name,
                        )
                    )
                    break
                max_index = max(max_index, idx)
        return broken

    def compute_health_score(
        self,
        *,
        total_events: int,
        duplicate_groups: list[DuplicateMessageGroup],
        schema_error_count: int,
        missing_property_count: int,
        volume_anomaly_count: int,
        broken_funnel_paths: int,
    ) -> float:
        if total_events == 0:
            return 100.0

        duplicate_events = sum(max(0, g.count - 1) for g in duplicate_groups)
        dup_rate = duplicate_events / total_events
        schema_rate = schema_error_count / total_events
        missing_rate = missing_property_count / total_events
        anomaly_rate = volume_anomaly_count / max(len(duplicate_groups) or 1, 1)
        funnel_rate = broken_funnel_paths / total_events

        penalty = (
            min(25.0, dup_rate * 100 * 0.25)
            + min(25.0, schema_rate * 100 * 0.25)
            + min(20.0, missing_rate * 100 * 0.20)
            + min(15.0, anomaly_rate * 5)
            + min(15.0, funnel_rate * 100 * 0.15)
        )
        return round(max(0.0, min(100.0, 100.0 - penalty)), 2)

    def build_summary(
        self,
        *,
        total_events: int,
        duplicate_groups: list[DuplicateMessageGroup],
        schema_error_count: int,
        missing_property_count: int,
        volume_anomaly_count: int,
        broken_funnel_paths: int,
    ) -> QualityAuditSummary:
        health_score = self.compute_health_score(
            total_events=total_events,
            duplicate_groups=duplicate_groups,
            schema_error_count=schema_error_count,
            missing_property_count=missing_property_count,
            volume_anomaly_count=volume_anomaly_count,
            broken_funnel_paths=broken_funnel_paths,
        )
        duplicate_events = sum(max(0, g.count - 1) for g in duplicate_groups)
        return QualityAuditSummary(
            total_events=total_events,
            duplicate_groups=len(duplicate_groups),
            duplicate_events=duplicate_events,
            schema_error_count=schema_error_count,
            missing_property_count=missing_property_count,
            volume_anomaly_count=volume_anomaly_count,
            broken_funnel_paths=broken_funnel_paths,
            health_score=health_score,
        )

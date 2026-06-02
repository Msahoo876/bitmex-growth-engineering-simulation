"""Unit tests for retention and cohort engine."""

from datetime import UTC, datetime

from app.domain.funnels import RETENTION_ACTIVITY_EVENTS
from app.repositories.analytics_repository import UserEventRecord
from app.services.analytics.retention_engine import RetentionAnalyticsEngine


def _record(identity: str, event_name: str, day: int) -> UserEventRecord:
    return UserEventRecord(
        identity=identity,
        event_name=event_name,
        timestamp=datetime(2026, 6, day, 12, 0, tzinfo=UTC),
        user_id=None,
        anonymous_id=identity,
    )


class TestRetentionAnalyticsEngine:
    def test_d1_retention(self) -> None:
        engine = RetentionAnalyticsEngine()
        anchor = [_record("user:a", "user_signed_up", 1)]
        activity = [
            _record("user:a", "user_signed_up", 1),
            _record("user:a", "user_logged_in", 2),
            _record("user:b", "user_signed_up", 1),
        ]
        result = engine.compute_retention(
            anchor_event="user_signed_up",
            activity_events=RETENTION_ACTIVITY_EVENTS,
            anchor_records=anchor + [_record("user:b", "user_signed_up", 1)],
            activity_records=activity,
            retention_days=(1,),
        )
        assert result.cohort_size == 2
        assert result.periods[0].retained_users == 1
        assert result.periods[0].retention_rate == 50.0

    def test_cohort_rows(self) -> None:
        engine = RetentionAnalyticsEngine()
        anchor = [
            _record("user:a", "user_signed_up", 1),
            _record("user:b", "user_signed_up", 3),
        ]
        activity = [
            _record("user:a", "user_logged_in", 2),
            _record("user:b", "trade_opened", 10),
        ]
        result = engine.compute_cohorts(
            anchor_event="user_signed_up",
            activity_events=RETENTION_ACTIVITY_EVENTS,
            anchor_records=anchor,
            activity_records=activity,
        )
        assert len(result.cohorts) == 2

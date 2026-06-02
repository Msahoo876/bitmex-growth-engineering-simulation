"""Unit tests for data quality engine."""

from datetime import UTC, date, datetime

from app.domain.funnels import DEFAULT_FUNNEL_STEPS
from app.repositories.quality_repository import DuplicateMessageGroup, StoredEventAuditRow
from app.services.quality.quality_engine import DataQualityEngine


def _event(
    event_id: str,
    event_name: str,
    *,
    properties: dict | None = None,
    user_id=None,
    anonymous_id: str | None = "anon1",
    hour: int = 0,
) -> StoredEventAuditRow:
    return StoredEventAuditRow(
        id=user_id or event_id,
        event_id=event_id,
        event_name=event_name,
        event_type="track",
        message_id=f"msg-{event_id}",
        user_id=user_id,
        anonymous_id=anonymous_id,
        properties=properties,
        timestamp=datetime(2026, 6, 1, hour, 0, tzinfo=UTC),
    )


class TestDataQualityEngine:
    def test_missing_properties_detection(self) -> None:
        engine = DataQualityEngine()
        events = [
            _event("e1", "trade_opened", properties={}),
            _event("e2", "trade_opened", properties={"symbol": "BTCUSDT"}),
        ]
        issues = engine.detect_missing_properties(events)
        assert len(issues) == 1
        assert issues[0].missing_fields == ["symbol"]

    def test_broken_funnel_path(self) -> None:
        engine = DataQualityEngine()
        events = [
            _event("e1", "landing_page_viewed", hour=0),
            _event("e2", "kyc_completed", hour=2),
        ]
        broken = engine.detect_broken_funnel_paths(events, list(DEFAULT_FUNNEL_STEPS))
        assert len(broken) == 1
        assert broken[0].reached_step == "kyc_completed"

    def test_volume_anomaly_detection(self) -> None:
        engine = DataQualityEngine()
        daily = {
            date(2026, 6, 1): 100,
            date(2026, 6, 2): 110,
            date(2026, 6, 3): 20,
        }
        anomalies = engine.detect_volume_anomalies(daily)
        assert len(anomalies) >= 1

    def test_health_score_penalizes_issues(self) -> None:
        engine = DataQualityEngine()
        score = engine.compute_health_score(
            total_events=100,
            duplicate_groups=[DuplicateMessageGroup("m1", 3, ["a", "b", "c"])],
            schema_error_count=10,
            missing_property_count=5,
            volume_anomaly_count=2,
            broken_funnel_paths=4,
        )
        assert 0.0 <= score < 100.0

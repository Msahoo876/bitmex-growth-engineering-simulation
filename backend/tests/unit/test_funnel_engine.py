"""Unit tests for funnel analytics engine."""

from datetime import UTC, datetime

from app.domain.funnels import DEFAULT_FUNNEL_STEPS
from app.repositories.analytics_repository import UserEventRecord
from app.services.analytics.funnel_engine import FunnelAnalyticsEngine


def _record(identity: str, event_name: str, hour: int) -> UserEventRecord:
    return UserEventRecord(
        identity=identity,
        event_name=event_name,
        timestamp=datetime(2026, 6, 1, hour, 0, tzinfo=UTC),
        user_id=None,
        anonymous_id=identity,
    )


class TestFunnelAnalyticsEngine:
    def test_full_funnel_user_counts(self) -> None:
        engine = FunnelAnalyticsEngine()
        grouped = {
            "user:a": [
                _record("user:a", "landing_page_viewed", 0),
                _record("user:a", "user_signed_up", 1),
                _record("user:a", "kyc_completed", 2),
                _record("user:a", "deposit_completed", 3),
                _record("user:a", "trade_opened", 4),
            ],
            "user:b": [
                _record("user:b", "landing_page_viewed", 0),
                _record("user:b", "user_signed_up", 1),
            ],
        }
        result = engine.compute_funnel(
            funnel_name="test",
            step_definitions=list(DEFAULT_FUNNEL_STEPS),
            grouped_events=grouped,
        )
        assert result.steps[0].users == 2
        assert result.steps[1].users == 2
        assert result.steps[2].users == 1
        assert result.total_completed == 1
        assert result.completion_rate == 50.0

    def test_dropoff_largest_step(self) -> None:
        engine = FunnelAnalyticsEngine()
        grouped = {
            "user:a": [
                _record("user:a", "landing_page_viewed", 0),
                _record("user:a", "user_signed_up", 1),
            ],
            "user:b": [
                _record("user:b", "landing_page_viewed", 0),
            ],
        }
        funnel = engine.compute_funnel(
            funnel_name="test",
            step_definitions=list(DEFAULT_FUNNEL_STEPS[:2]),
            grouped_events=grouped,
        )
        dropoff = engine.compute_dropoff(funnel)
        assert dropoff.steps[0].users_lost == 1
        assert dropoff.largest_dropoff_step == "landing"

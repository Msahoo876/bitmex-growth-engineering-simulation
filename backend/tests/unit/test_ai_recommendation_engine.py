"""Unit tests for deterministic AI insight fallback."""

from app.services.ai.recommendation_engine import RecommendationEngine


class TestRecommendationEngine:
    def test_executive_summary_uses_structured_metrics(self) -> None:
        metrics = {
            "funnel": {"completion_rate": 12.5},
            "quality": {"health_score": 97.2},
            "attribution": {"top_source": "telegram"},
        }

        draft = RecommendationEngine().build("executive", metrics)

        assert draft.title == "Executive growth summary"
        assert "97.2" in draft.summary
        assert "12.5" in draft.summary
        assert "telegram" in draft.summary
        assert draft.recommendations

    def test_quality_priority_increases_when_health_score_is_low(self) -> None:
        metrics = {
            "quality": {
                "health_score": 72.0,
                "summary": {"duplicate_events": 5, "schema_error_count": 3},
            }
        }

        draft = RecommendationEngine().build("quality", metrics)

        assert draft.priority == "high"
        assert "72.0" in draft.summary

"""Unit tests for event health score calculation."""

from app.services.event_health_service import EventHealthService


def test_health_score_perfect_when_no_ingestion() -> None:
    score = EventHealthService._compute_health_score(
        acceptance_rate=100.0,
        duplicate_events=0,
        total_ingested=0,
        invalid_count=0,
    )
    assert score == 100.0


def test_health_score_penalizes_invalid_and_duplicates() -> None:
    score = EventHealthService._compute_health_score(
        acceptance_rate=80.0,
        duplicate_events=10,
        total_ingested=100,
        invalid_count=20,
    )
    assert 0.0 <= score <= 100.0
    assert score < 80.0

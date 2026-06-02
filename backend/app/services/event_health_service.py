"""Event health metrics derived from validation logs and stored events."""

import logging
from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.repositories.event_repository import EventRepository
from app.repositories.event_validation_log_repository import EventValidationLogRepository
from app.schemas.event_health import EventHealthMetrics, ValidationBreakdownItem
from app.services.event_validator import ValidationCode

logger = logging.getLogger(__name__)


class EventHealthService:
    def __init__(self, session: Session) -> None:
        self._events = EventRepository(session)
        self._validation_logs = EventValidationLogRepository(session)

    def get_health_metrics(self, *, period_hours: int = 24) -> EventHealthMetrics:
        since = datetime.now(UTC) - timedelta(hours=period_hours)

        valid_count = self._validation_logs.count_since(since, is_valid=True)
        invalid_count = self._validation_logs.count_since(since, is_valid=False)
        total_ingested = valid_count + invalid_count

        code_breakdown = self._validation_logs.count_by_code_since(since)
        duplicate_events = code_breakdown.get(ValidationCode.DUPLICATE_EVENT.value, 0)

        acceptance_rate = (valid_count / total_ingested * 100) if total_ingested else 100.0
        events_by_name = self._events.count_by_event_name_since(since)
        health_score = self._compute_health_score(
            acceptance_rate=acceptance_rate,
            duplicate_events=duplicate_events,
            total_ingested=total_ingested,
            invalid_count=invalid_count,
        )

        logger.info(
            "Event health computed period_hours=%s score=%.2f acceptance=%.2f%%",
            period_hours,
            health_score,
            acceptance_rate,
        )

        return EventHealthMetrics(
            period_hours=period_hours,
            total_ingested=total_ingested,
            valid_events=valid_count,
            invalid_events=invalid_count,
            acceptance_rate=round(acceptance_rate, 2),
            duplicate_events=duplicate_events,
            events_by_name=events_by_name,
            validation_breakdown=[
                ValidationBreakdownItem(code=code, count=count)
                for code, count in sorted(code_breakdown.items())
            ],
            health_score=round(health_score, 2),
        )

    @staticmethod
    def _compute_health_score(
        *,
        acceptance_rate: float,
        duplicate_events: int,
        total_ingested: int,
        invalid_count: int,
    ) -> float:
        if total_ingested == 0:
            return 100.0

        duplicate_penalty = min(30.0, (duplicate_events / total_ingested) * 100 * 0.3)
        invalid_penalty = min(40.0, (invalid_count / total_ingested) * 100 * 0.4)
        score = acceptance_rate - duplicate_penalty - invalid_penalty
        return max(0.0, min(100.0, score))

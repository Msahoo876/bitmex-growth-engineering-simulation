"""Persistence for data quality health score snapshots."""

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.health_score import HealthScore
from app.repositories.base import BaseRepository


class HealthScoreRepository(BaseRepository[HealthScore]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, HealthScore)

    def save_score(
        self,
        *,
        score: float,
        period_start: datetime,
        period_end: datetime,
        breakdown: dict[str, Any],
        check_type: str = "data_quality",
    ) -> HealthScore:
        record = HealthScore(
            score=score,
            period_start=period_start,
            period_end=period_end,
            breakdown=breakdown,
            check_type=check_type,
        )
        return self.add(record)

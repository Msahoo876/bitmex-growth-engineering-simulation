"""Persist precomputed analytics snapshots."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.analytics_snapshot import AnalyticsSnapshot
from app.repositories.base import BaseRepository


class AnalyticsSnapshotRepository(BaseRepository[AnalyticsSnapshot]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, AnalyticsSnapshot)

    def save_snapshot(
        self,
        *,
        snapshot_type: str,
        period_start: datetime,
        period_end: datetime,
        metrics: dict[str, Any],
    ) -> AnalyticsSnapshot:
        snapshot = AnalyticsSnapshot(
            snapshot_type=snapshot_type,
            period_start=period_start,
            period_end=period_end,
            metrics=metrics,
        )
        return self.add(snapshot)

    def get_latest(
        self,
        snapshot_type: str,
        *,
        period_start: datetime | None = None,
        period_end: datetime | None = None,
    ) -> AnalyticsSnapshot | None:
        stmt = (
            select(AnalyticsSnapshot)
            .where(AnalyticsSnapshot.snapshot_type == snapshot_type)
            .order_by(AnalyticsSnapshot.created_at.desc())
            .limit(1)
        )
        if period_start is not None:
            stmt = stmt.where(AnalyticsSnapshot.period_start == period_start)
        if period_end is not None:
            stmt = stmt.where(AnalyticsSnapshot.period_end == period_end)
        return self._session.scalars(stmt).first()

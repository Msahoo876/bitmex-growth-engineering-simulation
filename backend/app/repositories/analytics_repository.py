"""Analytics queries over the events table."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.event import Event


@dataclass(frozen=True)
class UserEventRecord:
    """Normalized event row for analytics computation."""

    identity: str
    event_name: str
    timestamp: datetime
    user_id: UUID | None
    anonymous_id: str | None


class AnalyticsRepository:
    """Read-only analytics access to raw events."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_events_for_steps(
        self,
        *,
        event_names: list[str],
        period_start: datetime,
        period_end: datetime,
    ) -> list[UserEventRecord]:
        if not event_names:
            return []

        stmt = (
            select(
                Event.user_id,
                Event.anonymous_id,
                Event.event_name,
                Event.timestamp,
            )
            .where(
                Event.event_name.in_(event_names),
                Event.timestamp >= period_start,
                Event.timestamp <= period_end,
            )
            .order_by(Event.timestamp.asc())
        )
        rows = self._session.execute(stmt).all()
        records: list[UserEventRecord] = []
        for user_id, anonymous_id, event_name, timestamp in rows:
            identity = self._build_identity(user_id, anonymous_id)
            if identity is None:
                continue
            records.append(
                UserEventRecord(
                    identity=identity,
                    event_name=event_name,
                    timestamp=timestamp,
                    user_id=user_id,
                    anonymous_id=anonymous_id,
                )
            )
        return records

    def fetch_anchor_events(
        self,
        *,
        anchor_event: str,
        period_start: datetime,
        period_end: datetime,
    ) -> list[UserEventRecord]:
        return self.fetch_events_for_steps(
            event_names=[anchor_event],
            period_start=period_start,
            period_end=period_end,
        )

    def fetch_activity_events(
        self,
        *,
        activity_events: list[str],
        period_start: datetime,
        period_end: datetime,
    ) -> list[UserEventRecord]:
        return self.fetch_events_for_steps(
            event_names=activity_events,
            period_start=period_start,
            period_end=period_end,
        )

    @staticmethod
    def _build_identity(user_id: UUID | None, anonymous_id: str | None) -> str | None:
        if user_id is not None:
            return f"user:{user_id}"
        if anonymous_id:
            return f"anon:{anonymous_id}"
        return None

    @staticmethod
    def group_events_by_identity(records: list[UserEventRecord]) -> dict[str, list[UserEventRecord]]:
        grouped: dict[str, list[UserEventRecord]] = {}
        for record in records:
            grouped.setdefault(record.identity, []).append(record)
        return grouped

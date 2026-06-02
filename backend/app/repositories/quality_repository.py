"""Repository for data quality audits over events and validation logs."""

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.models.event_validation_log import EventValidationLog


@dataclass(frozen=True)
class StoredEventAuditRow:
    id: UUID
    event_id: str
    event_name: str
    event_type: str
    message_id: str | None
    user_id: UUID | None
    anonymous_id: str | None
    properties: dict[str, Any] | None
    timestamp: datetime


@dataclass(frozen=True)
class DuplicateMessageGroup:
    message_id: str
    count: int
    event_ids: list[str]


class QualityRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_events(self, *, period_start: datetime, period_end: datetime) -> int:
        stmt = select(func.count()).select_from(Event).where(
            Event.timestamp >= period_start,
            Event.timestamp <= period_end,
        )
        return int(self._session.scalar(stmt) or 0)

    def fetch_events_for_audit(
        self, *, period_start: datetime, period_end: datetime
    ) -> list[StoredEventAuditRow]:
        stmt = (
            select(Event)
            .where(Event.timestamp >= period_start, Event.timestamp <= period_end)
            .order_by(Event.timestamp.asc())
        )
        events = list(self._session.scalars(stmt).all())
        return [
            StoredEventAuditRow(
                id=e.id,
                event_id=e.event_id,
                event_name=e.event_name,
                event_type=e.event_type,
                message_id=e.message_id,
                user_id=e.user_id,
                anonymous_id=e.anonymous_id,
                properties=e.properties,
                timestamp=e.timestamp,
            )
            for e in events
        ]

    def find_duplicate_message_ids_from_logs(
        self, *, period_start: datetime, period_end: datetime
    ) -> list[DuplicateMessageGroup]:
        stmt = (
            select(EventValidationLog.message_id, func.count())
            .where(
                EventValidationLog.created_at >= period_start,
                EventValidationLog.created_at <= period_end,
                EventValidationLog.validation_code == "duplicate_event",
                EventValidationLog.message_id.is_not(None),
            )
            .group_by(EventValidationLog.message_id)
        )
        rows = self._session.execute(stmt).all()
        return [
            DuplicateMessageGroup(message_id=msg_id, count=int(count), event_ids=[])
            for msg_id, count in rows
        ]

    def find_duplicate_message_ids(
        self, *, period_start: datetime, period_end: datetime
    ) -> list[DuplicateMessageGroup]:
        groups: dict[str, list[str]] = {}
        for row in self.fetch_events_for_audit(period_start=period_start, period_end=period_end):
            if not row.message_id:
                continue
            groups.setdefault(row.message_id, []).append(row.event_id)
        return [
            DuplicateMessageGroup(message_id=mid, count=len(ids), event_ids=ids)
            for mid, ids in groups.items()
            if len(ids) > 1
        ]

    def schema_errors_from_logs(
        self, *, period_start: datetime, period_end: datetime
    ) -> list[dict[str, Any]]:
        codes = ("invalid_schema", "unknown_event_name", "required_field_missing")
        stmt = (
            select(EventValidationLog)
            .where(
                EventValidationLog.created_at >= period_start,
                EventValidationLog.created_at <= period_end,
                EventValidationLog.is_valid.is_(False),
                EventValidationLog.validation_code.in_(codes),
            )
            .order_by(EventValidationLog.created_at.desc())
            .limit(500)
        )
        logs = list(self._session.scalars(stmt).all())
        return [
            {
                "validation_code": log.validation_code,
                "event_name": log.event_name,
                "message_id": log.message_id,
                "message": log.validation_message,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ]

    def validation_counts_by_code(
        self, *, period_start: datetime, period_end: datetime
    ) -> dict[str, int]:
        stmt = (
            select(EventValidationLog.validation_code, func.count())
            .where(
                EventValidationLog.created_at >= period_start,
                EventValidationLog.created_at <= period_end,
                EventValidationLog.is_valid.is_(False),
            )
            .group_by(EventValidationLog.validation_code)
        )
        rows = self._session.execute(stmt).all()
        return {code: int(count) for code, count in rows}

    def daily_event_volume(
        self, *, period_start: datetime, period_end: datetime
    ) -> dict[date, int]:
        events = self.fetch_events_for_audit(period_start=period_start, period_end=period_end)
        counts: dict[date, int] = {}
        for event in events:
            day = event.timestamp.date()
            counts[day] = counts.get(day, 0) + 1
        return counts

    def fetch_funnel_events(
        self,
        *,
        event_names: list[str],
        period_start: datetime,
        period_end: datetime,
    ) -> list[StoredEventAuditRow]:
        stmt = (
            select(Event)
            .where(
                Event.event_name.in_(event_names),
                Event.timestamp >= period_start,
                Event.timestamp <= period_end,
            )
            .order_by(Event.timestamp.asc())
        )
        events = list(self._session.scalars(stmt).all())
        return [
            StoredEventAuditRow(
                id=e.id,
                event_id=e.event_id,
                event_name=e.event_name,
                event_type=e.event_type,
                message_id=e.message_id,
                user_id=e.user_id,
                anonymous_id=e.anonymous_id,
                properties=e.properties,
                timestamp=e.timestamp,
            )
            for e in events
        ]

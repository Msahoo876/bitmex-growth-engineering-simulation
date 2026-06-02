"""Event persistence and explorer queries."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.event import Event
from app.repositories.base import BaseRepository


class EventRepository(BaseRepository[Event]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Event)

    def get_by_event_id(self, event_id: str) -> Event | None:
        stmt = select(Event).where(Event.event_id == event_id)
        return self._session.scalars(stmt).first()

    def get_by_message_id(self, message_id: str) -> Event | None:
        stmt = select(Event).where(Event.message_id == message_id)
        return self._session.scalars(stmt).first()

    def message_id_exists(self, message_id: str) -> bool:
        return self.get_by_message_id(message_id) is not None

    def search(
        self,
        *,
        event_name: str | None = None,
        event_type: str | None = None,
        user_id: UUID | None = None,
        anonymous_id: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Event], int]:
        stmt = select(Event)
        count_stmt = select(func.count()).select_from(Event)

        if event_name:
            stmt = stmt.where(Event.event_name == event_name)
            count_stmt = count_stmt.where(Event.event_name == event_name)
        if event_type:
            stmt = stmt.where(Event.event_type == event_type)
            count_stmt = count_stmt.where(Event.event_type == event_type)
        if user_id:
            stmt = stmt.where(Event.user_id == user_id)
            count_stmt = count_stmt.where(Event.user_id == user_id)
        if anonymous_id:
            stmt = stmt.where(Event.anonymous_id == anonymous_id)
            count_stmt = count_stmt.where(Event.anonymous_id == anonymous_id)
        if from_timestamp:
            stmt = stmt.where(Event.timestamp >= from_timestamp)
            count_stmt = count_stmt.where(Event.timestamp >= from_timestamp)
        if to_timestamp:
            stmt = stmt.where(Event.timestamp <= to_timestamp)
            count_stmt = count_stmt.where(Event.timestamp <= to_timestamp)

        total = int(self._session.scalar(count_stmt) or 0)
        stmt = stmt.order_by(Event.timestamp.desc()).limit(limit).offset(offset)
        events = list(self._session.scalars(stmt).all())
        return events, total

    def count_since(self, since: datetime) -> int:
        stmt = select(func.count()).select_from(Event).where(Event.timestamp >= since)
        return int(self._session.scalar(stmt) or 0)

    def count_by_event_name_since(self, since: datetime) -> dict[str, int]:
        stmt = (
            select(Event.event_name, func.count())
            .where(Event.timestamp >= since)
            .group_by(Event.event_name)
        )
        rows = self._session.execute(stmt).all()
        return {name: int(count) for name, count in rows}

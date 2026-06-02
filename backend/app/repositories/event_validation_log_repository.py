"""Persistence for event validation outcomes."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.event_validation_log import EventValidationLog
from app.repositories.base import BaseRepository


class EventValidationLogRepository(BaseRepository[EventValidationLog]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, EventValidationLog)

    def create_log(
        self,
        *,
        event_id: UUID | None,
        message_id: str | None,
        event_name: str | None,
        is_valid: bool,
        validation_code: str,
        validation_message: str,
    ) -> EventValidationLog:
        log = EventValidationLog(
            event_id=event_id,
            message_id=message_id,
            event_name=event_name,
            is_valid=is_valid,
            validation_code=validation_code,
            validation_message=validation_message,
        )
        return self.add(log)

    def message_id_logged(self, message_id: str) -> bool:
        stmt = select(EventValidationLog.id).where(
            EventValidationLog.message_id == message_id
        ).limit(1)
        return self._session.scalars(stmt).first() is not None

    def is_duplicate_message(self, message_id: str) -> bool:
        return self.message_id_logged(message_id)

    def count_since(self, since: datetime, *, is_valid: bool | None = None) -> int:
        stmt = select(func.count()).select_from(EventValidationLog).where(
            EventValidationLog.created_at >= since
        )
        if is_valid is not None:
            stmt = stmt.where(EventValidationLog.is_valid == is_valid)
        return int(self._session.scalar(stmt) or 0)

    def count_by_code_since(self, since: datetime) -> dict[str, int]:
        stmt = (
            select(EventValidationLog.validation_code, func.count())
            .where(EventValidationLog.created_at >= since)
            .group_by(EventValidationLog.validation_code)
        )
        rows = self._session.execute(stmt).all()
        return {code: int(count) for code, count in rows}

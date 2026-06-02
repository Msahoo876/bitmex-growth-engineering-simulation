"""Event explorer — search and retrieve stored events."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ResourceNotFoundError
from app.repositories.event_repository import EventRepository
from app.repositories.user_repository import UserRepository
from app.schemas.events import EventExplorerResponse, EventRecordSchema

logger = logging.getLogger(__name__)


class EventExplorerService:
    def __init__(self, session: Session) -> None:
        self._events = EventRepository(session)
        self._users = UserRepository(session)

    def search(
        self,
        *,
        event_name: str | None = None,
        event_type: str | None = None,
        user_external_id: str | None = None,
        anonymous_id: str | None = None,
        from_timestamp: datetime | None = None,
        to_timestamp: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> EventExplorerResponse:
        user_uuid: UUID | None = None
        if user_external_id:
            user = self._users.get_by_external_id(user_external_id)
            if user:
                user_uuid = user.id

        events, total = self._events.search(
            event_name=event_name,
            event_type=event_type,
            user_id=user_uuid,
            anonymous_id=anonymous_id,
            from_timestamp=from_timestamp,
            to_timestamp=to_timestamp,
            limit=limit,
            offset=offset,
        )

        logger.debug("Event explorer returned %s/%s events", len(events), total)
        return EventExplorerResponse(
            total=total,
            limit=limit,
            offset=offset,
            events=[EventRecordSchema.model_validate(e) for e in events],
        )

    def get_by_event_id(self, event_id: str) -> EventRecordSchema:
        event = self._events.get_by_event_id(event_id)
        if event is None:
            raise ResourceNotFoundError(f"Event '{event_id}' not found.")
        return EventRecordSchema.model_validate(event)

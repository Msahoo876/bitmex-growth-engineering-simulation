"""Event tracking service — identify, track, page ingestion."""

import logging
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.event import Event
from app.repositories.event_repository import EventRepository
from app.repositories.event_validation_log_repository import EventValidationLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.events import (
    EventIngestResponse,
    IdentifyRequest,
    PageRequest,
    TrackRequest,
    ValidationIssueSchema,
)
from app.services.event_validator import EventValidator, ValidationCode, ValidationResult

logger = logging.getLogger(__name__)


class EventTrackingService:
    """Orchestrates validation, user resolution, and event persistence."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._events = EventRepository(session)
        self._users = UserRepository(session)
        self._validation_logs = EventValidationLogRepository(session)
        self._validator = EventValidator()

    def track(self, payload: TrackRequest) -> EventIngestResponse:
        message_id = payload.message_id or self._generate_message_id()
        is_duplicate = self._is_duplicate(message_id)

        validation = self._validator.validate_track(
            event_name=payload.event,
            user_id=payload.user_id,
            anonymous_id=payload.anonymous_id,
            timestamp=payload.timestamp,
            message_id=message_id,
            properties=payload.properties,
            is_duplicate=is_duplicate,
        )

        if not validation.is_valid:
            self._log_validation(
                validation=validation,
                message_id=message_id,
                event_name=payload.event,
            )
            self._session.commit()
            logger.warning("Track rejected: %s", validation.issues)
            return self._build_response(success=False, message_id=message_id, validation=validation)

        email = None
        if payload.properties and isinstance(payload.properties.get("email"), str):
            email = payload.properties["email"]
        user = self._resolve_user(payload.user_id, payload.anonymous_id, email)
        event = self._persist_event(
            event_name=payload.event,
            event_type="track",
            user=user,
            anonymous_id=payload.anonymous_id,
            properties=payload.properties,
            context=payload.context,
            timestamp=payload.timestamp,
            message_id=message_id,
        )
        self._log_validation(
            validation=validation,
            message_id=message_id,
            event_name=payload.event,
            event_db_id=event.id,
        )
        self._session.commit()
        logger.info("Track stored event_id=%s name=%s", event.event_id, event.event_name)
        return self._build_response(
            success=True, event_id=event.event_id, message_id=message_id, validation=validation
        )

    def identify(self, payload: IdentifyRequest) -> EventIngestResponse:
        message_id = payload.message_id or self._generate_message_id()
        is_duplicate = self._is_duplicate(message_id)

        validation = self._validator.validate_identify(
            user_id=payload.user_id,
            anonymous_id=payload.anonymous_id,
            traits=payload.traits,
            timestamp=payload.timestamp,
            message_id=message_id,
            is_duplicate=is_duplicate,
        )

        if not validation.is_valid:
            self._log_validation(
                validation=validation,
                message_id=message_id,
                event_name="identify",
            )
            self._session.commit()
            logger.warning("Identify rejected: %s", validation.issues)
            return self._build_response(success=False, message_id=message_id, validation=validation)

        email = None
        if payload.traits and isinstance(payload.traits.get("email"), str):
            email = payload.traits["email"]

        user = self._users.upsert_identify(
            external_id=payload.user_id,
            anonymous_id=payload.anonymous_id,
            email=email,
            traits=payload.traits,
        )

        event = self._persist_event(
            event_name="identify",
            event_type="identify",
            user=user,
            anonymous_id=payload.anonymous_id,
            properties=payload.traits,
            context=payload.context,
            timestamp=payload.timestamp,
            message_id=message_id,
        )
        self._log_validation(
            validation=validation,
            message_id=message_id,
            event_name="identify",
            event_db_id=event.id,
        )
        self._session.commit()
        logger.info("Identify stored for user=%s", payload.user_id)
        return self._build_response(
            success=True, event_id=event.event_id, message_id=message_id, validation=validation
        )

    def page(self, payload: PageRequest) -> EventIngestResponse:
        message_id = payload.message_id or self._generate_message_id()
        is_duplicate = self._is_duplicate(message_id)

        validation = self._validator.validate_page(
            name=payload.name,
            user_id=payload.user_id,
            anonymous_id=payload.anonymous_id,
            timestamp=payload.timestamp,
            message_id=message_id,
            properties=payload.properties,
            is_duplicate=is_duplicate,
        )

        if not validation.is_valid:
            self._log_validation(
                validation=validation,
                message_id=message_id,
                event_name="page",
            )
            self._session.commit()
            logger.warning("Page rejected: %s", validation.issues)
            return self._build_response(success=False, message_id=message_id, validation=validation)

        user = self._resolve_user(payload.user_id, payload.anonymous_id)
        page_url = payload.url
        if not page_url and payload.properties:
            page_url = payload.properties.get("url") or payload.properties.get("path")

        properties = dict(payload.properties or {})
        properties.setdefault("page_name", payload.name)
        if payload.title:
            properties.setdefault("title", payload.title)

        event = self._persist_event(
            event_name="page",
            event_type="page",
            user=user,
            anonymous_id=payload.anonymous_id,
            properties=properties,
            context=payload.context,
            timestamp=payload.timestamp,
            message_id=message_id,
            page_name=payload.name,
            page_url=page_url,
        )
        self._log_validation(
            validation=validation,
            message_id=message_id,
            event_name="page",
            event_db_id=event.id,
        )
        self._session.commit()
        logger.info("Page stored event_id=%s page=%s", event.event_id, payload.name)
        return self._build_response(
            success=True, event_id=event.event_id, message_id=message_id, validation=validation
        )

    def _resolve_user(
        self,
        user_id: str | None,
        anonymous_id: str | None,
        email: str | None = None,
    ) -> Any:
        if user_id:
            existing = self._users.get_by_external_id(user_id)
            if existing:
                if anonymous_id and not existing.anonymous_id:
                    existing.anonymous_id = anonymous_id
                return existing
            return self._users.upsert_identify(
                external_id=user_id,
                anonymous_id=anonymous_id,
                email=email,
                traits=None,
            )
        if anonymous_id:
            return self._users.get_by_anonymous_id(anonymous_id)
        return None

    def _persist_event(
        self,
        *,
        event_name: str,
        event_type: str,
        user: Any,
        anonymous_id: str | None,
        properties: dict[str, Any] | None,
        context: dict[str, Any] | None,
        timestamp: datetime | None,
        message_id: str,
        page_name: str | None = None,
        page_url: str | None = None,
    ) -> Event:
        ts = timestamp or datetime.now(UTC)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=UTC)

        event = Event(
            event_id=uuid.uuid4().hex,
            event_name=event_name,
            event_type=event_type,
            user_id=user.id if user else None,
            anonymous_id=anonymous_id,
            properties=properties or {},
            context=context or {},
            timestamp=ts,
            message_id=message_id,
            page_name=page_name,
            page_url=page_url,
        )
        return self._events.add(event)

    def _is_duplicate(self, message_id: str) -> bool:
        return (
            self._events.message_id_exists(message_id)
            or self._validation_logs.is_duplicate_message(message_id)
        )

    def _log_validation(
        self,
        *,
        validation: ValidationResult,
        message_id: str,
        event_name: str | None,
        event_db_id: Any = None,
    ) -> None:
        if validation.is_valid:
            self._validation_logs.create_log(
                event_id=event_db_id,
                message_id=message_id,
                event_name=event_name,
                is_valid=True,
                validation_code="valid",
                validation_message="Event passed validation.",
            )
            return

        for issue in validation.issues:
            self._validation_logs.create_log(
                event_id=event_db_id,
                message_id=message_id,
                event_name=event_name,
                is_valid=False,
                validation_code=issue.code.value,
                validation_message=issue.message,
            )

    @staticmethod
    def _generate_message_id() -> str:
        return f"msg_{uuid.uuid4().hex}"

    @staticmethod
    def _build_response(
        *,
        success: bool,
        event_id: str | None = None,
        message_id: str | None = None,
        validation: ValidationResult,
    ) -> EventIngestResponse:
        return EventIngestResponse(
            success=success,
            event_id=event_id,
            message_id=message_id,
            validation=[
                ValidationIssueSchema(code=i.code.value, message=i.message)
                for i in validation.issues
            ],
        )


# Helper on TrackRequest - I referenced payload.traits_email() which doesn't exist
# Fix: remove that call

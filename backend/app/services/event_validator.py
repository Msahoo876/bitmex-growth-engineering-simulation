"""Event validation layer — required fields, taxonomy, duplicates, timestamps."""

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from app.domain.event_taxonomy import is_known_event


class ValidationCode(StrEnum):
    REQUIRED_FIELD_MISSING = "required_field_missing"
    DUPLICATE_EVENT = "duplicate_event"
    MISSING_USER_ID = "missing_user_id"
    INVALID_TIMESTAMP = "invalid_timestamp"
    INVALID_SCHEMA = "invalid_schema"
    UNKNOWN_EVENT_NAME = "unknown_event_name"


@dataclass
class ValidationIssue:
    code: ValidationCode
    message: str


@dataclass
class ValidationResult:
    is_valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)

    @property
    def primary_code(self) -> ValidationCode | None:
        return self.issues[0].code if self.issues else None


class EventValidator:
    """Validates inbound tracking payloads before persistence."""

    MAX_FUTURE_SKEW = timedelta(hours=24)
    MAX_PAST_AGE = timedelta(days=30)

    def validate_track(
        self,
        *,
        event_name: str | None,
        user_id: str | None,
        anonymous_id: str | None,
        timestamp: datetime | None,
        message_id: str | None,
        properties: dict[str, Any] | None,
        is_duplicate: bool,
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []

        if not event_name or not str(event_name).strip():
            issues.append(
                ValidationIssue(
                    code=ValidationCode.REQUIRED_FIELD_MISSING,
                    message="Field 'event' is required for track calls.",
                )
            )
        elif not is_known_event(event_name):
            issues.append(
                ValidationIssue(
                    code=ValidationCode.UNKNOWN_EVENT_NAME,
                    message=f"Event '{event_name}' is not in the tracking taxonomy.",
                )
            )

        if not user_id and not anonymous_id:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.MISSING_USER_ID,
                    message="Either userId or anonymousId is required.",
                )
            )

        issues.extend(self._validate_timestamp(timestamp))
        issues.extend(self._validate_properties_schema(properties))

        if message_id and is_duplicate:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.DUPLICATE_EVENT,
                    message=f"Duplicate messageId '{message_id}' already processed.",
                )
            )

        return ValidationResult(is_valid=len(issues) == 0, issues=issues)

    def validate_identify(
        self,
        *,
        user_id: str | None,
        anonymous_id: str | None,
        traits: dict[str, Any] | None,
        timestamp: datetime | None,
        message_id: str | None,
        is_duplicate: bool,
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []

        if not user_id or not str(user_id).strip():
            issues.append(
                ValidationIssue(
                    code=ValidationCode.REQUIRED_FIELD_MISSING,
                    message="Field 'userId' is required for identify calls.",
                )
            )

        issues.extend(self._validate_timestamp(timestamp))
        issues.extend(self._validate_properties_schema(traits))

        if message_id and is_duplicate:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.DUPLICATE_EVENT,
                    message=f"Duplicate messageId '{message_id}' already processed.",
                )
            )

        if not anonymous_id and not user_id:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.MISSING_USER_ID,
                    message="userId is required for identify.",
                )
            )

        return ValidationResult(is_valid=len(issues) == 0, issues=issues)

    def validate_page(
        self,
        *,
        name: str | None,
        user_id: str | None,
        anonymous_id: str | None,
        timestamp: datetime | None,
        message_id: str | None,
        properties: dict[str, Any] | None,
        is_duplicate: bool,
    ) -> ValidationResult:
        issues: list[ValidationIssue] = []

        if not name or not str(name).strip():
            issues.append(
                ValidationIssue(
                    code=ValidationCode.REQUIRED_FIELD_MISSING,
                    message="Field 'name' is required for page calls.",
                )
            )

        if not user_id and not anonymous_id:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.MISSING_USER_ID,
                    message="Either userId or anonymousId is required.",
                )
            )

        issues.extend(self._validate_timestamp(timestamp))
        issues.extend(self._validate_properties_schema(properties))

        if message_id and is_duplicate:
            issues.append(
                ValidationIssue(
                    code=ValidationCode.DUPLICATE_EVENT,
                    message=f"Duplicate messageId '{message_id}' already processed.",
                )
            )

        return ValidationResult(is_valid=len(issues) == 0, issues=issues)

    def _validate_timestamp(self, timestamp: datetime | None) -> list[ValidationIssue]:
        if timestamp is None:
            return []

        now = datetime.now(UTC)
        ts = timestamp if timestamp.tzinfo else timestamp.replace(tzinfo=UTC)

        if ts > now + self.MAX_FUTURE_SKEW:
            return [
                ValidationIssue(
                    code=ValidationCode.INVALID_TIMESTAMP,
                    message="Event timestamp is too far in the future.",
                )
            ]
        if ts < now - self.MAX_PAST_AGE:
            return [
                ValidationIssue(
                    code=ValidationCode.INVALID_TIMESTAMP,
                    message="Event timestamp is too far in the past.",
                )
            ]
        return []

    def _validate_properties_schema(
        self, payload: dict[str, Any] | None
    ) -> list[ValidationIssue]:
        if payload is None:
            return []
        if not isinstance(payload, dict):
            return [
                ValidationIssue(
                    code=ValidationCode.INVALID_SCHEMA,
                    message="Properties must be a JSON object.",
                )
            ]
        for key in payload:
            if not isinstance(key, str):
                return [
                    ValidationIssue(
                        code=ValidationCode.INVALID_SCHEMA,
                        message="Property keys must be strings.",
                    )
                ]
        return []

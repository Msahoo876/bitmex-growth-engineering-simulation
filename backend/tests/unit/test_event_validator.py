"""Unit tests for the event validation layer."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.event_validator import EventValidator, ValidationCode


@pytest.fixture
def validator() -> EventValidator:
    return EventValidator()


class TestTrackValidation:
    def test_valid_track_event(self, validator: EventValidator) -> None:
        result = validator.validate_track(
            event_name="trade_opened",
            user_id="user_1",
            anonymous_id=None,
            timestamp=datetime.now(UTC),
            message_id="msg-1",
            properties={"symbol": "BTCUSDT", "amount": 500},
            is_duplicate=False,
        )
        assert result.is_valid
        assert result.issues == []

    def test_unknown_event_name(self, validator: EventValidator) -> None:
        result = validator.validate_track(
            event_name="unknown_event",
            user_id="user_1",
            anonymous_id=None,
            timestamp=None,
            message_id=None,
            properties=None,
            is_duplicate=False,
        )
        assert not result.is_valid
        assert result.primary_code == ValidationCode.UNKNOWN_EVENT_NAME

    def test_missing_identity(self, validator: EventValidator) -> None:
        result = validator.validate_track(
            event_name="trade_opened",
            user_id=None,
            anonymous_id=None,
            timestamp=None,
            message_id=None,
            properties=None,
            is_duplicate=False,
        )
        assert not result.is_valid
        assert any(i.code == ValidationCode.MISSING_USER_ID for i in result.issues)

    def test_duplicate_message(self, validator: EventValidator) -> None:
        result = validator.validate_track(
            event_name="trade_opened",
            user_id="user_1",
            anonymous_id=None,
            timestamp=None,
            message_id="dup-msg",
            properties=None,
            is_duplicate=True,
        )
        assert not result.is_valid
        assert any(i.code == ValidationCode.DUPLICATE_EVENT for i in result.issues)

    def test_invalid_timestamp_future(self, validator: EventValidator) -> None:
        future = datetime.now(UTC) + timedelta(days=2)
        result = validator.validate_track(
            event_name="trade_opened",
            user_id="user_1",
            anonymous_id=None,
            timestamp=future,
            message_id=None,
            properties=None,
            is_duplicate=False,
        )
        assert not result.is_valid
        assert any(i.code == ValidationCode.INVALID_TIMESTAMP for i in result.issues)

    def test_invalid_properties_schema(self, validator: EventValidator) -> None:
        result = validator.validate_track(
            event_name="trade_opened",
            user_id="user_1",
            anonymous_id=None,
            timestamp=None,
            message_id=None,
            properties="not-a-dict",  # type: ignore[arg-type]
            is_duplicate=False,
        )
        assert not result.is_valid
        assert any(i.code == ValidationCode.INVALID_SCHEMA for i in result.issues)


class TestIdentifyValidation:
    def test_identify_requires_user_id(self, validator: EventValidator) -> None:
        result = validator.validate_identify(
            user_id=None,
            anonymous_id="anon_1",
            traits={},
            timestamp=None,
            message_id=None,
            is_duplicate=False,
        )
        assert not result.is_valid
        assert any(i.code == ValidationCode.REQUIRED_FIELD_MISSING for i in result.issues)


class TestPageValidation:
    def test_page_requires_name(self, validator: EventValidator) -> None:
        result = validator.validate_page(
            name="",
            user_id="user_1",
            anonymous_id=None,
            timestamp=None,
            message_id=None,
            properties=None,
            is_duplicate=False,
        )
        assert not result.is_valid
        assert any(i.code == ValidationCode.REQUIRED_FIELD_MISSING for i in result.issues)

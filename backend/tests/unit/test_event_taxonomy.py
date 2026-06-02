"""Unit tests for event taxonomy."""

from app.domain.event_taxonomy import EventCategory, get_event_category, is_known_event


def test_known_trading_events() -> None:
    assert is_known_event("trade_opened")
    assert is_known_event("trade_closed")
    assert get_event_category("trade_opened") == EventCategory.TRADING


def test_unknown_event() -> None:
    assert not is_known_event("random_event")


def test_system_events() -> None:
    assert is_known_event("identify")
    assert is_known_event("page")

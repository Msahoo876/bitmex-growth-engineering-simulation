"""Canonical event names from the Growth Engineering tracking plan."""

from enum import StrEnum


class EventCategory(StrEnum):
    USER = "user"
    FUNDING = "funding"
    TRADING = "trading"
    GROWTH = "growth"
    PRODUCT = "product"
    SYSTEM = "system"


EVENT_TAXONOMY: dict[EventCategory, frozenset[str]] = {
    EventCategory.USER: frozenset(
        {
            "user_signed_up",
            "user_logged_in",
            "email_verified",
            "kyc_started",
            "kyc_completed",
        }
    ),
    EventCategory.FUNDING: frozenset(
        {
            "deposit_started",
            "deposit_completed",
            "withdrawal_requested",
        }
    ),
    EventCategory.TRADING: frozenset(
        {
            "trade_opened",
            "trade_closed",
            "leverage_changed",
            "position_liquidated",
        }
    ),
    EventCategory.GROWTH: frozenset(
        {
            "referral_clicked",
            "campaign_clicked",
            "landing_page_viewed",
            "signup_from_campaign",
        }
    ),
    EventCategory.PRODUCT: frozenset(
        {
            "watchlist_created",
            "market_viewed",
            "asset_searched",
            "price_alert_created",
        }
    ),
    EventCategory.SYSTEM: frozenset(
        {
            "identify",
            "page",
        }
    ),
}

ALL_KNOWN_EVENTS: frozenset[str] = frozenset(
    name for names in EVENT_TAXONOMY.values() for name in names
)


def is_known_event(event_name: str) -> bool:
    return event_name in ALL_KNOWN_EVENTS


def get_event_category(event_name: str) -> EventCategory | None:
    for category, names in EVENT_TAXONOMY.items():
        if event_name in names:
            return category
    return None

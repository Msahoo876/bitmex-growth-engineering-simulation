"""Data quality rules for event auditing."""

from typing import Any

from app.domain.event_taxonomy import ALL_KNOWN_EVENTS

# Required JSON properties per event (business tracking plan)
REQUIRED_EVENT_PROPERTIES: dict[str, tuple[str, ...]] = {
    "trade_opened": ("symbol",),
    "trade_closed": ("symbol",),
    "deposit_completed": ("amount",),
    "deposit_started": ("amount",),
    "campaign_clicked": ("campaign",),
    "signup_from_campaign": ("campaign",),
    "referral_clicked": ("referral_code",),
    "landing_page_viewed": ("source",),
}

# Events that must have user_id or anonymous_id when stored
IDENTITY_REQUIRED_EVENT_TYPES: frozenset[str] = frozenset({"track", "page"})

# Volume anomaly: flag if daily count deviates more than this % from baseline mean
VOLUME_ANOMALY_THRESHOLD_PCT: float = 50.0

# Minimum events in period before anomaly detection applies
MIN_EVENTS_FOR_ANOMALY: int = 10


def is_valid_event_name(event_name: str) -> bool:
    return event_name in ALL_KNOWN_EVENTS


def missing_required_properties(
    event_name: str, properties: dict[str, Any] | None
) -> list[str]:
    required = REQUIRED_EVENT_PROPERTIES.get(event_name, ())
    if not required:
        return []
    props = properties or {}
    return [key for key in required if key not in props or props[key] in (None, "", [])]

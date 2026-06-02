"""Default and configurable funnel definitions."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class FunnelStepDefinition:
    """Single step in a conversion funnel."""

    key: str
    label: str
    event_name: str


DEFAULT_FUNNEL_NAME = "growth_default"
DEFAULT_FUNNEL_STEPS: tuple[FunnelStepDefinition, ...] = (
    FunnelStepDefinition("landing", "Landing Page", "landing_page_viewed"),
    FunnelStepDefinition("signup", "Signup", "user_signed_up"),
    FunnelStepDefinition("kyc", "KYC", "kyc_completed"),
    FunnelStepDefinition("deposit", "Deposit", "deposit_completed"),
    FunnelStepDefinition("trade", "Trade", "trade_opened"),
)

# Events that indicate an active user for retention calculations
RETENTION_ACTIVITY_EVENTS: frozenset[str] = frozenset(
    {
        "user_logged_in",
        "trade_opened",
        "deposit_completed",
        "market_viewed",
        "trade_closed",
    }
)

RETENTION_ANCHOR_EVENT = "user_signed_up"
RETENTION_DAYS: tuple[int, ...] = (1, 7, 30)


def default_funnel_steps_json() -> list[dict[str, Any]]:
    return [
        {"key": s.key, "label": s.label, "event_name": s.event_name}
        for s in DEFAULT_FUNNEL_STEPS
    ]


def parse_funnel_steps(raw_steps: list[dict[str, Any]]) -> list[FunnelStepDefinition]:
    steps: list[FunnelStepDefinition] = []
    for item in raw_steps:
        steps.append(
            FunnelStepDefinition(
                key=str(item["key"]),
                label=str(item.get("label", item["key"])),
                event_name=str(item["event_name"]),
            )
        )
    return steps

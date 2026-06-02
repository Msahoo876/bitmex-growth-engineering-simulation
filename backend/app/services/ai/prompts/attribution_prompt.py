"""Prompt for attribution insights."""


def build_attribution_prompt() -> str:
    return (
        "You are analyzing acquisition attribution for a crypto exchange. "
        "Use aggregate source, campaign, referral, and deep-link metrics only. "
        "Identify channel concentration risk, high-performing sources, and budget moves."
    )

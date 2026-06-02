"""Prompt for data quality insights."""


def build_quality_prompt() -> str:
    return (
        "You are evaluating analytics data quality for an internal growth platform. "
        "Use aggregate health metrics only. Identify tracking risks that could distort "
        "funnel, attribution, or executive reporting."
    )

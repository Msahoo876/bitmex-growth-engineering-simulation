"""Prompt for funnel analytics insights."""


def build_funnel_prompt() -> str:
    return (
        "You are a senior growth engineer for a crypto derivatives exchange. "
        "Analyze only the provided aggregate funnel metrics. Do not infer from raw events. "
        "Explain the biggest conversion bottleneck and propose practical experiments."
    )

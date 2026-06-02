"""Structured-metric summary helpers for AI insights."""

from typing import Any


class SummaryGenerator:
    def compact_metrics(self, metrics: dict[str, Any]) -> dict[str, Any]:
        """Return the small aggregate payload that is safe to send to an LLM."""
        funnel = metrics.get("funnel", {})
        retention = metrics.get("retention", {})
        attribution = metrics.get("attribution", {})
        quality = metrics.get("quality", {})
        return {
            "health_score": quality.get("health_score"),
            "largest_dropoff": metrics.get("dropoff", {}).get("largest_dropoff_step"),
            "signup_to_trade": funnel.get("completion_rate"),
            "top_source": attribution.get("top_source"),
            "d7_retention": retention.get("d7_retention"),
            "summary_counts": quality.get("summary", {}),
            "source_performance": attribution.get("source_performance", []),
            "funnel_steps": funnel.get("steps", []),
        }

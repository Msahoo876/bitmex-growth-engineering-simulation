"""Deterministic fallback recommendations for local and test environments."""

from typing import Any

from app.services.ai.providers.base_provider import AIInsightDraft


class RecommendationEngine:
    def build(self, insight_type: str, metrics: dict[str, Any]) -> AIInsightDraft:
        builders = {
            "funnel": self._funnel,
            "attribution": self._attribution,
            "quality": self._quality,
            "executive": self._executive,
            "recommendations": self._recommendations,
        }
        return builders.get(insight_type, self._executive)(metrics)

    def _funnel(self, metrics: dict[str, Any]) -> AIInsightDraft:
        funnel = metrics.get("funnel", {})
        dropoff = metrics.get("dropoff", {})
        step = dropoff.get("largest_dropoff_step") or "the onboarding funnel"
        completion = funnel.get("completion_rate", 0.0)
        return AIInsightDraft(
            title="Funnel conversion pressure points",
            summary=(
                f"The default funnel is converting at {completion}%. "
                f"The largest visible drop-off is around {step}, making it the best "
                "place to focus the next growth experiment."
            ),
            recommendations=[
                {
                    "text": f"Instrument a focused experiment around {step} with clearer KYC/deposit guidance.",
                    "category": "funnel",
                    "impact": "high",
                    "effort": "medium",
                },
                {
                    "text": "Compare completion rates by acquisition source before changing paid spend.",
                    "category": "analytics",
                    "impact": "medium",
                    "effort": "low",
                },
            ],
            priority="high" if completion < 25 else "medium",
        )

    def _attribution(self, metrics: dict[str, Any]) -> AIInsightDraft:
        attribution = metrics.get("attribution", {})
        top_source = attribution.get("top_source") or "unknown"
        return AIInsightDraft(
            title="Acquisition source performance",
            summary=(
                f"{top_source} is currently the top acquisition source. "
                "Budget decisions should be tied to downstream deposit and trade conversion, "
                "not signup volume alone."
            ),
            recommendations=[
                {
                    "text": f"Audit {top_source} cohorts for deposit and first-trade quality.",
                    "category": "attribution",
                    "impact": "high",
                    "effort": "low",
                },
                {
                    "text": "Keep first-touch and last-touch views side by side for campaign reviews.",
                    "category": "measurement",
                    "impact": "medium",
                    "effort": "low",
                },
            ],
        )

    def _quality(self, metrics: dict[str, Any]) -> AIInsightDraft:
        quality = metrics.get("quality", {})
        score = quality.get("health_score", 0.0)
        summary = quality.get("summary", {})
        return AIInsightDraft(
            title="Analytics data quality posture",
            summary=(
                f"The tracking health score is {score}. "
                f"Detected {summary.get('duplicate_events', 0)} duplicate events and "
                f"{summary.get('schema_error_count', 0)} schema issues in the period."
            ),
            recommendations=[
                {
                    "text": "Prioritize schema validation fixes before relying on executive trend deltas.",
                    "category": "data-quality",
                    "impact": "high",
                    "effort": "medium",
                },
                {
                    "text": "Review duplicate message IDs from ingestion clients and retry flows.",
                    "category": "instrumentation",
                    "impact": "medium",
                    "effort": "medium",
                },
            ],
            priority="high" if score < 85 else "medium",
        )

    def _executive(self, metrics: dict[str, Any]) -> AIInsightDraft:
        funnel = metrics.get("funnel", {})
        quality = metrics.get("quality", {})
        attribution = metrics.get("attribution", {})
        return AIInsightDraft(
            title="Executive growth summary",
            summary=(
                f"Growth health is {quality.get('health_score', 0.0)} with "
                f"{funnel.get('completion_rate', 0.0)}% signup-to-trade funnel completion. "
                f"The leading source is {attribution.get('top_source') or 'not yet available'}."
            ),
            recommendations=[
                {
                    "text": "Focus the next executive review on funnel conversion, source quality, and tracking reliability.",
                    "category": "executive",
                    "impact": "high",
                    "effort": "low",
                }
            ],
        )

    def _recommendations(self, metrics: dict[str, Any]) -> AIInsightDraft:
        funnel = self._funnel(metrics)
        attribution = self._attribution(metrics)
        quality = self._quality(metrics)
        return AIInsightDraft(
            title="Growth recommendations",
            summary="The highest-leverage actions combine funnel repair, channel quality checks, and instrumentation hardening.",
            recommendations=[
                funnel.recommendations[0],
                attribution.recommendations[0],
                quality.recommendations[0],
            ],
            priority="high",
        )

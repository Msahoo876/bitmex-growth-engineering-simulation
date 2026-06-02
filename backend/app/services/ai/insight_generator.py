"""Insight generation over structured analytics metrics."""

import logging
from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.services.ai.prompts.attribution_prompt import build_attribution_prompt
from app.services.ai.prompts.executive_prompt import build_executive_prompt
from app.services.ai.prompts.funnel_prompt import build_funnel_prompt
from app.services.ai.prompts.quality_prompt import build_quality_prompt
from app.services.ai.providers.base_provider import AIInsightDraft, AIInsightProvider, AIProviderError
from app.services.ai.recommendation_engine import RecommendationEngine
from app.services.ai.summary_generator import SummaryGenerator
from app.services.analytics_service import AnalyticsService
from app.services.attribution_service import AttributionService
from app.services.data_quality_service import DataQualityService

logger = logging.getLogger(__name__)


class InsightGenerator:
    def __init__(self, session: Session, provider: AIInsightProvider) -> None:
        self._analytics = AnalyticsService(session)
        self._attribution = AttributionService(session)
        self._quality = DataQualityService(session)
        self._provider = provider
        self._fallback = RecommendationEngine()
        self._summary = SummaryGenerator()

    def collect_metrics(self, *, period_start: datetime, period_end: datetime) -> dict[str, Any]:
        funnel = self._analytics.get_funnel_analytics(
            period_start=period_start,
            period_end=period_end,
            persist_snapshot=False,
        )
        dropoff = self._analytics.get_dropoff_analytics(
            period_start=period_start,
            period_end=period_end,
            persist_snapshot=False,
        )
        retention = self._analytics.get_retention_analytics(
            period_start=period_start,
            period_end=period_end,
            persist_snapshot=False,
        )
        sources = self._attribution.get_sources(
            period_start=period_start,
            period_end=period_end,
            refresh=True,
        )
        quality = self._quality.get_health(
            period_start=period_start,
            period_end=period_end,
            persist_score=False,
        )
        duplicates = self._quality.get_duplicates(period_start=period_start, period_end=period_end)
        schema_errors = self._quality.get_schema_errors(
            period_start=period_start,
            period_end=period_end,
        )
        integrity = self._quality.get_funnel_integrity(
            period_start=period_start,
            period_end=period_end,
        )
        anomalies = self._quality.get_anomalies(period_start=period_start, period_end=period_end)

        d7_retention = next((p.retention_rate for p in retention.periods if p.day == 7), 0.0)
        return {
            "funnel": {
                "funnel_name": funnel.funnel_name,
                "completion_rate": funnel.completion_rate,
                "total_entered": funnel.total_entered,
                "total_completed": funnel.total_completed,
                "steps": [
                    {
                        "key": step.key,
                        "label": step.label,
                        "users": step.users,
                        "conversion_rate_from_start": step.conversion_rate_from_start,
                    }
                    for step in funnel.steps
                ],
            },
            "dropoff": {
                "largest_dropoff_step": dropoff.largest_dropoff_step,
                "steps": [step.model_dump(mode="json") for step in dropoff.steps],
            },
            "retention": {
                "cohort_size": retention.cohort_size,
                "d7_retention": d7_retention,
                "periods": [period.model_dump(mode="json") for period in retention.periods],
            },
            "attribution": {
                "top_source": sources.top_source,
                "source_performance": [
                    metric.model_dump(mode="json") for metric in sources.metrics[:5]
                ],
            },
            "quality": {
                "health_score": quality.health_score,
                "summary": {
                    **quality.summary,
                    "duplicate_events": duplicates.total_duplicate_events,
                    "schema_error_count": schema_errors.total_errors,
                    "broken_funnel_paths": integrity.total_broken_paths,
                    "volume_anomaly_count": anomalies.total_anomalies,
                },
                "breakdown": quality.breakdown,
            },
        }

    def generate(self, *, insight_type: str, metrics: dict[str, Any]) -> AIInsightDraft:
        prompt = self._prompt_for(insight_type)
        compact = self._summary.compact_metrics(metrics)
        try:
            return self._provider.generate(prompt=prompt, metrics=compact)
        except AIProviderError as exc:
            logger.info("Using deterministic insight fallback type=%s reason=%s", insight_type, exc)
            return self._fallback.build(insight_type, metrics)

    @staticmethod
    def _prompt_for(insight_type: str) -> str:
        prompts = {
            "funnel": build_funnel_prompt,
            "attribution": build_attribution_prompt,
            "quality": build_quality_prompt,
            "executive": build_executive_prompt,
            "recommendations": build_executive_prompt,
        }
        return prompts.get(insight_type, build_executive_prompt)()

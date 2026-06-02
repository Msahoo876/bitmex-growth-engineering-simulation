"""Executive reporting and insight persistence service."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.exceptions import ResourceNotFoundError
from app.models.insight import Insight
from app.repositories.insight_repository import InsightRepository
from app.schemas.insights import ExecutiveSummaryResponse, InsightRecommendation, InsightResponse
from app.services.ai.insight_generator import InsightGenerator
from app.services.ai.providers.gemini_provider import GeminiProvider
from app.services.analytics_service import AnalyticsService


class ExecutiveReportService:
    def __init__(self, session: Session, settings: Settings) -> None:
        self._session = session
        self._repo = InsightRepository(session)
        provider = GeminiProvider(api_key=settings.gemini_api_key)
        self._generator = InsightGenerator(session, provider)

    def generate_insights(
        self,
        *,
        insight_types: list[str],
        period_start: datetime,
        period_end: datetime,
        persist: bool = True,
    ) -> list[InsightResponse]:
        metrics = self._generator.collect_metrics(period_start=period_start, period_end=period_end)
        responses: list[InsightResponse] = []
        for insight_type in insight_types:
            draft = self._generator.generate(insight_type=insight_type, metrics=metrics)
            if persist:
                insight = self._repo.add(
                    Insight(
                        insight_type=insight_type,
                        title=draft.title,
                        summary=draft.summary,
                        recommendations=draft.recommendations,
                        input_metrics=metrics,
                        model_name=draft.model_name,
                        priority=draft.priority,
                    )
                )
                responses.append(self._to_response(insight))
            else:
                responses.append(
                    InsightResponse(
                        id="preview",
                        insight_type=insight_type,
                        title=draft.title,
                        summary=draft.summary,
                        recommendations=[
                            InsightRecommendation(**item) for item in draft.recommendations
                        ],
                        input_metrics=metrics,
                        model_name=draft.model_name,
                        priority=draft.priority,
                        created_at=period_end,
                    )
                )
        if persist:
            self._session.commit()
        return responses

    def list_insights(
        self,
        *,
        insight_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[InsightResponse]:
        return [
            self._to_response(insight)
            for insight in self._repo.list_insights(
                insight_type=insight_type,
                limit=limit,
                offset=offset,
            )
        ]

    def get_insight(self, insight_id: UUID) -> InsightResponse:
        insight = self._repo.get_by_uuid(insight_id)
        if insight is None:
            raise ResourceNotFoundError("Insight not found.")
        return self._to_response(insight)

    def get_executive_summary(self) -> ExecutiveSummaryResponse:
        latest = self._repo.get_latest_by_type("executive")
        if latest is None:
            period_start, period_end = AnalyticsService.default_period()
            generated = self.generate_insights(
                insight_types=["executive"],
                period_start=period_start,
                period_end=period_end,
            )
            latest_response = generated[0]
        else:
            latest_response = self._to_response(latest)

        metrics = latest_response.input_metrics or {}
        return ExecutiveSummaryResponse(
            title=latest_response.title,
            summary=latest_response.summary,
            recommendations=latest_response.recommendations,
            health_score=metrics.get("quality", {}).get("health_score"),
            top_source=metrics.get("attribution", {}).get("top_source"),
            generated_at=latest_response.created_at,
        )

    @staticmethod
    def _to_response(insight: Insight) -> InsightResponse:
        return InsightResponse(
            id=str(insight.id),
            insight_type=insight.insight_type,
            title=insight.title,
            summary=insight.summary,
            recommendations=[
                InsightRecommendation(**item)
                for item in (insight.recommendations or [])
                if isinstance(item, dict) and item.get("text")
            ],
            input_metrics=insight.input_metrics,
            model_name=insight.model_name,
            priority=insight.priority,
            created_at=insight.created_at,
        )

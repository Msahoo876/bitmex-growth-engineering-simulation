"""Schemas for AI insight generation and retrieval."""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

InsightType = Literal[
    "funnel",
    "attribution",
    "quality",
    "executive",
    "recommendations",
]


class InsightGenerateRequest(BaseModel):
    insight_types: list[InsightType] = Field(
        default=["executive", "funnel", "attribution", "quality", "recommendations"]
    )
    from_timestamp: datetime | None = Field(default=None, alias="from")
    to_timestamp: datetime | None = Field(default=None, alias="to")
    persist: bool = True


class InsightRecommendation(BaseModel):
    text: str
    category: str = "growth"
    impact: str = "medium"
    effort: str = "medium"


class InsightResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    insight_type: str
    title: str
    summary: str
    recommendations: list[InsightRecommendation] = []
    input_metrics: dict[str, Any] | None = None
    model_name: str | None = None
    priority: str | None = None
    created_at: datetime


class InsightListResponse(BaseModel):
    insights: list[InsightResponse]


class GeneratedInsightsResponse(BaseModel):
    insights: list[InsightResponse]
    generated_count: int


class ExecutiveSummaryResponse(BaseModel):
    title: str
    summary: str
    recommendations: list[InsightRecommendation]
    health_score: float | None = None
    top_source: str | None = None
    generated_at: datetime | None = None

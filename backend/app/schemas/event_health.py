"""Schemas for event health metrics API."""

from pydantic import BaseModel, Field


class ValidationBreakdownItem(BaseModel):
    code: str
    count: int


class EventHealthMetrics(BaseModel):
    period_hours: int
    total_ingested: int
    valid_events: int
    invalid_events: int
    acceptance_rate: float = Field(description="Percentage of valid ingestions (0-100)")
    duplicate_events: int
    events_by_name: dict[str, int] = Field(default_factory=dict)
    validation_breakdown: list[ValidationBreakdownItem] = Field(default_factory=list)
    health_score: float = Field(description="Composite event health score (0-100)")

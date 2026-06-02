"""Schemas for data quality monitoring APIs."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class QualityPeriod(BaseModel):
    start: datetime
    end: datetime


class DataHealthResponse(BaseModel):
    period: QualityPeriod
    health_score: float = Field(ge=0, le=100)
    snapshot_id: str | None = None
    summary: dict[str, int | float]
    breakdown: dict[str, float]


class DuplicateGroupResponse(BaseModel):
    message_id: str
    count: int
    event_ids: list[str]


class DuplicatesResponse(BaseModel):
    period: QualityPeriod
    total_duplicate_groups: int
    total_duplicate_events: int
    groups: list[DuplicateGroupResponse]


class SchemaErrorItem(BaseModel):
    validation_code: str | None = None
    event_name: str | None = None
    message_id: str | None = None
    message: str
    event_id: str | None = None
    issue: str | None = None


class SchemaErrorsResponse(BaseModel):
    period: QualityPeriod
    total_errors: int
    errors: list[SchemaErrorItem]


class MissingPropertyItem(BaseModel):
    event_id: str
    event_name: str
    missing_fields: list[str]


class MissingPropertiesSummary(BaseModel):
    period: QualityPeriod
    total_issues: int
    issues: list[MissingPropertyItem]


class VolumeAnomalyItem(BaseModel):
    date: date
    count: int
    baseline_mean: float
    deviation_pct: float


class AnomaliesResponse(BaseModel):
    period: QualityPeriod
    total_anomalies: int
    daily_volume: dict[str, int]
    anomalies: list[VolumeAnomalyItem]


class BrokenFunnelPathItem(BaseModel):
    identity: str
    skipped_step: str
    reached_step: str


class FunnelIntegrityResponse(BaseModel):
    period: QualityPeriod
    funnel_name: str
    total_broken_paths: int
    broken_paths: list[BrokenFunnelPathItem]

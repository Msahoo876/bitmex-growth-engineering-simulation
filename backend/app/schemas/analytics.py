"""Pydantic schemas for analytics APIs."""

from datetime import date, datetime

from pydantic import BaseModel, Field


class AnalyticsPeriod(BaseModel):
    start: datetime
    end: datetime


class FunnelStepResponse(BaseModel):
    key: str
    label: str
    event_name: str
    users: int
    conversion_rate_from_previous: float | None = None
    conversion_rate_from_start: float


class FunnelAnalyticsResponse(BaseModel):
    funnel_name: str
    period: AnalyticsPeriod
    steps: list[FunnelStepResponse]
    total_entered: int
    total_completed: int
    completion_rate: float
    snapshot_id: str | None = None


class ConversionStepResponse(BaseModel):
    from_step: str
    to_step: str
    from_event: str
    to_event: str
    users_at_from_step: int
    users_at_to_step: int
    conversion_rate: float


class ConversionAnalyticsResponse(BaseModel):
    funnel_name: str
    period: AnalyticsPeriod
    conversions: list[ConversionStepResponse]
    overall_conversion_rate: float
    snapshot_id: str | None = None


class DropoffStepResponse(BaseModel):
    from_step: str
    to_step: str
    users_lost: int
    dropoff_rate: float


class DropoffAnalyticsResponse(BaseModel):
    funnel_name: str
    period: AnalyticsPeriod
    steps: list[DropoffStepResponse]
    largest_dropoff_step: str | None
    snapshot_id: str | None = None


class RetentionPeriodResponse(BaseModel):
    day: int
    retained_users: int
    retention_rate: float


class RetentionAnalyticsResponse(BaseModel):
    anchor_event: str
    period: AnalyticsPeriod
    cohort_size: int
    periods: list[RetentionPeriodResponse]
    snapshot_id: str | None = None


class CohortRowResponse(BaseModel):
    cohort_date: date
    cohort_size: int
    d1_retention: float
    d7_retention: float
    d30_retention: float


class CohortAnalyticsResponse(BaseModel):
    anchor_event: str
    period: AnalyticsPeriod
    cohorts: list[CohortRowResponse]
    snapshot_id: str | None = None

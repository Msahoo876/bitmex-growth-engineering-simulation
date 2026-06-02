"""Schemas for attribution APIs."""

from datetime import datetime

from pydantic import BaseModel


class AttributionPeriod(BaseModel):
    start: datetime
    end: datetime


class SourceAttributionItem(BaseModel):
    source: str
    touch_type: str
    users: int


class SourceAttributionResponse(BaseModel):
    period: AttributionPeriod
    metrics: list[SourceAttributionItem]
    top_source: str | None


class CampaignAttributionItem(BaseModel):
    campaign_name: str
    source: str
    touch_type: str
    users: int


class CampaignAttributionResponse(BaseModel):
    period: AttributionPeriod
    metrics: list[CampaignAttributionItem]


class TopSourceResponse(BaseModel):
    period: AttributionPeriod
    source: str | None
    users: int


class DeepLinkItem(BaseModel):
    deep_link: str
    users: int


class DeepLinkResponse(BaseModel):
    period: AttributionPeriod
    metrics: list[DeepLinkItem]


class ReferralItem(BaseModel):
    referral_code: str
    users: int


class ReferralResponse(BaseModel):
    period: AttributionPeriod
    metrics: list[ReferralItem]

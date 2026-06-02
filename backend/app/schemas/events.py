"""Pydantic schemas for Segment-style event ingestion."""

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class TrackingContext(BaseModel):
    model_config = ConfigDict(extra="allow")

    ip: str | None = None
    user_agent: str | None = Field(default=None, alias="userAgent")
    locale: str | None = None


class TrackRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str | None = Field(default=None, alias="userId")
    anonymous_id: str | None = Field(default=None, alias="anonymousId")
    event: str = Field(..., min_length=1, max_length=128)
    properties: dict[str, Any] | None = None
    context: dict[str, Any] | None = None
    timestamp: datetime | None = None
    message_id: str | None = Field(default=None, alias="messageId")


class IdentifyRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="userId", min_length=1, max_length=255)
    anonymous_id: str | None = Field(default=None, alias="anonymousId")
    traits: dict[str, Any] | None = None
    context: dict[str, Any] | None = None
    timestamp: datetime | None = None
    message_id: str | None = Field(default=None, alias="messageId")


class PageRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str | None = Field(default=None, alias="userId")
    anonymous_id: str | None = Field(default=None, alias="anonymousId")
    name: str = Field(..., min_length=1, max_length=255)
    properties: dict[str, Any] | None = None
    context: dict[str, Any] | None = None
    timestamp: datetime | None = None
    message_id: str | None = Field(default=None, alias="messageId")
    url: str | None = None
    title: str | None = None


class IngestEventRequest(BaseModel):
    """Unified envelope for POST /events."""

    model_config = ConfigDict(populate_by_name=True)

    type: Literal["track", "identify", "page"]
    payload: dict[str, Any]


class ValidationIssueSchema(BaseModel):
    code: str
    message: str


class EventIngestResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    success: bool
    event_id: str | None = Field(default=None, serialization_alias="eventId")
    message_id: str | None = Field(default=None, serialization_alias="messageId")
    validation: list[ValidationIssueSchema] = Field(default_factory=list)


class EventRecordSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    event_id: str
    event_name: str
    event_type: str
    user_id: UUID | None
    anonymous_id: str | None
    properties: dict[str, Any] | None
    context: dict[str, Any] | None
    timestamp: datetime
    received_at: datetime
    message_id: str | None
    page_name: str | None
    page_url: str | None


class EventExplorerResponse(BaseModel):
    total: int
    limit: int
    offset: int
    events: list[EventRecordSchema]

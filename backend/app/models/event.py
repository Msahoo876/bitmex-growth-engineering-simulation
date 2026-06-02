"""Tracked analytics events (Segment-style track/page)."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Event(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    event_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(
        String(32), nullable=False, default="track"
    )  # track | page | identify
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    anonymous_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    properties: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=dict)
    context: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=dict)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    message_id: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    page_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    page_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="events", lazy="joined")
    validation_logs = relationship("EventValidationLog", back_populates="event", lazy="selectin")

    __table_args__ = (
        Index("ix_events_user_id_timestamp", "user_id", "timestamp"),
        Index("ix_events_event_name_timestamp", "event_name", "timestamp"),
    )

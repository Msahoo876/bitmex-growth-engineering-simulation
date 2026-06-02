"""Precomputed analytics snapshots for dashboards and AI summaries."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class AnalyticsSnapshot(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "analytics_snapshots"

    snapshot_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)

    __table_args__ = (
        Index("ix_analytics_snapshots_type_period", "snapshot_type", "period_start", "period_end"),
    )

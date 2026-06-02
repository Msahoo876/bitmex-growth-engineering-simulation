"""Data health score snapshots (0–100)."""

from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Float, Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class HealthScore(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "health_scores"

    score: Mapped[float] = mapped_column(Float, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    breakdown: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=dict)
    check_type: Mapped[str] = mapped_column(String(64), nullable=False, default="aggregate")

    __table_args__ = (
        Index("ix_health_scores_period", "period_start", "period_end"),
        Index("ix_health_scores_score", "score"),
    )

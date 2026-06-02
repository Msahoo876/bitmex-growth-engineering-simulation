"""AI-generated growth insights (Gemini output storage)."""

from typing import Any

from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Insight(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "insights"

    insight_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    recommendations: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    input_metrics: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    model_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    priority: Mapped[str | None] = mapped_column(String(32), nullable=True)  # low | medium | high

    __table_args__ = (Index("ix_insights_created_at", "created_at"),)

"""Event validation results and health diagnostics."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class EventValidationLog(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "event_validation_logs"

    event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("events.id", ondelete="SET NULL"), nullable=True, index=True
    )
    message_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    event_name: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    is_valid: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    validation_code: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    validation_message: Mapped[str] = mapped_column(Text, nullable=False)

    event = relationship("Event", back_populates="validation_logs", lazy="joined")

    __table_args__ = (
        Index("ix_event_validation_logs_is_valid", "is_valid"),
    )

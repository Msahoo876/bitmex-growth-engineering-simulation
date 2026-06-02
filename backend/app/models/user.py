"""User identity model (Segment-style identify)."""

from typing import Any

from sqlalchemy import Index, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class User(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "users"

    external_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True, index=True)
    anonymous_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    traits: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=dict)

    events = relationship("Event", back_populates="user", lazy="selectin")
    attributions = relationship("Attribution", back_populates="user", lazy="selectin")

    __table_args__ = (Index("ix_users_created_at", "created_at"),)

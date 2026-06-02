"""First-touch and last-touch attribution records."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin, UUIDPrimaryKeyMixin


class Attribution(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "attributions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    campaign_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("campaigns.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    medium: Mapped[str | None] = mapped_column(String(128), nullable=True)
    campaign_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    touch_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # first_touch | last_touch
    attributed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user = relationship("User", back_populates="attributions", lazy="joined")
    campaign = relationship("Campaign", back_populates="attributions", lazy="joined")

    __table_args__ = (
        Index("ix_attributions_user_touch", "user_id", "touch_type"),
        Index("ix_attributions_campaign_id_attributed_at", "campaign_id", "attributed_at"),
    )

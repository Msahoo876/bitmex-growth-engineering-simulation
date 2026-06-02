"""SQLAlchemy declarative base and model registry."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

    pass


# Import models so Alembic autogenerate detects metadata.
# noqa: E402 — intentional late import to avoid circular dependencies.
def import_models() -> None:
    from app.models import (  # noqa: F401
        analytics_snapshot,
        attribution,
        campaign,
        event,
        event_validation_log,
        funnel,
        health_score,
        insight,
        user,
    )

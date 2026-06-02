"""Initial database schema — all core tables.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-06-01

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=True),
        sa.Column("anonymous_id", sa.String(length=255), nullable=True),
        sa.Column("traits", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_id"),
    )
    op.create_index("ix_users_anonymous_id", "users", ["anonymous_id"], unique=False)
    op.create_index("ix_users_created_at", "users", ["created_at"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=False)
    op.create_index("ix_users_external_id", "users", ["external_id"], unique=True)

    op.create_table(
        "campaigns",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("medium", sa.String(length=128), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_campaigns_name", "campaigns", ["name"], unique=False)
    op.create_index("ix_campaigns_source", "campaigns", ["source"], unique=False)
    op.create_index("ix_campaigns_source_medium", "campaigns", ["source", "medium"], unique=False)

    op.create_table(
        "funnels",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("steps", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("is_default", sa.Boolean(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_funnels_is_default", "funnels", ["is_default"], unique=False)
    op.create_index("ix_funnels_name", "funnels", ["name"], unique=True)

    op.create_table(
        "analytics_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_type", sa.String(length=64), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_analytics_snapshots_type_period",
        "analytics_snapshots",
        ["snapshot_type", "period_start", "period_end"],
        unique=False,
    )
    op.create_index(
        "ix_analytics_snapshots_snapshot_type",
        "analytics_snapshots",
        ["snapshot_type"],
        unique=False,
    )

    op.create_table(
        "insights",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("insight_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("recommendations", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("input_metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("model_name", sa.String(length=128), nullable=True),
        sa.Column("priority", sa.String(length=32), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_insights_created_at", "insights", ["created_at"], unique=False)
    op.create_index("ix_insights_insight_type", "insights", ["insight_type"], unique=False)

    op.create_table(
        "health_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("breakdown", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("check_type", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_health_scores_period", "health_scores", ["period_start", "period_end"], unique=False)
    op.create_index("ix_health_scores_score", "health_scores", ["score"], unique=False)

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("event_name", sa.String(length=128), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("anonymous_id", sa.String(length=255), nullable=True),
        sa.Column("properties", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("context", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("message_id", sa.String(length=128), nullable=True),
        sa.Column("page_name", sa.String(length=255), nullable=True),
        sa.Column("page_url", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
        sa.UniqueConstraint("message_id"),
    )
    op.create_index("ix_events_anonymous_id", "events", ["anonymous_id"], unique=False)
    op.create_index("ix_events_event_id", "events", ["event_id"], unique=True)
    op.create_index("ix_events_event_name", "events", ["event_name"], unique=False)
    op.create_index("ix_events_event_name_timestamp", "events", ["event_name", "timestamp"], unique=False)
    op.create_index("ix_events_timestamp", "events", ["timestamp"], unique=False)
    op.create_index("ix_events_user_id", "events", ["user_id"], unique=False)
    op.create_index("ix_events_user_id_timestamp", "events", ["user_id", "timestamp"], unique=False)

    op.create_table(
        "attributions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("source", sa.String(length=128), nullable=False),
        sa.Column("medium", sa.String(length=128), nullable=True),
        sa.Column("campaign_name", sa.String(length=255), nullable=True),
        sa.Column("touch_type", sa.String(length=32), nullable=False),
        sa.Column("attributed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attributions_campaign_id", "attributions", ["campaign_id"], unique=False)
    op.create_index(
        "ix_attributions_campaign_id_attributed_at",
        "attributions",
        ["campaign_id", "attributed_at"],
        unique=False,
    )
    op.create_index("ix_attributions_source", "attributions", ["source"], unique=False)
    op.create_index("ix_attributions_user_id", "attributions", ["user_id"], unique=False)
    op.create_index("ix_attributions_user_touch", "attributions", ["user_id", "touch_type"], unique=False)

    op.create_table(
        "event_validation_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("message_id", sa.String(length=128), nullable=True),
        sa.Column("event_name", sa.String(length=128), nullable=True),
        sa.Column("is_valid", sa.Boolean(), nullable=False),
        sa.Column("validation_code", sa.String(length=64), nullable=False),
        sa.Column("validation_message", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["event_id"], ["events.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_event_validation_logs_event_id",
        "event_validation_logs",
        ["event_id"],
        unique=False,
    )
    op.create_index(
        "ix_event_validation_logs_event_name",
        "event_validation_logs",
        ["event_name"],
        unique=False,
    )
    op.create_index(
        "ix_event_validation_logs_is_valid",
        "event_validation_logs",
        ["is_valid"],
        unique=False,
    )
    op.create_index(
        "ix_event_validation_logs_message_id",
        "event_validation_logs",
        ["message_id"],
        unique=False,
    )
    op.create_index(
        "ix_event_validation_logs_validation_code",
        "event_validation_logs",
        ["validation_code"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("event_validation_logs")
    op.drop_table("attributions")
    op.drop_table("events")
    op.drop_table("health_scores")
    op.drop_table("insights")
    op.drop_table("analytics_snapshots")
    op.drop_table("funnels")
    op.drop_table("campaigns")
    op.drop_table("users")

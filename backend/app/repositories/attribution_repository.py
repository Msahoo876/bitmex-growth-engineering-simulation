"""Repository for attribution writes and aggregations."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.attribution import Attribution
from app.models.event import Event


@dataclass(frozen=True)
class AcquisitionEventRecord:
    identity: str
    user_id: UUID | None
    anonymous_id: str | None
    timestamp: datetime
    source: str
    medium: str | None
    campaign_name: str | None
    referral_code: str | None
    deep_link: str | None


@dataclass(frozen=True)
class AttributionTouch:
    user_id: UUID
    source: str
    medium: str | None
    campaign_name: str | None
    touch_type: str
    attributed_at: datetime


class AttributionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def fetch_acquisition_events(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
    ) -> list[AcquisitionEventRecord]:
        stmt = (
            select(
                Event.user_id,
                Event.anonymous_id,
                Event.timestamp,
                Event.properties,
                Event.event_name,
            )
            .where(
                Event.timestamp >= period_start,
                Event.timestamp <= period_end,
                Event.event_name.in_(
                    (
                        "landing_page_viewed",
                        "campaign_clicked",
                        "signup_from_campaign",
                        "referral_clicked",
                        "user_signed_up",
                    )
                ),
            )
            .order_by(Event.timestamp.asc())
        )
        rows = self._session.execute(stmt).all()
        out: list[AcquisitionEventRecord] = []
        for user_id, anonymous_id, timestamp, properties, event_name in rows:
            identity = self._identity(user_id, anonymous_id)
            if identity is None:
                continue
            props = properties or {}
            source = self._pick_source(event_name=event_name, properties=props)
            medium = self._pick_medium(props)
            campaign_name = self._pick_campaign(props)
            referral_code = self._pick_referral(props)
            deep_link = self._pick_deep_link(props)
            out.append(
                AcquisitionEventRecord(
                    identity=identity,
                    user_id=user_id,
                    anonymous_id=anonymous_id,
                    timestamp=timestamp,
                    source=source,
                    medium=medium,
                    campaign_name=campaign_name,
                    referral_code=referral_code,
                    deep_link=deep_link,
                )
            )
        return out

    def replace_user_touches(self, touches: list[AttributionTouch]) -> int:
        if not touches:
            return 0
        user_ids = list({t.user_id for t in touches})
        self._session.query(Attribution).filter(Attribution.user_id.in_(user_ids)).delete(
            synchronize_session=False
        )
        created = 0
        for touch in touches:
            self._session.add(
                Attribution(
                    user_id=touch.user_id,
                    campaign_id=None,
                    source=touch.source,
                    medium=touch.medium,
                    campaign_name=touch.campaign_name,
                    touch_type=touch.touch_type,
                    attributed_at=touch.attributed_at,
                )
            )
            created += 1
        return created

    def source_metrics(self, *, period_start: datetime, period_end: datetime) -> list[dict[str, Any]]:
        stmt = (
            select(Attribution.source, Attribution.touch_type, func.count())
            .where(
                Attribution.attributed_at >= period_start,
                Attribution.attributed_at <= period_end,
            )
            .group_by(Attribution.source, Attribution.touch_type)
            .order_by(func.count().desc())
        )
        rows = self._session.execute(stmt).all()
        return [
            {"source": source, "touch_type": touch_type, "users": int(count)}
            for source, touch_type, count in rows
        ]

    def campaign_metrics(self, *, period_start: datetime, period_end: datetime) -> list[dict[str, Any]]:
        stmt = (
            select(Attribution.campaign_name, Attribution.source, Attribution.touch_type, func.count())
            .where(
                Attribution.attributed_at >= period_start,
                Attribution.attributed_at <= period_end,
            )
            .group_by(Attribution.campaign_name, Attribution.source, Attribution.touch_type)
            .order_by(func.count().desc())
        )
        rows = self._session.execute(stmt).all()
        return [
            {
                "campaign_name": campaign_name or "(unknown)",
                "source": source,
                "touch_type": touch_type,
                "users": int(count),
            }
            for campaign_name, source, touch_type, count in rows
        ]

    @staticmethod
    def _identity(user_id: UUID | None, anonymous_id: str | None) -> str | None:
        if user_id is not None:
            return f"user:{user_id}"
        if anonymous_id:
            return f"anon:{anonymous_id}"
        return None

    @staticmethod
    def _pick_source(*, event_name: str, properties: dict[str, Any]) -> str:
        source = properties.get("source") or properties.get("utm_source")
        if isinstance(source, str) and source.strip():
            return source.strip().lower()
        if event_name == "referral_clicked":
            return "referral"
        return "direct"

    @staticmethod
    def _pick_medium(properties: dict[str, Any]) -> str | None:
        medium = properties.get("medium") or properties.get("utm_medium")
        return medium if isinstance(medium, str) and medium.strip() else None

    @staticmethod
    def _pick_campaign(properties: dict[str, Any]) -> str | None:
        campaign = properties.get("campaign") or properties.get("utm_campaign")
        return campaign if isinstance(campaign, str) and campaign.strip() else None

    @staticmethod
    def _pick_referral(properties: dict[str, Any]) -> str | None:
        code = properties.get("referral_code") or properties.get("referrer")
        return code if isinstance(code, str) and code.strip() else None

    @staticmethod
    def _pick_deep_link(properties: dict[str, Any]) -> str | None:
        link = properties.get("deep_link") or properties.get("deeplink") or properties.get("url")
        return link if isinstance(link, str) and link.strip() else None

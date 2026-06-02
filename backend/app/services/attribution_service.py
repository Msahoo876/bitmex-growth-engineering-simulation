"""Attribution analytics service."""

import logging
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.attribution_repository import (
    AcquisitionEventRecord,
    AttributionRepository,
    AttributionTouch,
)
from app.schemas.attribution import (
    AttributionPeriod,
    CampaignAttributionItem,
    CampaignAttributionResponse,
    DeepLinkItem,
    DeepLinkResponse,
    ReferralItem,
    ReferralResponse,
    SourceAttributionItem,
    SourceAttributionResponse,
    TopSourceResponse,
)

logger = logging.getLogger(__name__)


class AttributionService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = AttributionRepository(session)

    def get_sources(
        self, *, period_start: datetime, period_end: datetime, refresh: bool = True
    ) -> SourceAttributionResponse:
        if refresh:
            self._recompute_touches(period_start=period_start, period_end=period_end)
        metrics = [
            SourceAttributionItem(**item)
            for item in self._repo.source_metrics(period_start=period_start, period_end=period_end)
        ]
        top_source = metrics[0].source if metrics else None
        return SourceAttributionResponse(
            period=AttributionPeriod(start=period_start, end=period_end),
            metrics=metrics,
            top_source=top_source,
        )

    def get_campaigns(
        self, *, period_start: datetime, period_end: datetime, refresh: bool = True
    ) -> CampaignAttributionResponse:
        if refresh:
            self._recompute_touches(period_start=period_start, period_end=period_end)
        metrics = [
            CampaignAttributionItem(**item)
            for item in self._repo.campaign_metrics(period_start=period_start, period_end=period_end)
        ]
        return CampaignAttributionResponse(
            period=AttributionPeriod(start=period_start, end=period_end),
            metrics=metrics,
        )

    def get_top_source(
        self, *, period_start: datetime, period_end: datetime, refresh: bool = True
    ) -> TopSourceResponse:
        sources = self.get_sources(period_start=period_start, period_end=period_end, refresh=refresh)
        if not sources.metrics:
            return TopSourceResponse(
                period=sources.period,
                source=None,
                users=0,
            )
        return TopSourceResponse(
            period=sources.period,
            source=sources.metrics[0].source,
            users=sources.metrics[0].users,
        )

    def get_deep_links(
        self, *, period_start: datetime, period_end: datetime, refresh: bool = True
    ) -> DeepLinkResponse:
        records = self._repo.fetch_acquisition_events(period_start=period_start, period_end=period_end)
        if refresh:
            self._recompute_touches(period_start=period_start, period_end=period_end, records=records)
        counts: dict[str, set[str]] = {}
        for r in records:
            if not r.deep_link:
                continue
            counts.setdefault(r.deep_link, set()).add(r.identity)
        metrics = [
            DeepLinkItem(deep_link=link, users=len(identities))
            for link, identities in sorted(counts.items(), key=lambda i: len(i[1]), reverse=True)
        ]
        return DeepLinkResponse(
            period=AttributionPeriod(start=period_start, end=period_end),
            metrics=metrics,
        )

    def get_referrals(
        self, *, period_start: datetime, period_end: datetime, refresh: bool = True
    ) -> ReferralResponse:
        records = self._repo.fetch_acquisition_events(period_start=period_start, period_end=period_end)
        if refresh:
            self._recompute_touches(period_start=period_start, period_end=period_end, records=records)
        counts: dict[str, set[str]] = {}
        for r in records:
            if not r.referral_code:
                continue
            counts.setdefault(r.referral_code, set()).add(r.identity)
        metrics = [
            ReferralItem(referral_code=code, users=len(identities))
            for code, identities in sorted(counts.items(), key=lambda i: len(i[1]), reverse=True)
        ]
        return ReferralResponse(
            period=AttributionPeriod(start=period_start, end=period_end),
            metrics=metrics,
        )

    def _recompute_touches(
        self,
        *,
        period_start: datetime,
        period_end: datetime,
        records: list[AcquisitionEventRecord] | None = None,
    ) -> None:
        events = records or self._repo.fetch_acquisition_events(
            period_start=period_start, period_end=period_end
        )
        by_identity: dict[str, list[AcquisitionEventRecord]] = {}
        for record in events:
            by_identity.setdefault(record.identity, []).append(record)

        touches: list[AttributionTouch] = []
        for identity_records in by_identity.values():
            ordered = sorted(identity_records, key=lambda r: r.timestamp)
            first = ordered[0]
            last = ordered[-1]
            user_id = self._resolve_user_id(ordered)
            if user_id is None:
                continue
            touches.append(
                AttributionTouch(
                    user_id=user_id,
                    source=first.source,
                    medium=first.medium,
                    campaign_name=first.campaign_name,
                    touch_type="first_touch",
                    attributed_at=first.timestamp,
                )
            )
            touches.append(
                AttributionTouch(
                    user_id=user_id,
                    source=last.source,
                    medium=last.medium,
                    campaign_name=last.campaign_name,
                    touch_type="last_touch",
                    attributed_at=last.timestamp,
                )
            )
        created = self._repo.replace_user_touches(touches)
        self._session.commit()
        logger.info("Attribution recomputed users=%s touches=%s", len(by_identity), created)

    @staticmethod
    def _resolve_user_id(records: list[AcquisitionEventRecord]) -> UUID | None:
        for record in records:
            if record.user_id is not None:
                return record.user_id
        return None

    @staticmethod
    def default_period(days: int = 30) -> tuple[datetime, datetime]:
        end = datetime.now(UTC)
        start = end - timedelta(days=days)
        return start, end

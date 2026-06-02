"""Repository for AI-generated growth insights."""

from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models.insight import Insight
from app.repositories.base import BaseRepository


class InsightRepository(BaseRepository[Insight]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Insight)

    def list_insights(
        self,
        *,
        insight_type: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Insight]:
        stmt = select(Insight).order_by(desc(Insight.created_at)).limit(limit).offset(offset)
        if insight_type:
            stmt = stmt.where(Insight.insight_type == insight_type)
        return list(self._session.scalars(stmt).all())

    def get_latest_by_type(self, insight_type: str) -> Insight | None:
        stmt = (
            select(Insight)
            .where(Insight.insight_type == insight_type)
            .order_by(desc(Insight.created_at))
            .limit(1)
        )
        return self._session.scalars(stmt).first()

    def get_by_uuid(self, insight_id: UUID) -> Insight | None:
        return self.get_by_id(insight_id)

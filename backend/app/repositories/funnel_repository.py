"""Load configurable funnel definitions from PostgreSQL."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.funnels import (
    DEFAULT_FUNNEL_NAME,
    DEFAULT_FUNNEL_STEPS,
    FunnelStepDefinition,
    parse_funnel_steps,
)
from app.models.funnel import Funnel
from app.repositories.base import BaseRepository


class FunnelRepository(BaseRepository[Funnel]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Funnel)

    def get_by_name(self, name: str) -> Funnel | None:
        stmt = select(Funnel).where(Funnel.name == name, Funnel.is_active.is_(True))
        return self._session.scalars(stmt).first()

    def get_default(self) -> Funnel | None:
        stmt = select(Funnel).where(Funnel.is_default.is_(True), Funnel.is_active.is_(True))
        return self._session.scalars(stmt).first()

    def resolve_steps(self, funnel_name: str | None = None) -> tuple[str, list[FunnelStepDefinition]]:
        if funnel_name:
            funnel = self.get_by_name(funnel_name)
            if funnel is None:
                raise ValueError(f"Funnel '{funnel_name}' not found or inactive.")
            return funnel.name, parse_funnel_steps(funnel.steps)

        funnel = self.get_default()
        if funnel is not None:
            return funnel.name, parse_funnel_steps(funnel.steps)

        return DEFAULT_FUNNEL_NAME, list(DEFAULT_FUNNEL_STEPS)

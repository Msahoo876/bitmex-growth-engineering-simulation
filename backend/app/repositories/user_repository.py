"""User persistence for identify() and event attribution."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, User)

    def get_by_external_id(self, external_id: str) -> User | None:
        stmt = select(User).where(User.external_id == external_id)
        return self._session.scalars(stmt).first()

    def get_by_anonymous_id(self, anonymous_id: str) -> User | None:
        stmt = select(User).where(User.anonymous_id == anonymous_id)
        return self._session.scalars(stmt).first()

    def upsert_identify(
        self,
        *,
        external_id: str,
        anonymous_id: str | None,
        email: str | None,
        traits: dict[str, Any] | None,
    ) -> User:
        user = self.get_by_external_id(external_id)
        merged_traits = traits or {}

        if user is None:
            user = User(
                external_id=external_id,
                anonymous_id=anonymous_id,
                email=email or merged_traits.get("email"),
                traits=merged_traits,
            )
            return self.add(user)

        if anonymous_id:
            user.anonymous_id = anonymous_id
        if email:
            user.email = email
        elif merged_traits.get("email"):
            user.email = str(merged_traits["email"])

        existing_traits = dict(user.traits or {})
        existing_traits.update(merged_traits)
        user.traits = existing_traits
        self._session.flush()
        self._session.refresh(user)
        return user

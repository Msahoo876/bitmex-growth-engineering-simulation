"""Generic repository base class for the repository layer."""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """CRUD primitives shared by domain repositories (extended in later phases)."""

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self._session = session
        self._model = model

    def get_by_id(self, entity_id: UUID) -> ModelT | None:
        return self._session.get(self._model, entity_id)

    def list_all(self, *, limit: int = 100, offset: int = 0) -> list[ModelT]:
        stmt = select(self._model).limit(limit).offset(offset)
        return list(self._session.scalars(stmt).all())

    def add(self, entity: ModelT) -> ModelT:
        self._session.add(entity)
        self._session.flush()
        self._session.refresh(entity)
        return entity

    def delete(self, entity: ModelT) -> None:
        self._session.delete(entity)
        self._session.flush()

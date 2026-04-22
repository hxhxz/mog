from typing import Generic, TypeVar, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    model: Type[T]

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, id: str) -> T | None:
        return await self.db.get(self.model, id)

    async def add(self, obj: T) -> T:
        self.db.add(obj)
        await self.db.flush()
        return obj

    async def list(self) -> list[T]:
        res = await self.db.execute(select(self.model))
        return list(res.scalars().all())

    async def commit(self) -> None:
        await self.db.commit()

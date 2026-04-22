from sqlalchemy import select
from app.models.character import Character
from app.repositories.base import BaseRepository


class CharacterRepository(BaseRepository[Character]):
    model = Character

    async def list_by_project(self, project_id: str) -> list[Character]:
        res = await self.db.execute(select(Character).where(Character.project_id == project_id))
        return list(res.scalars().all())

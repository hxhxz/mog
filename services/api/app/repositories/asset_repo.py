from sqlalchemy import select
from app.models.asset import Asset
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    model = Asset

    async def list_by_kind(self, kind: str) -> list[Asset]:
        res = await self.db.execute(select(Asset).where(Asset.kind == kind))
        return list(res.scalars().all())

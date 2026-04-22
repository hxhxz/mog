from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.asset_repo import AssetRepository
from app.schemas.asset import AssetOut


class AssetService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AssetRepository(db)

    async def list_style_loras(self) -> list[AssetOut]:
        items = await self.repo.list_by_kind("style_lora")
        return [AssetOut.model_validate(a) for a in items]

    async def list_character_loras(self) -> list[AssetOut]:
        items = await self.repo.list_by_kind("character_lora")
        return [AssetOut.model_validate(a) for a in items]

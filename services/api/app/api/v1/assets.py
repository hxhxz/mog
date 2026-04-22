"""LoRA / 图片 / 视频资产 — PRD §4.4."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.asset import AssetOut

router = APIRouter()


@router.get("/loras/style", response_model=list[AssetOut])
async def list_style_loras(db: AsyncSession = Depends(get_db)) -> list[AssetOut]:
    """PRD §4.4 平台预置风格 LoRA."""
    return []  # TODO: AssetService(db).list_style_loras()


@router.get("/loras/character", response_model=list[AssetOut])
async def list_character_loras(db: AsyncSession = Depends(get_db)) -> list[AssetOut]:
    return []  # TODO

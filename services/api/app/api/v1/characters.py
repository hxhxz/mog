"""PRD §3.1 Step 2：角色卡管理."""
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.character import CharacterOut, CharacterCreate

router = APIRouter()


@router.post("", response_model=CharacterOut)
async def create_character(
    payload: CharacterCreate, db: AsyncSession = Depends(get_db)
) -> CharacterOut:
    raise NotImplementedError  # TODO: wire to CharacterService


@router.post("/{character_id}/reference")
async def upload_reference(character_id: str, file: UploadFile = File(...)) -> dict:
    return {"character_id": character_id, "status": "uploaded", "filename": file.filename}

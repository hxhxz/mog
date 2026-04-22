"""PRD §3.1 Step 1：片段确认 / 修改."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.segment import SegmentOut, SegmentUpdate
from app.services.segment_service import SegmentService

router = APIRouter()


@router.get("", response_model=list[SegmentOut])
async def list_segments(project_id: str, db: AsyncSession = Depends(get_db)) -> list[SegmentOut]:
    return await SegmentService(db).list_by_project(project_id)


@router.patch("/{segment_id}", response_model=SegmentOut)
async def update_segment(
    segment_id: str, payload: SegmentUpdate, db: AsyncSession = Depends(get_db)
) -> SegmentOut:
    return await SegmentService(db).update(segment_id, payload)


@router.post("/{segment_id}/confirm", response_model=SegmentOut)
async def confirm_segment(segment_id: str, db: AsyncSession = Depends(get_db)) -> SegmentOut:
    return await SegmentService(db).confirm(segment_id)

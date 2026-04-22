from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.segment_repo import SegmentRepository
from app.schemas.segment import SegmentOut, SegmentUpdate


class SegmentService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = SegmentRepository(db)

    async def list_by_project(self, project_id: str) -> list[SegmentOut]:
        items = await self.repo.list_by_project(project_id)
        return [SegmentOut.model_validate(s) for s in items]

    async def update(self, segment_id: str, payload: SegmentUpdate) -> SegmentOut:
        seg = await self.repo.get(segment_id)
        if not seg:
            raise HTTPException(status_code=404, detail="segment not found")
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(seg, k, v)
        await self.repo.commit()
        return SegmentOut.model_validate(seg)

    async def confirm(self, segment_id: str) -> SegmentOut:
        seg = await self.repo.get(segment_id)
        if not seg:
            raise HTTPException(status_code=404, detail="segment not found")
        seg.status = "confirmed"
        await self.repo.commit()
        return SegmentOut.model_validate(seg)

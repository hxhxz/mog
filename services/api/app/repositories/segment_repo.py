from sqlalchemy import select
from app.models.segment import Segment
from app.repositories.base import BaseRepository


class SegmentRepository(BaseRepository[Segment]):
    model = Segment

    async def list_by_project(self, project_id: str) -> list[Segment]:
        res = await self.db.execute(
            select(Segment).where(Segment.project_id == project_id).order_by(Segment.order_index)
        )
        return list(res.scalars().all())

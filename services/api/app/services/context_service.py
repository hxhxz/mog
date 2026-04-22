"""PRD §3.3 Context 对象的唯一真源."""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.project_repo import ProjectRepository
from app.repositories.segment_repo import SegmentRepository
from app.repositories.character_repo import CharacterRepository
from app.schemas.project import ProjectContext, CharacterRef, SegmentRef


class ContextService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get(self, project_id: str) -> ProjectContext:
        project = await ProjectRepository(self.db).get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="project not found")
        segs = await SegmentRepository(self.db).list_by_project(project_id)
        chars = await CharacterRepository(self.db).list_by_project(project_id)
        return ProjectContext(
            project_id=project.id,
            style_lora=project.style_lora_id,
            characters=[CharacterRef(
                id=c.id, name=c.name,
                reference_image_url=c.reference_image_url,
                character_lora_id=c.character_lora_id,
            ) for c in chars],
            segments=[SegmentRef(
                id=s.id, order_index=s.order_index, status=s.status,
                storyboard_url=s.storyboard_url, video_url=s.video_url,
            ) for s in segs],
            audio_track=project.audio_track_url,
        )

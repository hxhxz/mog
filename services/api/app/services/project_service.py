from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.repositories.project_repo import ProjectRepository
from app.schemas.project import ProjectCreate, ProjectOut
from app.services.project_step_service import ProjectStepService


class ProjectService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProjectRepository(db)

    async def create(self, payload: ProjectCreate) -> ProjectOut:
        project = Project(name=payload.name, style_lora_id=payload.style_lora_id)
        await self.repo.add(project)
        await self.repo.commit()
        # 项目创建时自动初始化 6 个流水线步骤
        await ProjectStepService(self.db).initialize(project.id)
        return ProjectOut.model_validate(project)

    async def list(self) -> list[ProjectOut]:
        items = await self.repo.list()
        return [ProjectOut.model_validate(p) for p in items]

    async def get(self, project_id: str) -> ProjectOut:
        project = await self.repo.get(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="project not found")
        return ProjectOut.model_validate(project)

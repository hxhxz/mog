"""PRD §3.1 项目 CRUD + Context 读写."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.project import ProjectCreate, ProjectOut, ProjectContext
from app.services.project_service import ProjectService
from app.services.context_service import ContextService

router = APIRouter()


@router.post("", response_model=ProjectOut)
async def create_project(payload: ProjectCreate, db: AsyncSession = Depends(get_db)) -> ProjectOut:
    return await ProjectService(db).create(payload)


@router.get("", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)) -> list[ProjectOut]:
    return await ProjectService(db).list()


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)) -> ProjectOut:
    return await ProjectService(db).get(project_id)


@router.get("/{project_id}/context", response_model=ProjectContext)
async def get_context(project_id: str, db: AsyncSession = Depends(get_db)) -> ProjectContext:
    return await ContextService(db).get(project_id)

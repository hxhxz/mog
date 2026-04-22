"""Pipeline 触发（REST 兜底，主路径走 Agent）— PRD §4.1/§4.2."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.pipelines.registry import PIPELINE_REGISTRY
from app.schemas.pipeline import PipelineInfo, PipelineInvoke
from app.schemas.job import JobOut
from app.services.job_service import JobService

router = APIRouter()


@router.get("", response_model=list[PipelineInfo])
async def list_pipelines() -> list[PipelineInfo]:
    return [PipelineInfo(name=name, endpoint=cls.endpoint, priority=cls.default_priority)
            for name, cls in PIPELINE_REGISTRY.items()]


@router.post("/{pipeline_name}/invoke", response_model=JobOut)
async def invoke(
    pipeline_name: str,
    payload: PipelineInvoke,
    db: AsyncSession = Depends(get_db),
) -> JobOut:
    return await JobService(db).submit(
        pipeline=pipeline_name,
        inputs=payload.inputs,
        project_id=payload.project_id,
        priority=payload.priority,
    )

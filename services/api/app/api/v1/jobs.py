"""任务队列管理接口 — PRD §6.2 进度 / 取消 + §4.3 DAG."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.job import JobOut, ChainCreate, ChainOut, JobProgress
from app.services.job_service import JobService

router = APIRouter()


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)) -> JobOut:
    return await JobService(db).get(job_id)


@router.get("/{job_id}/progress", response_model=JobProgress)
async def get_progress(job_id: str, db: AsyncSession = Depends(get_db)) -> JobProgress:
    return await JobService(db).query_progress(job_id)


@router.post("/{job_id}/cancel", response_model=JobOut)
async def cancel_job(job_id: str, db: AsyncSession = Depends(get_db)) -> JobOut:
    return await JobService(db).cancel(job_id)


@router.post("/chains", response_model=ChainOut)
async def create_chain(payload: ChainCreate, db: AsyncSession = Depends(get_db)) -> ChainOut:
    """一次性注册一个 DAG（PRD §4.3 场景）."""
    return await JobService(db).chain(payload.steps, project_id=payload.project_id)


@router.post("/chains/{chain_id}/cancel", response_model=ChainOut)
async def cancel_chain(chain_id: str, db: AsyncSession = Depends(get_db)) -> ChainOut:
    return await JobService(db).cancel_chain(chain_id)


@router.get("/chains/{chain_id}", response_model=ChainOut)
async def get_chain(chain_id: str, db: AsyncSession = Depends(get_db)) -> ChainOut:
    return await JobService(db).get_chain(chain_id)

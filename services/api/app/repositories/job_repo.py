from sqlalchemy import select
from app.models.pipeline_job import PipelineJob, JobStatus
from app.repositories.base import BaseRepository


class JobRepository(BaseRepository[PipelineJob]):
    model = PipelineJob

    async def list_by_chain(self, chain_id: str) -> list[PipelineJob]:
        res = await self.db.execute(
            select(PipelineJob).where(PipelineJob.chain_id == chain_id)
        )
        return list(res.scalars().all())

    async def list_children(self, parent_id: str) -> list[PipelineJob]:
        res = await self.db.execute(
            select(PipelineJob).where(PipelineJob.parent_job_id == parent_id)
        )
        return list(res.scalars().all())

    async def list_active_by_chain(self, chain_id: str) -> list[PipelineJob]:
        res = await self.db.execute(
            select(PipelineJob).where(
                PipelineJob.chain_id == chain_id,
                PipelineJob.status.in_([JobStatus.QUEUED, JobStatus.RUNNING, JobStatus.WAITING_PARENT]),
            )
        )
        return list(res.scalars().all())

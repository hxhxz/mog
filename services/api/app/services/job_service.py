"""任务队列管理门面 — 全部 Pipeline 提交必经此处.

能力：
  - submit(pipeline, inputs, *, project_id, priority, parent_job_id, chain_id) -> JobOut
  - chain(steps, *, project_id) -> ChainOut                 # PRD §4.3 DAG
  - cancel(job_id) / cancel_chain(chain_id)                 # PRD §6.2 取消
  - query_progress(job_id)                                  # PRD §6.2 进度
"""
import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.pipeline_job import PipelineJob, JobStatus, JobPriority
from app.pipelines.registry import PIPELINE_REGISTRY
from app.repositories.job_repo import JobRepository
from app.schemas.job import JobOut, JobProgress, ChainStep, ChainOut


class JobService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = JobRepository(db)

    # -------- submit --------
    async def submit(
        self,
        pipeline: str,
        inputs: dict,
        *,
        project_id: str,
        priority: str = "realtime",
        parent_job_id: str | None = None,
        chain_id: str | None = None,
    ) -> JobOut:
        if pipeline not in PIPELINE_REGISTRY:
            raise HTTPException(status_code=400, detail=f"unknown pipeline: {pipeline}")

        status = JobStatus.WAITING_PARENT if parent_job_id else JobStatus.QUEUED
        job = PipelineJob(
            project_id=project_id,
            pipeline=pipeline,
            priority=JobPriority(priority),
            status=status,
            parent_job_id=parent_job_id,
            chain_id=chain_id,
            inputs=inputs,
        )
        await self.repo.add(job)
        await self.repo.commit()

        if status == JobStatus.QUEUED:
            self._dispatch(job)
        return JobOut.model_validate(job)

    # -------- chain (DAG) --------
    async def chain(self, steps: list[ChainStep], *, project_id: str) -> ChainOut:
        chain_id = str(uuid.uuid4())
        created: list[PipelineJob] = []
        for idx, step in enumerate(steps):
            parent = created[step.depends_on[0]].id if step.depends_on else None
            status = JobStatus.WAITING_PARENT if parent else JobStatus.QUEUED
            job = PipelineJob(
                project_id=project_id,
                pipeline=step.pipeline,
                priority=JobPriority(step.priority),
                status=status,
                parent_job_id=parent,
                chain_id=chain_id,
                inputs=step.inputs,
            )
            await self.repo.add(job)
            created.append(job)
        await self.repo.commit()

        for job in created:
            if job.status == JobStatus.QUEUED:
                self._dispatch(job)

        return ChainOut(
            id=chain_id,
            project_id=project_id,
            jobs=[JobOut.model_validate(j) for j in created],
        )

    async def get_chain(self, chain_id: str) -> ChainOut:
        jobs = await self.repo.list_by_chain(chain_id)
        if not jobs:
            raise HTTPException(status_code=404, detail="chain not found")
        return ChainOut(
            id=chain_id,
            project_id=jobs[0].project_id,
            jobs=[JobOut.model_validate(j) for j in jobs],
        )

    # -------- cancel --------
    async def cancel(self, job_id: str) -> JobOut:
        job = await self.repo.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        self._revoke_celery(job)
        job.status = JobStatus.CANCELED if job.status == JobStatus.QUEUED else JobStatus.CANCELING
        await self.repo.commit()
        return JobOut.model_validate(job)

    async def cancel_chain(self, chain_id: str) -> ChainOut:
        jobs = await self.repo.list_active_by_chain(chain_id)
        for job in jobs:
            self._revoke_celery(job)
            job.status = JobStatus.CANCELED if job.status == JobStatus.QUEUED else JobStatus.CANCELING
        await self.repo.commit()
        return await self.get_chain(chain_id)

    # -------- progress --------
    async def query_progress(self, job_id: str) -> JobProgress:
        job = await self.repo.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        return JobProgress(id=job.id, status=job.status.value, progress=job.progress)

    async def get(self, job_id: str) -> JobOut:
        job = await self.repo.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        return JobOut.model_validate(job)

    # -------- internals --------
    def _dispatch(self, job: PipelineJob) -> None:
        """把 job 交给 Celery。失败时仅记录，由重试机制兜底。"""
        try:
            from app.tasks.pipeline_tasks import run_pipeline  # Celery client registered in worker
            queue = "queue_background" if job.priority == JobPriority.BACKGROUND else "queue_realtime"
            async_result = run_pipeline.apply_async(args=[job.id], queue=queue)
            job.celery_task_id = async_result.id
        except Exception as exc:  # pragma: no cover
            # MVP 阶段 pipeline_tasks 可能还未部署，仅记录不中断
            job.error_detail = {"dispatch_error": str(exc)}

    def _revoke_celery(self, job: PipelineJob) -> None:
        if not job.celery_task_id:
            return
        try:
            from celery.result import AsyncResult
            AsyncResult(job.celery_task_id).revoke(terminate=True, signal="SIGTERM")
        except Exception:
            pass

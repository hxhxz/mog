"""API 进程用的 Celery task 客户端引用.

真实执行逻辑在 services/worker/app/tasks/pipeline_tasks.py。
这里只需要 task 名与 worker 侧一致，便于 `apply_async`。
"""
from celery import Celery
from app.core.config import settings

celery_app = Celery("mog", broker=settings.redis_url, backend=settings.redis_url)


@celery_app.task(name="mog.pipeline.run")
def run_pipeline(job_id: str) -> dict:
    """Stub - worker provides the real implementation."""
    return {"job_id": job_id, "status": "stub"}

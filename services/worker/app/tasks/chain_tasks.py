"""DAG 回调任务 — 父节点成功后把子节点 WAITING_PARENT → QUEUED 并入队.

由 pipeline_tasks.run_pipeline 在 on_success 时触发：
    chain_tasks.advance_children.delay(job_id=parent_id)
"""
from app.celery_app import celery_app


@celery_app.task(name="mog.chain.advance_children")
def advance_children(parent_job_id: str) -> dict:
    """
    MVP stub. 真实实现：
      1. 查 DB 所有 parent_job_id = parent_job_id 的 children
      2. 检查每个 child 的 depends_on 是否全部 success
      3. 若是，置 QUEUED 并 apply_async 到对应队列
    """
    return {"parent": parent_job_id, "status": "stub"}

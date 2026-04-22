"""后处理：超分 / 拼接 — PRD §3.1 Step 5 + §4.3 Pipeline 6."""
from app.celery_app import celery_app


@celery_app.task(name="mog.postprocess.upscale_and_concat")
def upscale_and_concat(project_id: str, segment_ids: list[str]) -> dict:
    """批量超分 → 拼接 → 对齐音轨，全静默跑在 queue_background."""
    return {"project_id": project_id, "status": "stub", "segments": segment_ids}

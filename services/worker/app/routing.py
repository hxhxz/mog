"""Pipeline 名 → Celery queue 路由表."""

# 与 API 侧 app/pipelines/*.default_priority 保持一致
BACKGROUND_PIPELINES = {"upscale"}

TASK_ROUTES = {
    # Pipeline 主任务按 job.priority 动态路由（见 job_service._dispatch），默认落到 realtime
    "mog.pipeline.run": {"queue": "queue_realtime"},
    # 训练任务一律走 background
    "mog.training.*": {"queue": "queue_background"},
    # 后处理（拼接前的静默超分）也走 background
    "mog.postprocess.*": {"queue": "queue_background"},
    # DAG 回调任务走 realtime（轻量调度）
    "mog.chain.*": {"queue": "queue_realtime"},
}

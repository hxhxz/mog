"""Celery app — 双队列策略 (PRD §任务队列管理)：
  - queue_realtime:  用户等待感知强的任务（文生图 / 图生视频 / ...）
  - queue_background: 静默任务（超分 / LoRA 训练 / 后处理）
"""
from celery import Celery
from app.settings import settings
from app.routing import TASK_ROUTES

celery_app = Celery(
    "mog",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=[
        "app.tasks.pipeline_tasks",
        "app.tasks.training_tasks",
        "app.tasks.postprocess_tasks",
        "app.tasks.chain_tasks",
    ],
)

celery_app.conf.update(
    task_routes=TASK_ROUTES,
    task_default_queue="queue_realtime",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_time_limit=60 * 60,        # 硬上限 1 小时
    task_soft_time_limit=55 * 60,
    result_expires=3600 * 24,
)

"""Celery task 客户端存根.

API 进程通过 `from app.tasks.pipeline_tasks import run_pipeline` 拿到 task handle 后调用 .apply_async，
实际执行在 services/worker。同一个 Celery app 名字保证路由正确。
"""

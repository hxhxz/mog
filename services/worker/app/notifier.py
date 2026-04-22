"""任务状态/进度变更 → Redis Pub/Sub → API WebSocket 广播."""
import json
from redis import Redis
from app.settings import settings

_redis: Redis | None = None


def _client() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def publish(project_id: str, event: dict) -> None:
    _client().publish(f"chan:project:{project_id}", json.dumps(event))


def progress(project_id: str, job_id: str, pct: int, message: str | None = None) -> None:
    publish(project_id, {
        "type": "job.progress",
        "job_id": job_id,
        "progress": pct,
        "message": message,
    })


def status(project_id: str, job_id: str, status: str, outputs: dict | None = None) -> None:
    publish(project_id, {
        "type": "job.status",
        "job_id": job_id,
        "status": status,
        "outputs": outputs or {},
    })

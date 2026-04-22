"""Agent 会话历史持久化 — 默认 Redis List."""
import json
from redis import Redis
from app.settings import settings

_redis: Redis | None = None


def _client() -> Redis:
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis


def append(project_id: str, role: str, content: str) -> None:
    _client().rpush(f"agent:history:{project_id}",
                    json.dumps({"role": role, "content": content}))


def history(project_id: str, limit: int = 50) -> list[dict]:
    items = _client().lrange(f"agent:history:{project_id}", -limit, -1)
    return [json.loads(x) for x in items]

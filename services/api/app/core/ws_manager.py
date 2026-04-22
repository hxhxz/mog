"""WebSocket 连接池 + Redis Pub/Sub 桥接 — PRD §5.2 数据流."""
import asyncio
import json
from collections import defaultdict
from fastapi import WebSocket
from redis.asyncio import Redis
from app.core.config import settings


class WSManager:
    def __init__(self) -> None:
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)
        self._redis: Redis | None = None
        self._pubsub_task: asyncio.Task | None = None

    async def start(self) -> None:
        self._redis = Redis.from_url(settings.redis_url, decode_responses=True)
        self._pubsub_task = asyncio.create_task(self._listen())

    async def stop(self) -> None:
        if self._pubsub_task:
            self._pubsub_task.cancel()
        if self._redis:
            await self._redis.close()

    async def connect(self, project_id: str, ws: WebSocket) -> None:
        await ws.accept()
        self._channels[project_id].add(ws)

    def disconnect(self, project_id: str, ws: WebSocket) -> None:
        self._channels[project_id].discard(ws)

    async def broadcast(self, project_id: str, payload: dict) -> None:
        dead: list[WebSocket] = []
        for ws in self._channels.get(project_id, set()):
            try:
                await ws.send_json(payload)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._channels[project_id].discard(ws)

    async def _listen(self) -> None:
        """订阅 Redis `chan:project:*`，Worker 用来推送进度/结果."""
        assert self._redis
        pubsub = self._redis.pubsub()
        await pubsub.psubscribe("chan:project:*")
        async for msg in pubsub.listen():
            if msg["type"] != "pmessage":
                continue
            try:
                project_id = msg["channel"].split(":")[-1]
                payload = json.loads(msg["data"])
                await self.broadcast(project_id, payload)
            except Exception:
                continue


ws_manager = WSManager()

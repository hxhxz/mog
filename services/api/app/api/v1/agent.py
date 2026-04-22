"""Agent 入口：REST + WebSocket（给前端）."""
import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.config import settings
from app.core.ws_manager import ws_manager
from app.schemas.agent import AgentChatRequest, AgentChatResponse

router = APIRouter()


@router.post("/chat", response_model=AgentChatResponse)
async def chat(payload: AgentChatRequest) -> AgentChatResponse:
    """转发到 services/agent（smolagents 服务）."""
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{settings.agent_service_url}/chat", json=payload.model_dump())
        resp.raise_for_status()
        return AgentChatResponse(**resp.json())


@router.websocket("/ws/{project_id}")
async def agent_ws(websocket: WebSocket, project_id: str) -> None:
    await ws_manager.connect(project_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # MVP: echo + forward to agent service
            await ws_manager.broadcast(project_id, {"type": "echo", "data": data})
    except WebSocketDisconnect:
        ws_manager.disconnect(project_id, websocket)

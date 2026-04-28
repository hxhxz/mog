"""Agent 服务入口 — 独立进程，内部被 services/api 转发调用.

端口：
  8100 — FastAPI (chat / health)
  8101 — MCP SSE server (via mcp_main.py)
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import get_agent



app = FastAPI(title="mog agent", version="0.1.0")


class ChatRequest(BaseModel):
    project_id: str
    message: str
    context: dict | None = None


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[dict] = []


@app.get("/health")
async def health() -> dict:
    return {"status": "ok", "service": "agent"}


@app.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    agent = get_agent()
    reply = agent.run(payload.message, additional_args={"project_id": payload.project_id,
                                                         "context": payload.context or {}})
    return ChatResponse(reply=str(reply), tool_calls=[])

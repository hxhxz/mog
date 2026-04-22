from typing import Any
from pydantic import BaseModel


class AgentChatRequest(BaseModel):
    project_id: str
    message: str
    context: dict[str, Any] | None = None


class ToolCall(BaseModel):
    name: str
    arguments: dict[str, Any]


class AgentChatResponse(BaseModel):
    reply: str
    tool_calls: list[ToolCall] = []

"""Pipeline I/O 契约 — 对齐 PRD §4.1/§4.2 表格."""
from typing import Any, Literal
from pydantic import BaseModel


class PipelineInfo(BaseModel):
    name: str
    endpoint: str
    priority: Literal["realtime", "background"]


class PipelineInvoke(BaseModel):
    project_id: str
    inputs: dict[str, Any]
    priority: Literal["realtime", "background"] = "realtime"

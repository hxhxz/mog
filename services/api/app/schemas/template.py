"""Template DTOs — ComfyUI workflow 导入/调用契约."""
from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field


class TemplateImport(BaseModel):
    """导入一个 ComfyUI workflow 模板.

    `workflow` 字段直接接收 ComfyUI /prompt API JSON，原样存储。
    `input_nodes` 标注哪些 node_id 是用户素材槽位（供前端/Agent 展示），可选。
    """
    name: str
    description: str | None = None
    category: str | None = None
    pipeline: str
    workflow: dict[str, Any] = Field(..., description="ComfyUI /prompt API JSON")
    input_nodes: list[str] = Field(default_factory=list, description="用户可覆写的 node_id 列表")
    preview_url: str | None = None
    tags: list[str] = Field(default_factory=list)
    is_mcp_exposed: bool = True


class TemplateUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    category: str | None = None
    preview_url: str | None = None
    tags: list[str] | None = None
    is_mcp_exposed: bool | None = None
    status: Literal["draft", "published", "archived"] | None = None


class TemplateOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    name: str
    description: str | None
    category: str | None
    pipeline: str
    input_nodes: list[str]
    preview_url: str | None
    tags: list[str]
    status: str
    is_mcp_exposed: bool


class TemplateDetail(TemplateOut):
    workflow: dict[str, Any]


class TemplateInvoke(BaseModel):
    """通过模板驱动 pipeline 执行.

    `materials` 是对 workflow 中指定 node 的 inputs 覆写，key 格式为 "{node_id}.inputs.{field}"。
    例：{"6.inputs.text": "一个古装女子", "12.inputs.image": "oss://..."}
    """
    project_id: str
    materials: dict[str, Any] = Field(default_factory=dict)
    priority: Literal["realtime", "background"] = "realtime"

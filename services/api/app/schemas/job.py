"""任务队列管理 DTO."""
from typing import Any, Literal
from datetime import datetime
from pydantic import BaseModel


class JobOut(BaseModel):
    id: str
    project_id: str
    pipeline: str
    status: str
    priority: str
    progress: int
    parent_job_id: str | None = None
    chain_id: str | None = None
    inputs: dict[str, Any]
    outputs: dict[str, Any] = {}
    error_detail: dict[str, Any] | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JobProgress(BaseModel):
    id: str
    status: str
    progress: int
    message: str | None = None


class ChainStep(BaseModel):
    pipeline: str
    inputs: dict[str, Any]
    priority: Literal["realtime", "background"] = "realtime"
    depends_on: list[int] = []  # 索引式依赖（引用 steps 中的其它 step）


class ChainCreate(BaseModel):
    project_id: str
    steps: list[ChainStep]


class ChainOut(BaseModel):
    id: str
    project_id: str
    jobs: list[JobOut]

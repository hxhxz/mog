from __future__ import annotations
from typing import Any
from pydantic import BaseModel
from app.models.project_step import StepName, StepStatus


class ProjectStepOut(BaseModel):
    model_config = {"from_attributes": True}

    id: str
    project_id: str
    step: StepName
    status: StepStatus
    inputs: dict[str, Any]
    outputs: dict[str, Any]
    chain_id: str | None
    revision_note: str | None


class StepStart(BaseModel):
    """手动触发某一步骤开始生成（前端或 Agent 调用）."""
    inputs: dict[str, Any] = {}


class StepConfirm(BaseModel):
    """用户在 review 状态下确认产物，推进到 done."""
    pass


class StepModify(BaseModel):
    """用户修改某步产物，级联重置下游步骤.

    `inputs` 为修改后的新输入；`revision_note` 说明修改原因，Agent 可据此重新生成。
    下游步骤（含本步）将被重置为 pending，本步重新进入生成流程。
    """
    inputs: dict[str, Any]
    revision_note: str | None = None


class ProjectStepsOut(BaseModel):
    """项目全部步骤列表 + 当前活跃步骤."""
    project_id: str
    current_step: StepName | None
    steps: list[ProjectStepOut]

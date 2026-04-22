"""项目流水线步骤接口 (PRD §3.1 六步创作流程)."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.models.project_step import StepName
from app.schemas.project_step import (
    ProjectStepsOut, ProjectStepOut, StepStart, StepConfirm, StepModify,
)
from app.services.project_step_service import ProjectStepService

router = APIRouter()


@router.get("/{project_id}/steps", response_model=ProjectStepsOut)
async def get_steps(project_id: str, db: AsyncSession = Depends(get_db)) -> ProjectStepsOut:
    """获取项目全部步骤状态及当前进行中的步骤."""
    return await ProjectStepService(db).get_all(project_id)


@router.get("/{project_id}/steps/{step}", response_model=ProjectStepOut)
async def get_step(
    project_id: str, step: StepName, db: AsyncSession = Depends(get_db)
) -> ProjectStepOut:
    return await ProjectStepService(db).get_step(project_id, step)


@router.post("/{project_id}/steps/{step}/start", response_model=ProjectStepOut)
async def start_step(
    project_id: str,
    step: StepName,
    payload: StepStart,
    db: AsyncSession = Depends(get_db),
) -> ProjectStepOut:
    """触发某步开始生成（前置：上一步必须已完成）."""
    return await ProjectStepService(db).start(project_id, step, payload.inputs or None)


@router.post("/{project_id}/steps/{step}/confirm", response_model=ProjectStepOut)
async def confirm_step(
    project_id: str,
    step: StepName,
    _: StepConfirm,
    db: AsyncSession = Depends(get_db),
) -> ProjectStepOut:
    """用户确认 review 状态的步骤产物，推进到 done."""
    return await ProjectStepService(db).confirm(project_id, step)


@router.post("/{project_id}/steps/{step}/modify", response_model=ProjectStepsOut)
async def modify_step(
    project_id: str,
    step: StepName,
    payload: StepModify,
    db: AsyncSession = Depends(get_db),
) -> ProjectStepsOut:
    """修改某步产物，级联重置该步及所有下游步骤为 pending.

    返回整个项目的步骤列表，让前端一次性刷新全部状态。
    """
    return await ProjectStepService(db).modify(project_id, step, payload)


@router.post("/{project_id}/steps/{step}/complete", response_model=ProjectStepOut)
async def complete_step(
    project_id: str,
    step: StepName,
    outputs: dict,
    chain_id: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> ProjectStepOut:
    """Worker / Agent 内部回调：标记步骤生成完成并写入产物."""
    return await ProjectStepService(db).complete(project_id, step, outputs, chain_id)

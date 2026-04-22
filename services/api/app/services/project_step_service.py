"""项目流水线步骤管理 — 6步创作流程的推进、修改、级联重置.

核心操作：
  - initialize(project_id)     项目创建时初始化 6 个步骤行（全部 pending）
  - start(project_id, step)    触发某步生成（PENDING/REVIEW → RUNNING）
  - complete(project_id, step) Worker 回调：生成完成（RUNNING → REVIEW or DONE）
  - confirm(project_id, step)  用户确认 review 步骤（REVIEW → DONE），自动推进下一步
  - modify(project_id, step)   用户修改某步（级联重置该步及所有下游 → PENDING）
  - fail(project_id, step)     Worker 回调：生成失败（RUNNING → FAILED）

级联重置规则（STEP_ORDER 顺序）：
  修改 script → 重置 storyboard text2image image2video concat audio
  修改 storyboard → 重置 text2image image2video concat audio
  修改 text2image → 重置 image2video concat audio
  ... 以此类推
"""
from __future__ import annotations
from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_step import ProjectStep, StepName, StepStatus, STEP_ORDER, REVIEW_STEPS
from app.repositories.project_step_repo import ProjectStepRepository
from app.schemas.project_step import ProjectStepOut, ProjectStepsOut, StepModify


class ProjectStepService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ProjectStepRepository(db)

    # ──────────────── 初始化 ────────────────

    async def initialize(self, project_id: str) -> list[ProjectStepOut]:
        """项目创建时调用，写入 6 个步骤行（幂等）."""
        existing = await self.repo.list_for_project(project_id)
        existing_names = {s.step for s in existing}
        created = []
        for step in STEP_ORDER:
            if step not in existing_names:
                row = ProjectStep(project_id=project_id, step=step)
                await self.repo.add(row)
                created.append(row)
        await self.repo.commit()
        all_steps = await self.repo.list_for_project(project_id)
        return [ProjectStepOut.model_validate(s) for s in all_steps]

    # ──────────────── 查询 ────────────────

    async def get_all(self, project_id: str) -> ProjectStepsOut:
        steps = await self.repo.list_for_project(project_id)
        current = next(
            (s.step for s in steps if s.status in (StepStatus.RUNNING, StepStatus.REVIEW)),
            next((s.step for s in steps if s.status == StepStatus.PENDING), None),
        )
        return ProjectStepsOut(
            project_id=project_id,
            current_step=current,
            steps=[ProjectStepOut.model_validate(s) for s in steps],
        )

    async def get_step(self, project_id: str, step: StepName) -> ProjectStepOut:
        row = await self._get_or_404(project_id, step)
        return ProjectStepOut.model_validate(row)

    # ──────────────── 推进 ────────────────

    async def start(self, project_id: str, step: StepName,
                    inputs: dict[str, Any] | None = None) -> ProjectStepOut:
        """触发某步开始生成.

        前置：上一步必须是 done（或是第一步）。
        """
        row = await self._get_or_404(project_id, step)
        if row.status not in (StepStatus.PENDING, StepStatus.FAILED):
            raise HTTPException(
                status_code=409,
                detail=f"step {step} is {row.status}, cannot start",
            )
        _assert_prev_done(step, await self.repo.list_for_project(project_id))
        if inputs:
            row.inputs = inputs
        row.status = StepStatus.RUNNING
        await self.repo.commit()
        return ProjectStepOut.model_validate(row)

    async def complete(self, project_id: str, step: StepName,
                       outputs: dict[str, Any], chain_id: str | None = None) -> ProjectStepOut:
        """Worker / Agent 回调：本步生成完成，写入产物.

        需要 review 的步骤（script / storyboard）进入 REVIEW；其余直接 DONE。
        """
        row = await self._get_or_404(project_id, step)
        if row.status != StepStatus.RUNNING:
            raise HTTPException(status_code=409,
                                detail=f"step {step} is not running")
        row.outputs = outputs
        if chain_id:
            row.chain_id = chain_id
        row.status = StepStatus.REVIEW if step in REVIEW_STEPS else StepStatus.DONE
        await self.repo.commit()
        return ProjectStepOut.model_validate(row)

    async def confirm(self, project_id: str, step: StepName) -> ProjectStepOut:
        """用户确认 review 步骤，推进到 done."""
        row = await self._get_or_404(project_id, step)
        if row.status != StepStatus.REVIEW:
            raise HTTPException(status_code=409,
                                detail=f"step {step} is not in review")
        row.status = StepStatus.DONE
        await self.repo.commit()
        return ProjectStepOut.model_validate(row)

    async def fail(self, project_id: str, step: StepName,
                   error: str | None = None) -> ProjectStepOut:
        """Worker 回调：生成失败."""
        row = await self._get_or_404(project_id, step)
        row.status = StepStatus.FAILED
        if error:
            row.outputs = {**row.outputs, "error": error}
        await self.repo.commit()
        return ProjectStepOut.model_validate(row)

    # ──────────────── 修改（级联重置）────────────────

    async def modify(self, project_id: str, step: StepName,
                     payload: StepModify) -> ProjectStepsOut:
        """用户修改某步，级联重置该步及所有下游步骤为 pending.

        本步写入新 inputs 和 revision_note 后重置为 PENDING，
        等待用户或 Agent 重新触发 start()。
        """
        downstream = await self.repo.list_downstream(project_id, step)
        if not downstream:
            raise HTTPException(status_code=404, detail=f"step {step} not found")

        for row in downstream:
            if row.step == step:
                row.inputs = payload.inputs
                row.revision_note = payload.revision_note
            row.status = StepStatus.PENDING
            row.outputs = {}
            row.chain_id = None

        await self.repo.commit()
        return await self.get_all(project_id)

    # ──────────────── internal ────────────────

    async def _get_or_404(self, project_id: str, step: StepName) -> ProjectStep:
        row = await self.repo.get_by_step(project_id, step)
        if not row:
            raise HTTPException(status_code=404,
                                detail=f"step {step} not found for project {project_id}")
        return row


def _assert_prev_done(step: StepName, all_steps: list[ProjectStep]) -> None:
    idx = STEP_ORDER.index(step)
    if idx == 0:
        return
    prev_step = STEP_ORDER[idx - 1]
    prev_row = next((s for s in all_steps if s.step == prev_step), None)
    if not prev_row or prev_row.status != StepStatus.DONE:
        raise HTTPException(
            status_code=409,
            detail=f"previous step '{prev_step}' must be done before starting '{step}'",
        )

from sqlalchemy import select
from app.models.project_step import ProjectStep, StepName, StepStatus, STEP_ORDER
from app.repositories.base import BaseRepository


class ProjectStepRepository(BaseRepository[ProjectStep]):
    model = ProjectStep

    async def get_by_step(self, project_id: str, step: StepName) -> ProjectStep | None:
        res = await self.db.execute(
            select(ProjectStep).where(
                ProjectStep.project_id == project_id,
                ProjectStep.step == step,
            )
        )
        return res.scalar_one_or_none()

    async def list_for_project(self, project_id: str) -> list[ProjectStep]:
        res = await self.db.execute(
            select(ProjectStep)
            .where(ProjectStep.project_id == project_id)
            .order_by(ProjectStep.step)
        )
        rows = {r.step: r for r in res.scalars().all()}
        # 按 STEP_ORDER 排序返回（保证顺序稳定）
        return [rows[s] for s in STEP_ORDER if s in rows]

    async def list_downstream(self, project_id: str, from_step: StepName) -> list[ProjectStep]:
        """返回 from_step 之后（含）的所有步骤行."""
        idx = STEP_ORDER.index(from_step)
        downstream_names = STEP_ORDER[idx:]
        res = await self.db.execute(
            select(ProjectStep).where(
                ProjectStep.project_id == project_id,
                ProjectStep.step.in_(downstream_names),
            )
        )
        rows = {r.step: r for r in res.scalars().all()}
        return [rows[s] for s in downstream_names if s in rows]

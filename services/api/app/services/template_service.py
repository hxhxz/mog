"""模板管理 + 执行 — 将 materials 合并进 ComfyUI workflow JSON 后投递给 JobService."""
from __future__ import annotations
import copy
from typing import Any

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.template import Template
from app.repositories.template_repo import TemplateRepository
from app.schemas.template import TemplateImport, TemplateUpdate, TemplateOut, TemplateDetail, TemplateInvoke
from app.schemas.job import JobOut
from app.services.job_service import JobService


class TemplateService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = TemplateRepository(db)

    # ──────────────── CRUD ────────────────

    async def import_template(self, payload: TemplateImport) -> TemplateDetail:
        tpl = Template(
            name=payload.name,
            description=payload.description,
            category=payload.category,
            pipeline=payload.pipeline,
            workflow=payload.workflow,
            input_nodes=payload.input_nodes,
            preview_url=payload.preview_url,
            tags=payload.tags,
            is_mcp_exposed=payload.is_mcp_exposed,
        )
        await self.repo.add(tpl)
        await self.repo.commit()
        return TemplateDetail.model_validate(tpl)

    async def list_templates(
        self, *, pipeline: str | None = None, category: str | None = None
    ) -> list[TemplateOut]:
        items = await self.repo.list_published(pipeline=pipeline, category=category)
        return [TemplateOut.model_validate(t) for t in items]

    async def get_template(self, template_id: str) -> TemplateDetail:
        tpl = await self.repo.get(template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="template not found")
        return TemplateDetail.model_validate(tpl)

    async def update_template(self, template_id: str, payload: TemplateUpdate) -> TemplateDetail:
        tpl = await self.repo.get(template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="template not found")
        for field, value in payload.model_dump(exclude_none=True).items():
            setattr(tpl, field, value)
        await self.repo.commit()
        return TemplateDetail.model_validate(tpl)

    async def delete_template(self, template_id: str) -> None:
        tpl = await self.repo.get(template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="template not found")
        await self.db.delete(tpl)
        await self.repo.commit()

    # ──────────────── invoke ────────────────

    async def invoke(self, template_id: str, payload: TemplateInvoke) -> JobOut:
        """将 materials 合并进 workflow，以 template_id 对应的 pipeline 提交任务."""
        tpl = await self.repo.get(template_id)
        if not tpl:
            raise HTTPException(status_code=404, detail="template not found")

        merged_workflow = _apply_materials(tpl.workflow, payload.materials)

        return await JobService(self.db).submit(
            pipeline=tpl.pipeline,
            inputs={"workflow": merged_workflow, "template_id": template_id},
            project_id=payload.project_id,
            priority=payload.priority,
        )

    # ──────────────── MCP helper ────────────────

    async def list_mcp_tools(self) -> list[dict[str, Any]]:
        """返回所有暴露给 MCP 的模板描述，供 MCP server 动态注册工具."""
        items = await self.repo.list_mcp_exposed()
        return [
            {
                "id": t.id,
                "name": t.name,
                "description": t.description or t.name,
                "pipeline": t.pipeline,
                "input_nodes": t.input_nodes,
            }
            for t in items
        ]


# ──────────────── materials merge ────────────────

def _apply_materials(workflow: dict[str, Any], materials: dict[str, Any]) -> dict[str, Any]:
    """将 materials 覆写到 ComfyUI workflow JSON 指定节点的 inputs.

    key 格式："{node_id}.inputs.{field}"，例如 "6.inputs.text"
    不符合格式的 key 静默跳过，避免意外破坏 workflow 结构。
    """
    result = copy.deepcopy(workflow)
    for key, value in materials.items():
        parts = key.split(".")
        if len(parts) != 3 or parts[1] != "inputs":
            continue
        node_id, _, field = parts
        node = result.get(node_id)
        if isinstance(node, dict) and "inputs" in node:
            node["inputs"][field] = value
    return result

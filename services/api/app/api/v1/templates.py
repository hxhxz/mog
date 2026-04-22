"""模板管理 + 执行 REST 接口."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db
from app.schemas.template import TemplateImport, TemplateUpdate, TemplateOut, TemplateDetail, TemplateInvoke
from app.schemas.job import JobOut
from app.services.template_service import TemplateService

router = APIRouter()


@router.get("", response_model=list[TemplateOut])
async def list_templates(
    pipeline: str | None = Query(None),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> list[TemplateOut]:
    return await TemplateService(db).list_templates(pipeline=pipeline, category=category)


@router.post("", response_model=TemplateDetail, status_code=201)
async def import_template(
    payload: TemplateImport,
    db: AsyncSession = Depends(get_db),
) -> TemplateDetail:
    return await TemplateService(db).import_template(payload)


@router.get("/{template_id}", response_model=TemplateDetail)
async def get_template(template_id: str, db: AsyncSession = Depends(get_db)) -> TemplateDetail:
    return await TemplateService(db).get_template(template_id)


@router.patch("/{template_id}", response_model=TemplateDetail)
async def update_template(
    template_id: str,
    payload: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
) -> TemplateDetail:
    return await TemplateService(db).update_template(template_id, payload)


@router.delete("/{template_id}", status_code=204)
async def delete_template(template_id: str, db: AsyncSession = Depends(get_db)) -> None:
    await TemplateService(db).delete_template(template_id)


@router.post("/{template_id}/invoke", response_model=JobOut)
async def invoke_template(
    template_id: str,
    payload: TemplateInvoke,
    db: AsyncSession = Depends(get_db),
) -> JobOut:
    """用模板驱动 pipeline 执行任务.

    `materials` 覆写 workflow 指定节点，格式 `"{node_id}.inputs.{field}"`。
    """
    return await TemplateService(db).invoke(template_id, payload)

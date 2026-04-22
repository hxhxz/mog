from sqlalchemy import select
from app.models.template import Template, TemplateStatus
from app.repositories.base import BaseRepository


class TemplateRepository(BaseRepository[Template]):
    model = Template

    async def list_published(self, *, pipeline: str | None = None, category: str | None = None) -> list[Template]:
        q = select(Template).where(Template.status == TemplateStatus.PUBLISHED)
        if pipeline:
            q = q.where(Template.pipeline == pipeline)
        if category:
            q = q.where(Template.category == category)
        res = await self.db.execute(q.order_by(Template.created_at.desc()))
        return list(res.scalars().all())

    async def list_mcp_exposed(self) -> list[Template]:
        res = await self.db.execute(
            select(Template).where(
                Template.status == TemplateStatus.PUBLISHED,
                Template.is_mcp_exposed.is_(True),
            )
        )
        return list(res.scalars().all())

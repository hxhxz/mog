"""ComfyUI 模板 — 原生 workflow JSON + 元数据.

模板结构完全由 ComfyUI 定义（即 /prompt API JSON 格式），我们不自定义槽位 schema。
Agent 调用时通过 `materials` 覆写指定 node 的 inputs，其余节点保持模板默认值。
"""
import enum
import uuid
from sqlalchemy import String, JSON, Enum, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class TemplateStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Template(Base, TimestampMixin):
    """ComfyUI workflow 模板.

    - `workflow`：ComfyUI 原生 /prompt API JSON（导入时原样保留）
    - `input_nodes`：声明哪些 node_id 是用户可覆写的输入槽；
       仅用于 Agent/前端展示 "这个模板需要提供什么素材"，执行时实际合并逻辑不依赖这里
    - `pipeline`：对应 PIPELINE_REGISTRY 里 9 个 ComfyUI 客户端之一，
       Worker 根据这个 key 选择用哪个 client 去 POST /prompt
    """
    __tablename__ = "templates"

    id: Mapped[str] = mapped_column(String(64), primary_key=True,
                                    default=lambda: f"tpl_{uuid.uuid4().hex[:12]}")
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(64), index=True)

    pipeline: Mapped[str] = mapped_column(String(64), index=True)
    workflow: Mapped[dict] = mapped_column(JSON, nullable=False)
    input_nodes: Mapped[list] = mapped_column(JSON, default=list)

    preview_url: Mapped[str | None] = mapped_column(String(500))
    tags: Mapped[list] = mapped_column(JSON, default=list)

    status: Mapped[TemplateStatus] = mapped_column(
        Enum(TemplateStatus), default=TemplateStatus.PUBLISHED, index=True
    )
    is_mcp_exposed: Mapped[bool] = mapped_column(Boolean, default=True)

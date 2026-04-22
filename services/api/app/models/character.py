"""PRD §3.1 Step 2 + §4.4 角色卡 / 角色 LoRA."""
import uuid
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Character(Base, TimestampMixin):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(100))
    reference_image_url: Mapped[str | None] = mapped_column(String(500))
    character_lora_id: Mapped[str | None] = mapped_column(String(36))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

    project = relationship("Project", back_populates="characters")

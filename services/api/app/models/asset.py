"""PRD §4.4 LoRA + 生成产物 (image/video/audio)."""
import uuid
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    kind: Mapped[str] = mapped_column(String(32))  # style_lora / character_lora / image / video / audio
    name: Mapped[str] = mapped_column(String(200))
    url: Mapped[str] = mapped_column(String(500))
    owner_project_id: Mapped[str | None] = mapped_column(String(36))
    meta: Mapped[dict] = mapped_column(JSON, default=dict)

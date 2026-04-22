"""PRD §3.3 项目级 Context 的持久化载体."""
import uuid
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    owner_id: Mapped[str | None] = mapped_column(String(64))

    # PRD §3.3 Context 字段
    style_lora_id: Mapped[str | None] = mapped_column(String(36))
    audio_track_url: Mapped[str | None] = mapped_column(String(500))
    context: Mapped[dict] = mapped_column(JSON, default=dict)  # 灵活扩展字段

    segments = relationship("Segment", back_populates="project", cascade="all, delete-orphan")
    characters = relationship("Character", back_populates="project", cascade="all, delete-orphan")

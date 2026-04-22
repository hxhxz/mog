"""任务队列管理 — 参考 Plan §任务队列管理机制."""
import enum
import uuid
from sqlalchemy import String, Integer, ForeignKey, JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    WAITING_PARENT = "waiting_parent"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELING = "canceling"
    CANCELED = "canceled"


class JobPriority(str, enum.Enum):
    REALTIME = "realtime"
    BACKGROUND = "background"


class PipelineJob(Base, TimestampMixin):
    __tablename__ = "pipeline_jobs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    pipeline: Mapped[str] = mapped_column(String(64))  # name in PIPELINE_REGISTRY

    priority: Mapped[JobPriority] = mapped_column(
        Enum(JobPriority), default=JobPriority.REALTIME
    )
    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)

    # DAG support (PRD §4.3 chained pipelines)
    parent_job_id: Mapped[str | None] = mapped_column(String(36))
    chain_id: Mapped[str | None] = mapped_column(String(36))

    # Progress / cancellation
    progress: Mapped[int] = mapped_column(Integer, default=0)
    celery_task_id: Mapped[str | None] = mapped_column(String(64))

    # Retry policy
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)

    inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    outputs: Mapped[dict] = mapped_column(JSON, default=dict)
    error_detail: Mapped[dict | None] = mapped_column(JSON)

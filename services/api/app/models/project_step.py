"""项目流水线步骤 — 6步创作流程的状态追踪 (PRD §3.1).

职责：
  - 跟踪每个项目当前走到哪一步、每步的状态
  - 存储每步的输入产物和输出产物
  - 关联触发的 pipeline_job（文生图以后的步骤）
  - 用户修改某步时，级联重置下游步骤

与 pipeline_jobs 的关系：
  pipeline_jobs 是 ComfyUI 层的原子任务；
  ProjectStep 是产品层的创作阶段，一个步骤可能触发多个 pipeline_job。
"""
import enum
import uuid
from sqlalchemy import String, JSON, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin


class StepName(str, enum.Enum):
    SCRIPT = "script"            # 剧本生成
    STORYBOARD = "storyboard"    # 分镜设计
    TEXT2IMAGE = "text2image"    # 文生图
    IMAGE2VIDEO = "image2video"  # 图生视频
    CONCAT = "concat"            # 视频合成
    AUDIO = "audio"              # 音效配乐


class StepStatus(str, enum.Enum):
    PENDING = "pending"      # 未开始（等待上一步完成或用户触发）
    RUNNING = "running"      # 生成中
    REVIEW = "review"        # 待用户确认（剧本、分镜等人工审核步骤）
    DONE = "done"            # 已完成
    FAILED = "failed"        # 生成失败


# 步骤顺序，用于级联重置下游
STEP_ORDER: list[StepName] = [
    StepName.SCRIPT,
    StepName.STORYBOARD,
    StepName.TEXT2IMAGE,
    StepName.IMAGE2VIDEO,
    StepName.CONCAT,
    StepName.AUDIO,
]

# 需要用户确认才能推进的步骤（生成后进入 review 而非直接 done）
REVIEW_STEPS = {StepName.SCRIPT, StepName.STORYBOARD}


class ProjectStep(Base, TimestampMixin):
    __tablename__ = "project_steps"

    id: Mapped[str] = mapped_column(String(36), primary_key=True,
                                    default=lambda: str(uuid.uuid4()))
    project_id: Mapped[str] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    step: Mapped[StepName] = mapped_column(Enum(StepName), nullable=False)
    status: Mapped[StepStatus] = mapped_column(
        Enum(StepStatus), nullable=False, default=StepStatus.PENDING
    )

    inputs: Mapped[dict] = mapped_column(JSON, default=dict)
    outputs: Mapped[dict] = mapped_column(JSON, default=dict)

    # 本步骤触发的 Celery chain（文生图 / 图生视频 / 视频合成 / 音效配乐）
    chain_id: Mapped[str | None] = mapped_column(String(36))

    # 用户在 review 阶段提交的修改意见，记录在此便于 Agent 重新生成
    revision_note: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        # 每个项目每个步骤只有一行
        __import__("sqlalchemy").UniqueConstraint("project_id", "step", name="uq_project_step"),
    )

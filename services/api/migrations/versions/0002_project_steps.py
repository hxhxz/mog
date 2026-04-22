"""add project_steps table

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-22 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "project_steps",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("project_id", sa.String(36),
                  sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("step", sa.String(16), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("inputs", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("outputs", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("chain_id", sa.String(36)),
        sa.Column("revision_note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True),
                  server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "step", name="uq_project_step"),
    )
    op.create_index("ix_project_steps_project_id", "project_steps", ["project_id"])
    op.create_index("ix_project_steps_status", "project_steps", ["status"])


def downgrade() -> None:
    op.drop_table("project_steps")

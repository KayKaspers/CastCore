"""platform metadata

Revision ID: 0012_platmeta
Revises: 0011_chfallback
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0012_platmeta"
down_revision: Union[str, None] = "0011_chfallback"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_metadata",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("stream_job_id", sa.Uuid(), sa.ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("platform", sa.String(24), nullable=False),
        sa.Column("title", sa.String(256), nullable=True),
        sa.Column("description_template", sa.Text(), nullable=True),
        sa.Column("category", sa.String(128), nullable=True),
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("language", sa.String(8), nullable=True),
        sa.Column("visibility", sa.String(16), nullable=False, server_default="public"),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("stream_job_id", "platform", name="uq_meta_job_platform"),
    )
    op.create_index("ix_platform_metadata_job", "platform_metadata", ["stream_job_id"])


def downgrade() -> None:
    op.drop_table("platform_metadata")

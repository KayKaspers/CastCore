"""Persisted preflight reports

Revision ID: 0016_preflight_reports
Revises: 0015_platform_accounts
Create Date: 2026-06-26
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0016_preflight_reports"
down_revision: Union[str, None] = "0015_platform_accounts"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "preflight_reports",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("stream_job_id", sa.Uuid(), sa.ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("level", sa.String(length=8), nullable=False),
        sa.Column("can_start", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("checks", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("started_by_user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_preflight_reports_job", "preflight_reports", ["stream_job_id"])


def downgrade() -> None:
    op.drop_index("ix_preflight_reports_job", table_name="preflight_reports")
    op.drop_table("preflight_reports")

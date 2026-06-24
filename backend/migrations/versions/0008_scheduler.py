"""scheduler entries

Revision ID: 0008_scheduler
Revises: 0007_recording
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0008_scheduler"
down_revision: Union[str, None] = "0007_recording"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "scheduler_entries",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("action", sa.String(24), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=True),
        sa.Column("schedule_type", sa.String(12), nullable=False, server_default="interval"),
        sa.Column("run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("interval_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("daily_time", sa.String(5), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("next_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_run_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_status", sa.String(256), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scheduler_next_run", "scheduler_entries", ["next_run_at"])


def downgrade() -> None:
    op.drop_table("scheduler_entries")

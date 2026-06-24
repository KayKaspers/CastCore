"""recording: recordings table + stream_jobs recording flags

Revision ID: 0007_recording
Revises: 0006_notify
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007_recording"
down_revision: Union[str, None] = "0006_notify"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("stream_jobs", sa.Column("recording_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("stream_jobs", sa.Column("recording_retention_days", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "recordings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("stream_job_id", sa.Uuid(), sa.ForeignKey("stream_jobs.id", ondelete="SET NULL"), nullable=True),
        sa.Column("output_id", sa.Uuid(), nullable=False),
        sa.Column("path", sa.String(2048), nullable=False),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("state", sa.String(16), nullable=False, server_default="recording"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("retention_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_recordings_job", "recordings", ["stream_job_id"])
    op.create_index("ix_recordings_output", "recordings", ["output_id"])


def downgrade() -> None:
    op.drop_table("recordings")
    op.drop_column("stream_jobs", "recording_retention_days")
    op.drop_column("stream_jobs", "recording_enabled")

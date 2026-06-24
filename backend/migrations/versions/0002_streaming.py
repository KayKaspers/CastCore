"""streaming schema: ffmpeg profiles, destinations, stream jobs, inputs, outputs, status

Revision ID: 0002_streaming
Revises: 0001_initial
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0002_streaming"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "ffmpeg_profiles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False, unique=True),
        sa.Column("global_opts", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("video", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("audio", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("filters", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("copy_mode", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("expert_args", sa.JSON(), nullable=False, server_default="[]"),
        *_ts(),
    )

    op.create_table(
        "destinations",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False, server_default="rtmp"),
        sa.Column("url", sa.String(1024), nullable=False),
        sa.Column("stream_key", sa.String(1024), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )

    op.create_table(
        "stream_jobs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("type", sa.String(16), nullable=False, server_default="single"),
        sa.Column("status", sa.String(16), nullable=False, server_default="stopped"),
        sa.Column("autostart", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("ffmpeg_profile_id", sa.Uuid(), sa.ForeignKey("ffmpeg_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("fallback_policy", sa.JSON(), nullable=False, server_default="{}"),
        *_ts(),
    )

    op.create_table(
        "inputs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False, server_default="file"),
        sa.Column("uri", sa.String(2048), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("loop", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("reconnect", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        *_ts(),
    )
    op.create_index("ix_inputs_job_id", "inputs", ["job_id"])

    op.create_table(
        "outputs",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("job_id", sa.Uuid(), sa.ForeignKey("stream_jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("destination_id", sa.Uuid(), sa.ForeignKey("destinations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("format", sa.String(16), nullable=False, server_default="flv"),
        sa.Column("output_opts", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )
    op.create_index("ix_outputs_job_id", "outputs", ["job_id"])

    op.create_table(
        "process_status",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("output_id", sa.Uuid(), sa.ForeignKey("outputs.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("pid", sa.Integer(), nullable=True),
        sa.Column("state", sa.String(16), nullable=False, server_default="stopped"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("bitrate_kbps", sa.Float(), nullable=True),
        sa.Column("speed", sa.Float(), nullable=True),
        sa.Column("dropped_frames", sa.Integer(), nullable=True),
        sa.Column("reconnect_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cpu_pct", sa.Float(), nullable=True),
        sa.Column("rss_mb", sa.Float(), nullable=True),
        *_ts(),
    )
    op.create_index("ix_process_status_output_id", "process_status", ["output_id"])


def downgrade() -> None:
    for table in ("process_status", "outputs", "inputs", "stream_jobs", "destinations", "ffmpeg_profiles"):
        op.drop_table(table)

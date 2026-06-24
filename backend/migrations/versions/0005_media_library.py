"""media library: items + probe data

Revision ID: 0005_media
Revises: 0004_backups
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005_media"
down_revision: Union[str, None] = "0004_backups"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "media_library_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("storage_source_id", sa.Uuid(), sa.ForeignKey("storage_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rel_path", sa.String(2048), nullable=False),
        sa.Column("filename", sa.String(512), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False, server_default="other"),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("mtime", sa.Float(), nullable=False, server_default="0"),
        sa.Column("streamable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("problem_flags", sa.JSON(), nullable=False, server_default="{}"),
        *_ts(),
    )
    op.create_index("ix_media_items_source", "media_library_items", ["storage_source_id"])
    op.create_index("ix_media_items_relpath", "media_library_items", ["storage_source_id", "rel_path"], unique=True)

    op.create_table(
        "media_probe_data",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("media_item_id", sa.Uuid(), sa.ForeignKey("media_library_items.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("container", sa.String(64), nullable=True),
        sa.Column("duration_s", sa.Float(), nullable=True),
        sa.Column("video_codec", sa.String(32), nullable=True),
        sa.Column("audio_codec", sa.String(32), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("fps", sa.Float(), nullable=True),
        sa.Column("video_bitrate", sa.BigInteger(), nullable=True),
        sa.Column("audio_bitrate", sa.BigInteger(), nullable=True),
        sa.Column("raw_ffprobe", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("probed_at", sa.DateTime(timezone=True), nullable=True),
        *_ts(),
    )


def downgrade() -> None:
    op.drop_table("media_probe_data")
    op.drop_table("media_library_items")

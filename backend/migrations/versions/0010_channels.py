"""linear channels

Revision ID: 0010_channels
Revises: 0009_playlists
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010_channels"
down_revision: Union[str, None] = "0009_playlists"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "channels",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("playlist_id", sa.Uuid(), sa.ForeignKey("playlists.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ffmpeg_profile_id", sa.Uuid(), sa.ForeignKey("ffmpeg_profiles.id", ondelete="SET NULL"), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("hls_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("epg_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(16), nullable=False, server_default="stopped"),
        sa.Column("output_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("channels")

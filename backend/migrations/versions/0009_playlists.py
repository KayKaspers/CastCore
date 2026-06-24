"""playlists + items

Revision ID: 0009_playlists
Revises: 0008_scheduler
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009_playlists"
down_revision: Union[str, None] = "0008_scheduler"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "playlists",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("mode", sa.String(16), nullable=False, server_default="sequential"),
        sa.Column("description", sa.String(512), nullable=True),
        *_ts(),
    )
    op.create_table(
        "playlist_items",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("playlist_id", sa.Uuid(), sa.ForeignKey("playlists.id", ondelete="CASCADE"), nullable=False),
        sa.Column("media_item_id", sa.Uuid(), sa.ForeignKey("media_library_items.id", ondelete="CASCADE"), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        *_ts(),
    )
    op.create_index("ix_playlist_items_playlist", "playlist_items", ["playlist_id"])


def downgrade() -> None:
    op.drop_table("playlist_items")
    op.drop_table("playlists")

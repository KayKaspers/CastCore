"""assets + platform_metadata thumbnail reference

Revision ID: 0013_assets
Revises: 0012_platmeta
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0013_assets"
down_revision: Union[str, None] = "0012_platmeta"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "assets",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("filename", sa.String(128), nullable=False),
        sa.Column("original_name", sa.String(512), nullable=True),
        sa.Column("path", sa.String(2048), nullable=False),
        sa.Column("kind", sa.String(16), nullable=False, server_default="image"),
        sa.Column("mime", sa.String(64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_assets_sha256", "assets", ["sha256"])
    op.add_column(
        "platform_metadata",
        sa.Column("thumbnail_asset_id", sa.Uuid(), sa.ForeignKey("assets.id", ondelete="SET NULL"), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("platform_metadata", "thumbnail_asset_id")
    op.drop_table("assets")

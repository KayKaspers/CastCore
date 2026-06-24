"""storage sources: local folders + SMB shares

Revision ID: 0003_storage
Revises: 0002_streaming
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003_storage"
down_revision: Union[str, None] = "0002_streaming"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "storage_sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("source_class", sa.String(16), nullable=False, server_default="local"),
        sa.Column("type", sa.String(16), nullable=False, server_default="folder"),
        sa.Column("path", sa.String(2048), nullable=True),
        sa.Column("read_only", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("automount", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(16), nullable=False, server_default="offline"),
        sa.Column("last_error", sa.String(512), nullable=True),
        sa.Column("last_scan_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("config", sa.JSON(), nullable=False, server_default="{}"),
        *_ts(),
    )

    op.create_table(
        "smb_sources",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("storage_source_id", sa.Uuid(), sa.ForeignKey("storage_sources.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("server", sa.String(255), nullable=False),
        sa.Column("share", sa.String(255), nullable=False),
        sa.Column("domain", sa.String(128), nullable=True),
        sa.Column("username", sa.String(128), nullable=True),
        sa.Column("password", sa.String(1024), nullable=True),
        sa.Column("smb_version", sa.String(8), nullable=True),
        sa.Column("mount_path", sa.String(2048), nullable=False),
        *_ts(),
    )


def downgrade() -> None:
    op.drop_table("smb_sources")
    op.drop_table("storage_sources")

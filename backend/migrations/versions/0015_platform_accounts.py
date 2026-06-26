"""Platform OAuth accounts

Revision ID: 0015_platform_accounts
Revises: 0014_totp
Create Date: 2026-06-25
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0015_platform_accounts"
down_revision: Union[str, None] = "0014_totp"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "platform_accounts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("provider", sa.String(length=24), nullable=False),
        sa.Column("account_name", sa.String(length=128), nullable=True),
        sa.Column("scope", sa.String(length=512), nullable=True),
        sa.Column("access_token", sa.Text(), nullable=False),
        sa.Column("refresh_token", sa.Text(), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_platform_accounts_provider", "platform_accounts", ["provider"])


def downgrade() -> None:
    op.drop_index("ix_platform_accounts_provider", table_name="platform_accounts")
    op.drop_table("platform_accounts")

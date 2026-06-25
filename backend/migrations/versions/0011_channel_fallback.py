"""channel fallback uri

Revision ID: 0011_chfallback
Revises: 0010_channels
Create Date: 2026-06-24
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0011_chfallback"
down_revision: Union[str, None] = "0010_channels"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("channels", sa.Column("fallback_uri", sa.String(2048), nullable=True))


def downgrade() -> None:
    op.drop_column("channels", "fallback_uri")

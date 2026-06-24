"""initial security & setup schema

Creates roles, users, user_roles, sessions, api_tokens, settings, setup_state,
audit_events and seeds the default roles (admin/operator/viewer).

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-24
"""

from __future__ import annotations

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _ts(table: str) -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    ]


def upgrade() -> None:
    op.create_table(
        "roles",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(32), nullable=False, unique=True),
        sa.Column("permissions", sa.JSON(), nullable=False, server_default="{}"),
        *_ts("roles"),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("language", sa.String(5), nullable=False, server_default="de"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("totp_secret", sa.String(255), nullable=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        *_ts("users"),
        sa.UniqueConstraint("username", name="uq_users_username"),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )
    op.create_index("ix_users_username", "users", ["username"])

    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", sa.Uuid(), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("refresh_token_hash", sa.String(255), nullable=False),
        sa.Column("user_agent", sa.String(255), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        *_ts("sessions"),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_refresh_token_hash", "sessions", ["refresh_token_hash"])

    op.create_table(
        "api_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(64), nullable=False),
        sa.Column("token_hash", sa.String(255), nullable=False),
        sa.Column("scopes", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        *_ts("api_tokens"),
    )
    op.create_index("ix_api_tokens_user_id", "api_tokens", ["user_id"])
    op.create_index("ix_api_tokens_token_hash", "api_tokens", ["token_hash"])

    op.create_table(
        "settings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("scope", sa.String(16), nullable=False, server_default="global"),
        sa.Column("user_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=True),
        *_ts("settings"),
        sa.UniqueConstraint("key", "user_id", name="uq_setting_key_user"),
    )
    op.create_index("ix_settings_key", "settings", ["key"])

    op.create_table(
        "setup_state",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("step", sa.String(32), nullable=False, unique=True),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("data", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        *_ts("setup_state"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("actor_id", sa.Uuid(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("target_type", sa.String(64), nullable=True),
        sa.Column("target_id", sa.String(64), nullable=True),
        sa.Column("ip", sa.String(64), nullable=True),
        sa.Column("meta", sa.JSON(), nullable=False, server_default="{}"),
        *_ts("audit_events"),
    )
    op.create_index("ix_audit_events_actor_id", "audit_events", ["actor_id"])
    op.create_index("ix_audit_events_action", "audit_events", ["action"])

    # Seed default roles.
    roles = sa.table(
        "roles",
        sa.column("id", sa.Uuid()),
        sa.column("name", sa.String()),
        sa.column("permissions", sa.JSON()),
    )
    op.bulk_insert(
        roles,
        [
            {"id": uuid.uuid4(), "name": "admin", "permissions": {"*": True}},
            {"id": uuid.uuid4(), "name": "operator", "permissions": {"streams": True, "sources": True, "platforms": True}},
            {"id": uuid.uuid4(), "name": "viewer", "permissions": {"read": True}},
        ],
    )


def downgrade() -> None:
    for table in (
        "audit_events", "setup_state", "settings", "api_tokens",
        "sessions", "user_roles", "users", "roles",
    ):
        op.drop_table(table)

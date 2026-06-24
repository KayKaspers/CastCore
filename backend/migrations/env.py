"""Alembic environment.

Uses the application settings for the DB URL. ``target_metadata`` will point at the
SQLAlchemy ``Base.metadata`` once the ORM models land (Phase 1); until then there are
no migrations and ``alembic upgrade head`` is a no-op.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Sync URL for Alembic (strip the asyncpg driver).
config.set_main_option(
    "sqlalchemy.url",
    get_settings().database_url.replace("+asyncpg", ""),
)

# TODO(Phase 1): from app.models import Base; target_metadata = Base.metadata
target_metadata = None


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

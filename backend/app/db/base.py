"""SQLAlchemy declarative base and shared column mixins.

All ORM models inherit from ``Base``. Importing ``app.models`` (which imports every
model module) populates ``Base.metadata`` for Alembic autogeneration and migrations.
"""

from __future__ import annotations

import datetime as dt
import uuid

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(primary_key=True, default=uuid.uuid4)


class TimestampMixin:
    created_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

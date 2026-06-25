"""Update / version info — reports the running version, deployment mode and the database
migration status (is the schema at the latest revision?).

CastCore does not self-update: updates are performed via Docker images or the native
update script. This service is purely informational (shown on the Updates page).
"""

from __future__ import annotations

import os

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import __version__
from app.core.config import get_settings


def _head_revision() -> str | None:
    try:
        cfg = Config("alembic.ini")
        return ScriptDirectory.from_config(cfg).get_current_head()
    except Exception:  # noqa: BLE001 - defensive: missing alembic config
        return None


async def get_state(db: AsyncSession) -> dict:
    settings = get_settings()
    try:
        row = (await db.execute(text("SELECT version_num FROM alembic_version"))).first()
        db_rev = row[0] if row else None
    except Exception:  # noqa: BLE001 - table may not exist yet
        db_rev = None
    head = _head_revision()
    return {
        "current_version": __version__,
        "environment": settings.castcore_env,
        "deployment": "docker" if os.path.exists("/.dockerenv") else "native",
        "db_revision": db_rev,
        "head_revision": head,
        "up_to_date": db_rev is not None and head is not None and db_rev == head,
    }

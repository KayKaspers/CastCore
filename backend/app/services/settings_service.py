"""Global (instance-wide) settings stored in the `settings` table (scope=global).

Per-user settings (e.g. preferred language) live on the User model and are updated via
the profile endpoints.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.settings import Setting

# Known global keys (others are ignored on write to keep the surface predictable).
GLOBAL_KEYS = {"instance_name", "default_language"}


async def get_global(db: AsyncSession) -> dict[str, Any]:
    res = await db.execute(select(Setting).where(Setting.scope == "global"))
    return {s.key: (s.value or {}).get("value") for s in res.scalars().all()}


async def set_global(db: AsyncSession, key: str, value: Any) -> None:
    if key not in GLOBAL_KEYS:
        return
    res = await db.execute(
        select(Setting).where(Setting.scope == "global", Setting.key == key)
    )
    setting = res.scalar_one_or_none()
    if setting is None:
        setting = Setting(key=key, value={"value": value}, scope="global")
        db.add(setting)
    else:
        setting.value = {"value": value}
    await db.flush()

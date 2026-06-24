"""Backup / restore — self-contained logical dump of all tables to gzipped JSON.

Why logical (not pg_dump): no client/server version coupling, identical behaviour in
Docker and native installs, and the artifact is portable. Secrets stay **encrypted**
in the dump (they are stored encrypted), so a backup is useless without the matching
``ENCRYPTION_KEY`` — keep that key safe and separate.

Restore wipes and re-inserts all application tables (in FK order) within one
transaction. The ``backups`` table itself is excluded so history survives a restore.
"""

from __future__ import annotations

import datetime as dt
import gzip
import json
import uuid
from pathlib import Path

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import Base
from app.models.backup import Backup

FORMAT_VERSION = 1
_EXCLUDE = {"backups", "alembic_version"}


def _tables() -> list[sa.Table]:
    return [t for t in Base.metadata.sorted_tables if t.name not in _EXCLUDE]


def _encode(value):  # JSON default for non-native types
    if isinstance(value, uuid.UUID):
        return str(value)
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    raise TypeError(f"unserializable: {type(value)}")


def _decode_row(table: sa.Table, row: dict) -> dict:
    out: dict = {}
    for col in table.columns:
        if col.name not in row:
            continue
        val = row[col.name]
        if val is not None:
            if isinstance(col.type, sa.Uuid):
                val = uuid.UUID(val)
            elif isinstance(col.type, sa.DateTime):
                val = dt.datetime.fromisoformat(val)
        out[col.name] = val
    return out


async def create_backup(db: AsyncSession, *, kind: str = "manual") -> Backup:
    settings = get_settings()
    backup_dir = Path(settings.backup_dir)
    backup_dir.mkdir(parents=True, exist_ok=True)

    data: dict[str, list[dict]] = {}
    for table in _tables():
        res = await db.execute(table.select())
        data[table.name] = [dict(m) for m in res.mappings().all()]

    payload = {
        "meta": {
            "format_version": FORMAT_VERSION,
            "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "tables": list(data.keys()),
        },
        "data": data,
    }

    ts = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d-%H%M%S")
    filename = f"castcore-{ts}.json.gz"
    path = backup_dir / filename
    raw = json.dumps(payload, default=_encode).encode("utf-8")
    with gzip.open(path, "wb") as fh:
        fh.write(raw)

    backup = Backup(
        filename=filename,
        path=str(path),
        kind=kind,
        size_bytes=path.stat().st_size,
        includes={"tables": list(data.keys())},
        status="completed",
    )
    db.add(backup)
    await db.flush()
    return backup


async def restore_backup(db: AsyncSession, backup: Backup) -> dict:
    path = Path(backup.path)
    if not path.exists():
        raise FileNotFoundError("backup file missing")

    with gzip.open(path, "rt", encoding="utf-8") as fh:
        payload = json.load(fh)
    data = payload.get("data", {})

    tables = _tables()
    # Wipe in reverse dependency order, then repopulate in dependency order.
    for table in reversed(tables):
        await db.execute(table.delete())
    counts: dict[str, int] = {}
    for table in tables:
        rows = data.get(table.name, [])
        if rows:
            await db.execute(table.insert(), [_decode_row(table, r) for r in rows])
        counts[table.name] = len(rows)
    return counts

---
title: "Migrations"
description: "Create and apply Alembic migrations."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Migrations

> Schema changes go through **Alembic** (`backend/migrations/`).

**Audience:** developers.

## Applying

In Docker, **automatic** on backend start. Manually:

```bash
docker compose exec backend alembic upgrade head
```

## Creating a new migration

1. Change a model in `app/models/` and register it in `app/models/__init__.py`.
2. Generate (autogenerate) or hand-write:
   ```bash
   docker compose exec backend alembic revision -m "description" --autogenerate
   ```
3. Review/adjust the file in `backend/migrations/versions/` (UUID columns, defaults,
   indexes) and chain `down_revision` correctly.

## Conventions

- File/revision numbered sequentially (e.g. `0014_…`).
- `sa.Uuid()` for UUID PKs/FKs, `sa.JSON()` for JSON columns.
- Set server defaults for bool/JSON (`server_default`) so existing rows fit.

## Checking status

Current vs. latest revision: **Updates** page (`/api/v1/update/state`).

## Related pages

- [Database](/docs/en/developer-guide/database.md) · [Updates](/docs/en/user-guide/updates.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

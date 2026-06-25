---
title: "Backend"
description: "FastAPI backend: structure, services, dependencies."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Backend

> FastAPI + SQLAlchemy 2 (async) + Pydantic v2.

**Audience:** developers.

## Structure

- **`app/main.py`** – app + lifespan (starts the status consumer & scheduler loop).
- **`app/api/v1/router.py`** – aggregates all endpoint routers under `/api/v1`.
- **`app/api/deps.py`** – `get_db`, `get_current_user`, `require_roles(...)`.
- **`app/core/`** – `config` (env), `security` (argon2/JWT/Fernet/masking), `redis`,
  `errors` (translatable codes).
- **`app/services/`** – business logic (e.g. `stream_service`, `channel_service`,
  `ffmpeg/command_builder`, `metadata_service`, `notification_service`).

## Patterns

- Endpoints are thin; logic lives in `services/`.
- DB session via dependency (`DbDep`), commit at request end.
- Role checks via `dependencies=[Depends(require_roles("operator"))]`.
- Errors via `CastCoreError(code, …)` → uniform `{detail:{error:{code,…}}}`.

## Background loops

The **lifespan** runs two tasks: `status_consumer` (PM→DB reconcile + events +
self-healing) and `scheduler` (due entries every ~20 s).

## Local dev

See [Local dev](https://github.com/KayKaspers/CastCore/blob/main/docs/LOCAL_DEV.md).
Tests/linting: [Testing](/docs/en/developer-guide/testing.md).

## Related pages

- [Database](/docs/en/developer-guide/database.md) · [API](/docs/en/api/overview.md)
- [Process manager](/docs/en/developer-guide/process-manager.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

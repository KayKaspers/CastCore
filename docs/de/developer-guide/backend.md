---
title: "Backend"
description: "FastAPI-Backend: Aufbau, Services, Dependencies."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Backend

> FastAPI + SQLAlchemy 2 (async) + Pydantic v2.

**Zielgruppe:** Entwickler.

## Aufbau

- **`app/main.py`** – App + Lifespan (startet Status-Consumer & Scheduler-Loop).
- **`app/api/v1/router.py`** – aggregiert alle Endpoint-Router unter `/api/v1`.
- **`app/api/deps.py`** – `get_db`, `get_current_user`, `require_roles(...)`.
- **`app/core/`** – `config` (Env), `security` (argon2/JWT/Fernet/Masking),
  `redis`, `errors` (übersetzbare Codes).
- **`app/services/`** – Geschäftslogik (z. B. `stream_service`, `channel_service`,
  `ffmpeg/command_builder`, `metadata_service`, `notification_service`).

## Muster

- Endpunkte sind dünn; Logik liegt in `services/`.
- DB-Session per Dependency (`DbDep`), Commit am Request-Ende.
- Rollenprüfung über `dependencies=[Depends(require_roles("operator"))]`.
- Fehler über `CastCoreError(code, …)` → einheitliches `{detail:{error:{code,…}}}`.

## Hintergrund-Loops

In der **Lifespan** laufen zwei Tasks: `status_consumer` (PM→DB-Abgleich + Events +
Selbstheilung) und `scheduler` (fällige Einträge alle ~20 s).

## Lokal entwickeln

Siehe [Lokales Testen](https://github.com/KayKaspers/CastCore/blob/main/docs/LOCAL_DEV.md).
Tests/Linting: [Tests](/docs/de/developer-guide/testing.md).

## Verwandte Seiten

- [Datenbank](/docs/de/developer-guide/database.md) · [API](/docs/de/api/overview.md)
- [Process Manager](/docs/de/developer-guide/process-manager.md)

---
_Stand: 2026-06-24 · Status: Stabil_

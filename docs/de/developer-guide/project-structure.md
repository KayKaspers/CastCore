---
title: "Projektstruktur"
description: "Verzeichnislayout des Monorepos."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# Projektstruktur

> Layout des Monorepos.

**Zielgruppe:** Entwickler.

```text
CastCore/
├── backend/            FastAPI-App
│   ├── app/
│   │   ├── api/v1/endpoints/   API-Router je Modul
│   │   ├── core/               config, security, redis, errors
│   │   ├── db/                  Base, Session
│   │   ├── models/             SQLAlchemy-Modelle
│   │   ├── schemas/            Pydantic-Schemas
│   │   └── services/           Geschäftslogik (ffmpeg, stream, channel, …)
│   ├── migrations/             Alembic
│   └── tests/
├── process_manager/    FFmpeg-Supervisor (asyncio)
├── worker/             arq-Worker
├── frontend/           React/Vite
│   └── src/{pages,components,lib,i18n,styles}
├── deploy/             caddy, nginx, systemd, mediamtx
├── scripts/            install/update/uninstall, check_docs.py
├── docs/               Doku (de/en) + Manifest/Status/Nav
└── docker-compose.yml
```

## Konventionen

- Backend: ein Service pro Modul unter `services/`, API-Router unter `api/v1/endpoints/`.
- Frontend: eine Seite pro Route unter `pages/`, geteilte Logik in `lib/`.
- Doku: jede Seite in **beiden** Sprachen (`docs/de`, `docs/en`).

## Verwandte Seiten

- [Backend](/docs/de/developer-guide/backend.md) · [Frontend](/docs/de/developer-guide/frontend.md)
- [Mitwirken](/docs/de/developer-guide/contributing.md)

---
_Stand: 2026-06-24 · Status: Stabil_

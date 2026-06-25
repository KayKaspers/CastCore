---
title: "Project structure"
description: "Directory layout of the monorepo."
lang: en
audience: "Developers"
status: stable
lastReviewed: 2026-06-24
---

# Project structure

> Monorepo layout.

**Audience:** developers.

```text
CastCore/
├── backend/            FastAPI app
│   ├── app/
│   │   ├── api/v1/endpoints/   API routers per module
│   │   ├── core/               config, security, redis, errors
│   │   ├── db/                  Base, Session
│   │   ├── models/             SQLAlchemy models
│   │   ├── schemas/            Pydantic schemas
│   │   └── services/           business logic (ffmpeg, stream, channel, …)
│   ├── migrations/             Alembic
│   └── tests/
├── process_manager/    FFmpeg supervisor (asyncio)
├── worker/             arq worker
├── frontend/           React/Vite
│   └── src/{pages,components,lib,i18n,styles}
├── deploy/             caddy, nginx, systemd, mediamtx
├── scripts/            install/update/uninstall, check_docs.py
├── docs/               docs (de/en) + manifest/status/nav
└── docker-compose.yml
```

## Conventions

- Backend: one service per module under `services/`, API routers under `api/v1/endpoints/`.
- Frontend: one page per route under `pages/`, shared logic in `lib/`.
- Docs: every page in **both** languages (`docs/de`, `docs/en`).

## Related pages

- [Backend](/docs/en/developer-guide/backend.md) · [Frontend](/docs/en/developer-guide/frontend.md)
- [Contributing](/docs/en/developer-guide/contributing.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

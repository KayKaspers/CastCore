---
title: "API overview"
description: "Base URL, auth, error format, OpenAPI/Swagger."
lang: en
audience: "Developers / Integrators"
status: stable
lastReviewed: 2026-06-24
---

# API overview

> CastCore offers a REST API (JSON) plus WebSockets for live logs/status. Base: `/api/v1`.

**Audience:** developers / integrators.

## Authentication

- `POST /api/v1/auth/login` returns **access** and **refresh** tokens.
- Send requests with `Authorization: Bearer <access_token>`.
- Automation: API tokens via `X-API-Key` (see [Auth](/docs/en/api/auth.md)).

## Error format

Errors return **translatable codes** instead of fixed text:

```json
{ "detail": { "error": { "code": "preflight.source_unreachable",
                          "params": { "source": "Studio NAS" }, "level": "error" } } }
```

The frontend localizes `code` via i18n (`error.*`).

## Roles

Each route requires a role (Admin/Operator/Viewer). Admin always passes. See
[Roles](/docs/en/reference/roles.md).

## OpenAPI / Swagger

- Interactive docs: **`/api/docs`** (Swagger UI)
- Schema: **`/api/openapi.json`**

## Live (WebSocket)

| Channel | Purpose |
| --- | --- |
| `WS /api/v1/ws/logs/{job_id}` | live FFmpeg logs + hints |
| `WS /api/v1/ws/status` | status/metric updates |

The token is passed as the `?token=` query parameter.

## Sections

- [Auth](/docs/en/api/auth.md) · [Streams](/docs/en/api/streams.md) ·
  [Sources](/docs/en/api/sources.md) · [Platforms & metadata](/docs/en/api/platforms.md)
- [Media library](/docs/en/api/media-library.md) · [Monitoring](/docs/en/api/monitoring.md)
  · [Backup/restore](/docs/en/api/backup-restore.md)

---
_Last reviewed: 2026-06-24 · Status: stable_

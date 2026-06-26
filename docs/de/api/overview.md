---
title: "API-Überblick"
description: "Basis-URL, Auth, Fehlerformat, OpenAPI/Swagger."
lang: de
audience: "Entwickler / Integratoren"
status: stable
lastReviewed: 2026-06-26
---

# API-Überblick

> CastCore bietet eine REST-API (JSON) plus WebSockets für Live-Logs/Status. Basis:
> `/api/v1`.

**Zielgruppe:** Entwickler / Integratoren.

## Authentifizierung

- `POST /api/v1/auth/login` liefert **Access-** und **Refresh-Token**.
- Anfragen mit `Authorization: Bearer <access_token>`.
- Automatisierung: persönliche API-Tokens via `Authorization: Bearer cc_…` (siehe [Auth](/docs/de/api/auth.md)).

## Fehlerformat

Fehler liefern **übersetzbare Codes** statt fester Texte:

```json
{ "detail": { "error": { "code": "preflight.source_unreachable",
                          "params": { "source": "Studio NAS" }, "level": "error" } } }
```

Das Frontend übersetzt `code` via i18n (`error.*`).

## Rollen

Jede Route verlangt eine Rolle (Admin/Operator/Viewer). Admin darf immer.
Siehe [Rollen](/docs/de/reference/roles.md).

## OpenAPI / Swagger

- Interaktive Doku: **`/api/docs`** (Swagger UI)
- Schema: **`/api/openapi.json`**

## Live (WebSocket)

| Kanal | Zweck |
| --- | --- |
| `WS /api/v1/ws/logs/{job_id}` | Live-FFmpeg-Logs + Hinweise |
| `WS /api/v1/ws/status` | Status-/Metrik-Updates |

Token wird als Query-Parameter `?token=` übergeben.

## Bereiche

- [Auth](/docs/de/api/auth.md) · [Streams](/docs/de/api/streams.md) ·
  [Quellen](/docs/de/api/sources.md) · [Plattformen & Metadaten](/docs/de/api/platforms.md)
- [Medienbibliothek](/docs/de/api/media-library.md) · [Monitoring](/docs/de/api/monitoring.md)
  · [Backup/Restore](/docs/de/api/backup-restore.md)

---
_Stand: 2026-06-26 · Status: Stabil_

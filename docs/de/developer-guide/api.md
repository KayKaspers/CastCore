---
title: "API (Entwickler)"
description: "REST/WS-API-Aufbau, OpenAPI, typed client."
lang: de
audience: "Entwickler"
status: stable
lastReviewed: 2026-06-24
---

# API (Entwickler)

> Wie die API intern aufgebaut ist. Endpunkt-Referenz: [API-Überblick](/docs/de/api/overview.md).

**Zielgruppe:** Entwickler.

## Aufbau

- Versioniert unter `/api/v1` (`app/api/v1/router.py` bündelt die Endpoint-Router).
- Ein Router pro Modul in `app/api/v1/endpoints/`.
- Schemas (Pydantic v2) in `app/schemas/`, Logik in `app/services/`.

## Auth & Rollen

- Dependency `get_current_user` (Bearer-JWT) und Factory `require_roles("operator")`.
- Rollen werden **serverseitig** pro Route erzwungen.

## Fehler

`CastCoreError(code, params=…, http_status=…)` erzeugt
`{detail:{error:{code, params, level}}}` mit **übersetzbarem Code** (kein fester Text).

## OpenAPI

FastAPI generiert `/api/openapi.json` und Swagger UI unter `/api/docs`. Daraus lässt sich
ein **typed Client** fürs Frontend generieren.

## Live

WebSockets unter `/api/v1/ws/...` (Token via Query) – siehe
[WebSockets / SSE](/docs/de/developer-guide/websocket-sse.md).

## Verwandte Seiten

- [Backend](/docs/de/developer-guide/backend.md) · [API-Überblick](/docs/de/api/overview.md)

---
_Stand: 2026-06-24 · Status: Stabil_
